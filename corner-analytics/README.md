# Corner Analytics Platform

Sports betting analytics platform that predicts corner kicks for Premier League, La Liga, Bundesliga, and Serie A matches using machine learning.

## Stack
- **Backend**: Python 3.12 + FastAPI
- **ML Engine**: XGBoost + scikit-learn (quantile regression for 90% CI)
- **Database**: PostgreSQL + SQLAlchemy + Alembic
- **Cache**: Redis
- **Scheduler**: APScheduler (nightly data refresh)
- **Frontend**: Next.js 14 + Tailwind CSS
- **Data Sources**: StatsBomb Open Data (training) + API-Football free tier (live fixtures)

## Quick Start

```bash
# Copy env file and add your API-Football key
cp backend/.env.example backend/.env

# Start all services
docker compose up -d

# Run DB migrations
docker compose exec backend alembic upgrade head

# Seed leagues
docker compose exec backend python -m app.services.seed

# API docs available at:
# http://localhost:8000/docs
# Frontend at:
# http://localhost:3000
```

## Project Structure

```
corner-analytics/
├── backend/
│   ├── app/
│   │   ├── api/          # FastAPI route handlers
│   │   ├── models/       # SQLAlchemy ORM + Pydantic schemas
│   │   ├── services/     # Data ingestion, feature engine, predictor
│   │   └── ml/           # Model training and evaluation
│   └── migrations/       # Alembic migration files
├── frontend/             # Next.js 14 app
└── docker-compose.yml
```

## Build Phases
1. ✅ DB schema + migrations + seed data
2. Data ingestion (StatsBomb + API-Football)
3. Feature engineering + ML model training
4. FastAPI endpoints
5. Next.js frontend (dashboard + charts)
6. Scheduler wiring
7. Backtesting + accuracy reporting
