"""
APScheduler nightly data refresh.

Jobs run in this order every night at 02:00 UTC:
  1. sync_teams          — ensure all teams exist in DB
  2. sync_upcoming       — pull next 7 days of fixtures
  3. sync_results        — update corners/scores for recently finished matches
  4. run_predictions     — generate fresh predictions for all upcoming fixtures

The scheduler is started when the FastAPI app starts up and stopped on shutdown.
"""
import logging

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

log = logging.getLogger(__name__)

_scheduler: BackgroundScheduler | None = None


def _run_nightly_pipeline():
    """Full nightly data refresh + prediction regeneration."""
    log.info("Nightly pipeline starting...")

    # Import here to avoid circular imports at module load time
    from app.database import SessionLocal
    from app.services.api_football import APIFootballClient
    from app.services.data_ingestion import (
        sync_teams,
        sync_upcoming_fixtures,
        sync_finished_results,
    )

    db = SessionLocal()
    try:
        with APIFootballClient() as client:
            log.info("Step 1/4 — Syncing teams...")
            sync_teams(db, client)

            log.info("Step 2/4 — Syncing upcoming fixtures...")
            sync_upcoming_fixtures(db, client, days_ahead=7)

            log.info("Step 3/4 — Syncing finished results...")
            sync_finished_results(db, client, days_back=3)

        log.info("Step 4/4 — Running predictions for upcoming fixtures...")
        _run_predictions(db)

    except Exception as exc:
        log.error("Nightly pipeline failed: %s", exc, exc_info=True)
    finally:
        db.close()

    log.info("Nightly pipeline complete.")


def _run_predictions(db):
    """Generate / refresh predictions for all upcoming scheduled fixtures."""
    try:
        from app.services.predictor import generate_predictions_for_upcoming
        generate_predictions_for_upcoming(db)
    except Exception as exc:
        log.error("Prediction generation failed: %s", exc, exc_info=True)


def start_scheduler():
    global _scheduler
    if _scheduler is not None:
        return

    _scheduler = BackgroundScheduler(timezone="UTC")

    # Nightly at 02:00 UTC
    _scheduler.add_job(
        _run_nightly_pipeline,
        trigger=CronTrigger(hour=2, minute=0),
        id="nightly_pipeline",
        name="Nightly data refresh + predictions",
        replace_existing=True,
        misfire_grace_time=3600,  # allow up to 1h late start
    )

    # Also run predictions every 6 hours in case new fixtures are added
    _scheduler.add_job(
        lambda: _run_predictions_standalone(),
        trigger=CronTrigger(hour="*/6", minute=30),
        id="refresh_predictions",
        name="Refresh predictions every 6h",
        replace_existing=True,
    )

    _scheduler.start()
    log.info("Scheduler started. Nightly pipeline runs at 02:00 UTC.")


def _run_predictions_standalone():
    from app.database import SessionLocal
    db = SessionLocal()
    try:
        _run_predictions(db)
    finally:
        db.close()


def stop_scheduler():
    global _scheduler
    if _scheduler is not None:
        _scheduler.shutdown(wait=False)
        _scheduler = None
        log.info("Scheduler stopped.")
