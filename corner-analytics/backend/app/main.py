from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import fixtures, predictions, teams, leagues, admin
from app.scheduler import start_scheduler, stop_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    start_scheduler()
    yield
    stop_scheduler()


app = FastAPI(
    title="Corner Analytics API",
    description="Predicts corner kicks for Premier League, La Liga, Bundesliga & Serie A matches.",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(leagues.router, prefix="/api/leagues", tags=["Leagues"])
app.include_router(fixtures.router, prefix="/api/fixtures", tags=["Fixtures"])
app.include_router(predictions.router, prefix="/api/predictions", tags=["Predictions"])
app.include_router(teams.router, prefix="/api/teams", tags=["Teams"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin"])


@app.get("/health")
def health():
    return {"status": "ok"}
