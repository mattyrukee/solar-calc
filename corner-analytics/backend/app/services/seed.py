"""
Seed script — inserts the 4 supported leagues into the database.
Run once after initial migration:  python -m app.services.seed
"""
from app.database import SessionLocal
from app.models.db_models import League

LEAGUES = [
    {"api_id": 39, "name": "Premier League", "short_name": "PL", "country": "England"},
    {"api_id": 140, "name": "La Liga", "short_name": "LL", "country": "Spain"},
    {"api_id": 78, "name": "Bundesliga", "short_name": "BL", "country": "Germany"},
    {"api_id": 135, "name": "Serie A", "short_name": "SA", "country": "Italy"},
]


def seed():
    db = SessionLocal()
    try:
        for data in LEAGUES:
            exists = db.query(League).filter(League.api_id == data["api_id"]).first()
            if not exists:
                db.add(League(**data))
        db.commit()
        print("Leagues seeded successfully.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
