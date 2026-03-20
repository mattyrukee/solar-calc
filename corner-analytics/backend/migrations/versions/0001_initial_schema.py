"""Initial schema — leagues, teams, matches, team_match_stats, predictions

Revision ID: 0001
Revises:
Create Date: 2026-03-20
"""
from typing import Sequence, Union
import sqlalchemy as sa
from alembic import op

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- leagues ---
    op.create_table(
        "leagues",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("api_id", sa.Integer(), nullable=False, unique=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("short_name", sa.String(20), nullable=False),
        sa.Column("country", sa.String(50), nullable=False),
        sa.Column("logo_url", sa.String(255)),
    )

    # --- teams ---
    op.create_table(
        "teams",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("api_id", sa.Integer(), nullable=False, unique=True),
        sa.Column("league_id", sa.Integer(), sa.ForeignKey("leagues.id"), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("short_name", sa.String(30)),
        sa.Column("logo_url", sa.String(255)),
    )

    # --- match status enum ---
    match_status = sa.Enum("scheduled", "live", "finished", "postponed", name="matchstatus")
    match_status.create(op.get_bind())

    # --- matches ---
    op.create_table(
        "matches",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("api_id", sa.Integer(), nullable=False, unique=True),
        sa.Column("league_id", sa.Integer(), sa.ForeignKey("leagues.id"), nullable=False),
        sa.Column("season", sa.Integer(), nullable=False),
        sa.Column("fixture_date", sa.DateTime(), nullable=False),
        sa.Column("home_team_id", sa.Integer(), sa.ForeignKey("teams.id"), nullable=False),
        sa.Column("away_team_id", sa.Integer(), sa.ForeignKey("teams.id"), nullable=False),
        sa.Column("status", match_status, server_default="scheduled"),
        sa.Column("home_score", sa.Integer()),
        sa.Column("away_score", sa.Integer()),
        sa.Column("home_corners", sa.Integer()),
        sa.Column("away_corners", sa.Integer()),
        sa.Column("total_corners", sa.Integer()),
        sa.Column("is_derby", sa.Boolean(), server_default="false"),
        sa.Column("is_title_decider", sa.Boolean(), server_default="false"),
        sa.Column("is_relegation", sa.Boolean(), server_default="false"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_index("ix_matches_fixture_date", "matches", ["fixture_date"])
    op.create_index("ix_matches_league_status", "matches", ["league_id", "status"])

    # --- team_match_stats ---
    op.create_table(
        "team_match_stats",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("match_id", sa.Integer(), sa.ForeignKey("matches.id"), nullable=False),
        sa.Column("team_id", sa.Integer(), sa.ForeignKey("teams.id"), nullable=False),
        sa.Column("is_home", sa.Boolean(), nullable=False),
        sa.Column("corners_for", sa.Integer()),
        sa.Column("corners_against", sa.Integer()),
        sa.Column("shots_total", sa.Integer()),
        sa.Column("shots_on_target", sa.Integer()),
        sa.Column("possession", sa.Float()),
        sa.Column("ppda", sa.Float()),
        sa.Column("formation", sa.String(20)),
        sa.UniqueConstraint("match_id", "team_id", name="uq_match_team"),
    )

    # --- predictions ---
    op.create_table(
        "predictions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("match_id", sa.Integer(), sa.ForeignKey("matches.id"), nullable=False, unique=True),
        sa.Column("predicted_total", sa.Float(), nullable=False),
        sa.Column("low_bound", sa.Integer(), nullable=False),
        sa.Column("high_bound", sa.Integer(), nullable=False),
        sa.Column("confidence_score", sa.Float(), nullable=False),
        sa.Column("home_avg_corners_for", sa.Float()),
        sa.Column("away_avg_corners_for", sa.Float()),
        sa.Column("home_avg_corners_against", sa.Float()),
        sa.Column("away_avg_corners_against", sa.Float()),
        sa.Column("h2h_avg_corners", sa.Float()),
        sa.Column("home_press_intensity", sa.Float()),
        sa.Column("away_press_intensity", sa.Float()),
        sa.Column("league_avg_corners", sa.Float()),
        sa.Column("model_version", sa.String(20), nullable=False),
        sa.Column("generated_at", sa.DateTime(), server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("predictions")
    op.drop_table("team_match_stats")
    op.drop_index("ix_matches_league_status", "matches")
    op.drop_index("ix_matches_fixture_date", "matches")
    op.drop_table("matches")
    sa.Enum(name="matchstatus").drop(op.get_bind())
    op.drop_table("teams")
    op.drop_table("leagues")
