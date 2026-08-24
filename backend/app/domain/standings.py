from __future__ import annotations

from app.config import Settings, get_settings
from app.domain.scoring import ordered_standings, owner_name, seed_band
from app.schemas.models import StandingRow, StandingsResponse


def build_standings(league, settings: Settings | None = None) -> StandingsResponse:
    settings = settings or get_settings()
    ordered = ordered_standings(league, settings)
    rows: list[StandingRow] = []
    for seed, rec in enumerate(ordered, 1):
        team = rec["team"]
        rows.append(
            StandingRow(
                seed=seed,
                team_id=team.team_id,
                team_name=team.team_name,
                owner_name=owner_name(team),
                division=rec["division"],
                wins=team.wins,
                losses=team.losses,
                record=f"{team.wins}-{team.losses}",
                h2h_points=rec["h2h"],
                top6_points=rec["top6"],
                total_points=rec["total"],
                points_for=rec["pf"],
                points_against=rec["pa"],
                streak=rec["streak"],
                is_division_leader=rec["is_division_leader"],
                band=seed_band(seed, rec["is_division_leader"], settings.playoff_teams),
            )
        )
    return StandingsResponse(week=league.current_week, rows=rows)
