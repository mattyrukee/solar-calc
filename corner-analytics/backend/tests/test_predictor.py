"""
Unit tests for the predictor service.

Tests the prediction output shape and confidence score bounds
using a lightweight mock model so no trained .pkl files are needed.
"""
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from app.services.predictor import predict_match


class FakeModel:
    """Minimal stand-in for a joblib-loaded XGBRegressor."""
    def __init__(self, return_value):
        self._val = return_value

    def predict(self, X):
        return np.array([self._val])


@pytest.fixture()
def db_with_match():
    """Return a mock DB session and a minimal Match object."""
    from unittest.mock import MagicMock
    from app.models.db_models import Match, MatchStatus

    match = Match(
        id=1, api_id=12345, league_id=1, season=2024,
        fixture_date=datetime.utcnow() + timedelta(days=1),
        home_team_id=1, away_team_id=2,
        status=MatchStatus.scheduled,
        is_derby=False, is_title_decider=False, is_relegation=False,
    )
    db = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = None  # no existing prediction
    return db, match


def test_predict_match_output_shape(db_with_match):
    """Prediction should return valid bounds and confidence within [0.5, 0.99]."""
    db, match = db_with_match

    from app.services.feature_engine import MatchFeatures
    fake_features = MatchFeatures(
        home_avg_corners_for_h=6.0, home_avg_corners_against_h=4.5,
        away_avg_corners_for_a=5.0, away_avg_corners_against_a=5.0,
        home_avg_corners_for_all=5.8, away_avg_corners_for_all=4.9,
        home_form_corners=6.2, away_form_corners=4.8,
        home_avg_shots=12.0, away_avg_shots=9.0,
        home_avg_possession=54.0, away_avg_possession=46.0,
        h2h_avg_total_corners=10.5, h2h_matches_available=4,
        league_avg_corners=10.2,
        is_derby=0, is_title_decider=0, is_relegation=0,
    )

    with (
        patch("app.services.predictor._ensure_models", return_value=True),
        patch("app.services.predictor._point_model", FakeModel(10.5)),
        patch("app.services.predictor._low_model", FakeModel(7.0)),
        patch("app.services.predictor._high_model", FakeModel(14.0)),
        patch("app.services.predictor._feature_names", list(fake_features.to_dict().keys())),
        patch("app.services.feature_engine.build_features", return_value=fake_features),
        patch("app.services.predictor.build_features", return_value=fake_features),
    ):
        prediction = predict_match(db, match)

    assert prediction is not None
    assert prediction.predicted_total == pytest.approx(10.5, abs=0.1)
    assert prediction.low_bound <= prediction.predicted_total <= prediction.high_bound
    assert 0.5 <= prediction.confidence_score <= 0.99
    assert prediction.model_version == "v1"


def test_predict_match_returns_none_when_no_features(db_with_match):
    """If features cannot be built, predict_match should return None."""
    db, match = db_with_match

    with (
        patch("app.services.predictor._ensure_models", return_value=True),
        patch("app.services.predictor.build_features", return_value=None),
    ):
        result = predict_match(db, match)

    assert result is None


def test_predict_match_skips_when_models_not_trained(db_with_match):
    """If models are not loaded, predict_match should return None gracefully."""
    db, match = db_with_match

    with patch("app.services.predictor._ensure_models", return_value=False):
        result = predict_match(db, match)

    assert result is None
