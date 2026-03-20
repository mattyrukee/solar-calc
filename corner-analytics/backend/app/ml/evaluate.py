"""
Backtesting and evaluation script.

Simulates how the model would have performed on a held-out season:
  - Loads the trained models
  - For each finished match in the test period, builds features using
    only data that was available BEFORE that match (no leakage)
  - Computes MAE, RMSE, and CI coverage
  - Prints a per-league breakdown

Usage:
    python -m app.ml.evaluate --season 2023
"""
import argparse
import json
import logging
import os
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error

from app.database import SessionLocal
from app.models.db_models import Match, MatchStatus
from app.services.feature_engine import build_features

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

MODEL_DIR = Path(os.getenv("MODEL_DIR", "app/ml/models"))
MODEL_VERSION = "v1"


def load_models():
    point = joblib.load(MODEL_DIR / f"point_{MODEL_VERSION}.pkl")
    low = joblib.load(MODEL_DIR / f"low_{MODEL_VERSION}.pkl")
    high = joblib.load(MODEL_DIR / f"high_{MODEL_VERSION}.pkl")
    with open(MODEL_DIR / "feature_names.json") as f:
        feature_names = json.load(f)
    return point, low, high, feature_names


def backtest(season: int) -> dict:
    db = SessionLocal()
    try:
        point_model, low_model, high_model, feature_names = load_models()

        # Fetch finished matches for the target season
        matches = (
            db.query(Match)
            .filter(
                Match.status == MatchStatus.finished,
                Match.season == season,
                Match.total_corners.isnot(None),
            )
            .order_by(Match.fixture_date)
            .all()
        )

        log.info("Backtesting on %d matches from season %d", len(matches), season)

        results = []
        skipped = 0

        for match in matches:
            features = build_features(db, match, cutoff_date=match.fixture_date)
            if features is None:
                skipped += 1
                continue

            row = pd.DataFrame([features.to_dict()])[feature_names]
            pred = float(point_model.predict(row)[0])
            pred_low = float(low_model.predict(row)[0])
            pred_high = float(high_model.predict(row)[0])
            actual = match.total_corners

            results.append({
                "match_id": match.id,
                "league_id": match.league_id,
                "fixture_date": match.fixture_date,
                "actual": actual,
                "predicted": pred,
                "low_bound": max(0, round(pred_low)),
                "high_bound": round(pred_high),
                "in_ci": pred_low <= actual <= pred_high,
                "error": abs(pred - actual),
            })

        if not results:
            log.warning("No results — check that the season has finished matches with corner data.")
            return {}

        df = pd.DataFrame(results)

        # Overall metrics
        mae = mean_absolute_error(df["actual"], df["predicted"])
        rmse = float(np.sqrt(mean_squared_error(df["actual"], df["predicted"])))
        ci_coverage = float(df["in_ci"].mean())
        avg_ci_width = float((df["high_bound"] - df["low_bound"]).mean())

        # Per-league breakdown
        league_metrics = {}
        for league_id, group in df.groupby("league_id"):
            league_metrics[str(league_id)] = {
                "mae": round(mean_absolute_error(group["actual"], group["predicted"]), 3),
                "rmse": round(float(np.sqrt(mean_squared_error(group["actual"], group["predicted"]))), 3),
                "ci_coverage": round(float(group["in_ci"].mean()), 3),
                "n_matches": len(group),
            }

        metrics = {
            "season": season,
            "n_matches": len(df),
            "n_skipped": skipped,
            "mae": round(mae, 3),
            "rmse": round(rmse, 3),
            "ci_coverage_pct": round(ci_coverage * 100, 1),
            "avg_ci_width": round(avg_ci_width, 1),
            "by_league": league_metrics,
        }

        _print_report(metrics)
        return metrics

    finally:
        db.close()


def _print_report(m: dict):
    print("\n" + "=" * 55)
    print(f"  Backtest Results — Season {m['season']}")
    print("=" * 55)
    print(f"  Matches evaluated : {m['n_matches']} ({m['n_skipped']} skipped)")
    print(f"  MAE               : {m['mae']} corners")
    print(f"  RMSE              : {m['rmse']} corners")
    print(f"  90% CI coverage   : {m['ci_coverage_pct']}%  (target ≥ 90%)")
    print(f"  Avg CI width      : {m['avg_ci_width']} corners")
    print()
    print("  Per-league breakdown:")
    for league_id, lm in m.get("by_league", {}).items():
        print(
            f"    League {league_id:>4} — MAE: {lm['mae']:.2f} | "
            f"RMSE: {lm['rmse']:.2f} | "
            f"CI: {lm['ci_coverage']*100:.0f}% | "
            f"n={lm['n_matches']}"
        )
    print("=" * 55 + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Backtest corner prediction model")
    parser.add_argument("--season", type=int, default=2023, help="Season to backtest on")
    args = parser.parse_args()
    backtest(args.season)
