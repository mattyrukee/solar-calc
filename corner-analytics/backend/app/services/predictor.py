"""
Corner prediction service.

Stub implementation — Phase 3 will replace this with the real ML model.
"""
import logging
from sqlalchemy.orm import Session

log = logging.getLogger(__name__)


def generate_predictions_for_upcoming(db: Session) -> None:
    """
    Generate / refresh corner predictions for all upcoming scheduled fixtures.

    Phase 3 will implement the full XGBoost prediction pipeline here.
    """
    log.info("Predictor: Phase 3 not yet implemented — skipping prediction run.")
