"""
ML training pipeline for corner kick prediction.

Models trained:
  1. XGBoost Regressor — predicts the expected total corners (point estimate)
  2. XGBoost Quantile (5th percentile)  — lower bound of 90% CI
  3. XGBoost Quantile (95th percentile) — upper bound of 90% CI

Validation strategy: Walk-forward time-series split (no data leakage).

Usage:
    python -m app.ml.train
"""
import json
import logging
import os
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import mean_absolute_error, mean_squared_error
from xgboost import XGBRegressor

from app.database import SessionLocal
from app.services.feature_engine import build_training_dataset

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

MODEL_DIR = Path(os.getenv("MODEL_DIR", "app/ml/models"))
MODEL_VERSION = "v1"

# ------------------------------------------------------------------ #
# XGBoost hyper-parameters                                           #
# ------------------------------------------------------------------ #

BASE_PARAMS = dict(
    n_estimators=400,
    learning_rate=0.05,
    max_depth=4,
    subsample=0.8,
    colsample_bytree=0.8,
    min_child_weight=5,
    random_state=42,
    n_jobs=-1,
    early_stopping_rounds=30,
    eval_metric="mae",
)


def _xgb_regressor(**extra) -> XGBRegressor:
    return XGBRegressor(**{**BASE_PARAMS, **extra})


# ------------------------------------------------------------------ #
# Training                                                            #
# ------------------------------------------------------------------ #

def train(db=None) -> dict[str, Any]:
    """
    Train all three models and save them to MODEL_DIR.

    Returns a metrics dict with MAE, RMSE, and CI coverage on the
    walk-forward validation folds.
    """
    close_db = db is None
    if db is None:
        db = SessionLocal()

    try:
        log.info("Building training dataset from DB...")
        X_dicts, y = build_training_dataset(db)
    finally:
        if close_db:
            db.close()

    if len(X_dicts) < 50:
        raise RuntimeError(
            f"Only {len(X_dicts)} training samples — need at least 50. "
            "Run the StatsBomb ingestion first: POST /api/admin/ingest-statsbomb"
        )

    X = pd.DataFrame(X_dicts)
    y = np.array(y)
    feature_names = list(X.columns)

    log.info("Dataset: %d samples, %d features", len(y), len(feature_names))

    # ---- Walk-forward cross-validation ---------------------------------- #
    tscv = TimeSeriesSplit(n_splits=5)
    fold_maes, fold_rmses, fold_coverages = [], [], []

    for fold, (train_idx, val_idx) in enumerate(tscv.split(X), 1):
        X_tr, X_val = X.iloc[train_idx], X.iloc[val_idx]
        y_tr, y_val = y[train_idx], y[val_idx]

        # Point estimate model
        model_p = _xgb_regressor()
        model_p.fit(
            X_tr, y_tr,
            eval_set=[(X_val, y_val)],
            verbose=False,
        )

        # Quantile models for CI
        model_low = _xgb_regressor(objective="reg:quantileerror", quantile_alpha=0.05)
        model_high = _xgb_regressor(objective="reg:quantileerror", quantile_alpha=0.95)

        # Quantile models don't use early stopping the same way
        model_low_simple = XGBRegressor(
            **{k: v for k, v in {**BASE_PARAMS, "objective": "reg:quantileerror",
                                  "quantile_alpha": 0.05}.items()
               if k != "early_stopping_rounds"},
        )
        model_high_simple = XGBRegressor(
            **{k: v for k, v in {**BASE_PARAMS, "objective": "reg:quantileerror",
                                  "quantile_alpha": 0.95}.items()
               if k != "early_stopping_rounds"},
        )
        model_low_simple.fit(X_tr, y_tr, verbose=False)
        model_high_simple.fit(X_tr, y_tr, verbose=False)

        preds = model_p.predict(X_val)
        low_preds = model_low_simple.predict(X_val)
        high_preds = model_high_simple.predict(X_val)

        mae = mean_absolute_error(y_val, preds)
        rmse = float(np.sqrt(mean_squared_error(y_val, preds)))
        coverage = float(np.mean((y_val >= low_preds) & (y_val <= high_preds)))

        fold_maes.append(mae)
        fold_rmses.append(rmse)
        fold_coverages.append(coverage)
        log.info(
            "Fold %d — MAE: %.2f  RMSE: %.2f  CI coverage: %.1f%%",
            fold, mae, rmse, coverage * 100,
        )

    metrics = {
        "mae_mean": float(np.mean(fold_maes)),
        "mae_std": float(np.std(fold_maes)),
        "rmse_mean": float(np.mean(fold_rmses)),
        "ci_coverage_mean": float(np.mean(fold_coverages)),
        "n_samples": len(y),
        "n_features": len(feature_names),
        "model_version": MODEL_VERSION,
    }
    log.info(
        "Cross-validation results — MAE: %.2f ± %.2f | RMSE: %.2f | CI coverage: %.1f%%",
        metrics["mae_mean"], metrics["mae_std"],
        metrics["rmse_mean"], metrics["ci_coverage_mean"] * 100,
    )

    # ---- Final models trained on ALL data ------------------------------- #
    log.info("Training final models on full dataset...")

    final_point = _xgb_regressor()
    # For final model, use last 20% as eval set (no early stopping risk)
    split = int(len(X) * 0.8)
    final_point.fit(
        X.iloc[:split], y[:split],
        eval_set=[(X.iloc[split:], y[split:])],
        verbose=False,
    )

    final_low = XGBRegressor(
        **{k: v for k, v in {**BASE_PARAMS, "objective": "reg:quantileerror",
                              "quantile_alpha": 0.05}.items()
           if k != "early_stopping_rounds"},
    )
    final_high = XGBRegressor(
        **{k: v for k, v in {**BASE_PARAMS, "objective": "reg:quantileerror",
                              "quantile_alpha": 0.95}.items()
           if k != "early_stopping_rounds"},
    )
    final_low.fit(X, y, verbose=False)
    final_high.fit(X, y, verbose=False)

    # ---- Save models ---------------------------------------------------- #
    MODEL_DIR.mkdir(parents=True, exist_ok=True)

    joblib.dump(final_point, MODEL_DIR / f"point_{MODEL_VERSION}.pkl")
    joblib.dump(final_low, MODEL_DIR / f"low_{MODEL_VERSION}.pkl")
    joblib.dump(final_high, MODEL_DIR / f"high_{MODEL_VERSION}.pkl")

    # Save feature names for inference-time validation
    with open(MODEL_DIR / "feature_names.json", "w") as f:
        json.dump(feature_names, f)

    # Save metrics
    with open(MODEL_DIR / "metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)

    log.info("Models saved to %s", MODEL_DIR)
    return metrics


if __name__ == "__main__":
    results = train()
    print("\n=== Training complete ===")
    for k, v in results.items():
        print(f"  {k}: {v:.4f}" if isinstance(v, float) else f"  {k}: {v}")
