from __future__ import annotations
from app.domain.scoring import owner_name
from app.schemas.models import RosterPlayer, TeamSummary, TeamsResponse, WeeklyScore


def _roster(team) -> list[RosterPlayer]:
    players: list[RosterPlayer] = []
    for player in getattr(team, "roster", []) or []:
        players.append(
            RosterPlayer(
                name=getattr(player, "name", "Unknown"),
                position=getattr(player, "position", None),
                slot=getattr(player, "slot_position", None) or getattr(player, "lineupSlot", None),
                points=_maybe_float(getattr(player, "points", None)),
                projected=_maybe_float(getattr(player, "projected_points", None)),
                injured=bool(getattr(player, "injured", False)),
            )
        )
    return players


def _maybe_float(value) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _team_summary(team, current_week: int) -> TeamSummary:
    scores = [s for s in team.scores if s is not None]
    nonzero = [s for s in scores if s > 0]
    total = sum(scores)
    count = len(scores) or 1
    weekly = [
        WeeklyScore(week=i + 1, score=None if score is None else float(score))
        for i, score in enumerate(team.scores[:current_week])
    ]
    return TeamSummary(
        team_id=team.team_id,
        team_name=team.team_name,
        owner_name=owner_name(team),
        division=getattr(team, "division_name", "") or "",
        wins=team.wins,
        losses=team.losses,
        points_for=float(team.points_for or 0),
        points_against=float(team.points_against or 0),
        avg_points=total / count if scores else 0.0,
        highest_score=max(scores) if scores else 0.0,
        lowest_score=min(nonzero) if nonzero else 0.0,
        weekly_scores=weekly,
        roster=_roster(team),
    )


def build_teams(league) -> TeamsResponse:
    return TeamsResponse(teams=[_team_summary(team, league.current_week) for team in league.teams])


def build_team(league, team_id: int) -> TeamSummary | None:
    for team in league.teams:
        if team.team_id == team_id:
            return _team_summary(team, league.current_week)
    return None
