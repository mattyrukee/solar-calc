"""
Corner prediction inference service.

Loads the trained XGBoost models and generates predictions for upcoming fixtures.
Models are loaded once at module level (lazy) and cached in memory.
"""
from __future__ import annotations

import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

import joblib
import numpy as np
import pandas as pd
from sqlalchemy.orm import Session

from app.models.db_models import Match, MatchStatus, Prediction
from app.services.feature_engine import build_features

log = logging.getLogger(__name__)

MODEL_DIR = Path(os.getenv("MODEL_DIR", "app/ml/models"))
MODEL_VERSION = "v1"

# ---- Lazy model cache ---------------------------------------------------- #
_point_model = None
_low_model = None
_high_model = None
_feature_names: list[str] | None = None
_models_loaded = False


def _load_models() -> bool:
    """Load models from disk into module-level cache. Returns True if successful."""
    global _point_model, _low_model, _high_model, _feature_names, _models_loaded

    point_path = MODEL_DIR / f"point_{MODEL_VERSION}.pkl"
    low_path = MODEL_DIR / f"low_{MODEL_VERSION}.pkl"
    high_path = MODEL_DIR / f"high_{MODEL_VERSION}.pkl"
    feat_path = MODEL_DIR / "feature_names.json"

    if not all(p.exists() for p in [point_path, low_path, high_path, feat_path]):
        log.warning(
            "Trained models not found in %s. "
            "Run: python -m app.ml.train  to train first.",
            MODEL_DIR,
        )
        return False

    _point_model = joblib.load(point_path)
    _low_model = joblib.load(low_path)
    _high_model = joblib.load(high_path)
    with open(feat_path) as f:
        _feature_names = json.load(f)

    _models_loaded = True
    log.info("Prediction models loaded from %s (version=%s)", MODEL_DIR, MODEL_VERSION)
    return True


def _ensure_models() -> bool:
    if not _models_loaded:
        return _load_models()
    return True


# --------------------------------------------------------------------------- #
# Single-fixture prediction                                                   #
# --------------------------------------------------------------------------- #

def predict_match(db: Session, match: Match) -> Optional[Prediction]:
    """
    Generate (or refresh) a corner prediction for a single upcoming fixture.

    Returns the Prediction ORM object (not yet committed to DB).
    Returns None if the model is not trained or features cannot be built.
    """
    if not _ensure_models():
        return None

    features = build_features(db, match)
    if features is None:
        log.debug("Cannot build features for fixture %d — skipping", match.id)
        return None

    row = pd.DataFrame([features.to_dict()])[_feature_names]

    predicted_total = float(_point_model.predict(row)[0])
    low_raw = float(_low_model.predict(row)[0])
    high_raw = float(_high_model.predict(row)[0])

    # Ensure low <= predicted <= high and no negatives
    low_bound = max(0, round(min(low_raw, predicted_total)))
    high_bound = max(round(max(high_raw, predicted_total)), low_bound + 1)

    # Confidence score: inverse of relative CI width, capped at 0.99
    ci_width = high_bound - low_bound
    raw_confidence = 1.0 - (ci_width / max(predicted_total, 1.0)) * 0.3
    confidence_score = round(float(np.clip(raw_confidence, 0.50, 0.99)), 4)

    prediction = (
        db.query(Prediction).filter(Prediction.match_id == match.id).first()
    )
    if prediction is None:
        prediction = Prediction(match_id=match.id)
        db.add(prediction)

    prediction.predicted_total = round(predicted_total, 2)
    prediction.low_bound = low_bound
    prediction.high_bound = high_bound
    prediction.confidence_score = confidence_score
    prediction.model_version = MODEL_VERSION
    prediction.generated_at = datetime.utcnow()

    # Store key features for explainability on the frontend
    prediction.home_avg_corners_for = round(features.home_avg_corners_for_h, 2)
    prediction.away_avg_corners_for = round(features.away_avg_corners_for_a, 2)
    prediction.home_avg_corners_against = round(features.home_avg_corners_against_h, 2)
    prediction.away_avg_corners_against = round(features.away_avg_corners_against_a, 2)
    prediction.h2h_avg_corners = round(features.h2h_avg_total_corners, 2)
    prediction.home_press_intensity = features.home_avg_possession
    prediction.away_press_intensity = features.away_avg_possession
    prediction.league_avg_corners = features.league_avg_corners

    return prediction


# --------------------------------------------------------------------------- #
# Batch prediction for all upcoming fixtures                                  #
# --------------------------------------------------------------------------- #

def generate_predictions_for_upcoming(db: Session) -> int:
    """
    Generate / refresh predictions for all upcoming scheduled fixtures.

    Returns the number of predictions successfully generated.
    """
    if not _ensure_models():
        log.info("Skipping prediction run — models not trained yet.")
        return 0

    upcoming = (
        db.query(Match)
        .filter(Match.status == MatchStatus.scheduled)
        .order_by(Match.fixture_date)
        .all()
    )

    log.info("Generating predictions for %d upcoming fixtures...", len(upcoming))
    generated = 0

    for match in upcoming:
        try:
            result = predict_match(db, match)
            if result is not None:
                generated += 1
        except Exception as exc:
            log.error("Prediction failed for fixture %d: %s", match.id, exc)

    db.commit()
    log.info("Predictions generated: %d / %d", generated, len(upcoming))
    return generated


# --------------------------------------------------------------------------- #
# Model metadata                                                              #
# --------------------------------------------------------------------------- #

def get_model_metrics() -> Optional[dict]:
    """Return stored training metrics if available."""
    metrics_path = MODEL_DIR / "metrics.json"
    if not metrics_path.exists():
        return None
    with open(metrics_path) as f:
        return json.load(f)
