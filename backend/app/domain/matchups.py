from __future__ import annotations
from app.config import Settings, get_settings
from app.schemas.models import MatchupRow, MatchupSide, MatchupsResponse, WeeklyLeader, WeeklyLeadersResponse


def _top_n_ids_from_scores(score_by_team: dict[int, float], top_n: int) -> set[int]:
    """Rank by the same scores shown in the UI; ignore missing scores."""
    ranked = sorted(
        ((team_id, score) for team_id, score in score_by_team.items() if score is not None),
        key=lambda item: item[1],
        reverse=True,
    )
    return {team_id for team_id, _ in ranked[:top_n]}


def build_matchups(league, week: int | None = None, settings: Settings | None = None) -> MatchupsResponse:
    settings = settings or get_settings()
    # Show the active week (live scores). Callers can still pass an explicit week.
    display_week = week if week is not None else max(1, league.current_week)

    matchups: list[MatchupRow] = []
    score_by_team: dict[int, float] = {}
    try:
        boxes = league.box_scores(display_week)
    except Exception:
        boxes = []

    for matchup in boxes:
        home = matchup.home_team
        home_score = getattr(matchup, "home_score", None)
        away = getattr(matchup, "away_team", None)
        away_score = getattr(matchup, "away_score", None)
        if home_score is not None:
            score_by_team[home.team_id] = float(home_score)
        if away is not None and away_score is not None:
            score_by_team[away.team_id] = float(away_score)
        matchups.append(
            MatchupRow(
                home=MatchupSide(
                    team_id=home.team_id,
                    team_name=home.team_name,
                    score=None if home_score is None else float(home_score),
                    top_n=False,
                ),
                away=None
                if away is None
                else MatchupSide(
                    team_id=away.team_id,
                    team_name=away.team_name,
                    score=None if away_score is None else float(away_score),
                    top_n=False,
                ),
            )
        )

    top_ids = _top_n_ids_from_scores(score_by_team, settings.top_n_bonus)
    for row in matchups:
        row.home.top_n = row.home.team_id in top_ids
        if row.away is not None:
            row.away.top_n = row.away.team_id in top_ids

    return MatchupsResponse(week=display_week, top_n=settings.top_n_bonus, matchups=matchups)


def build_weekly_leaders(league) -> WeeklyLeadersResponse:
    leaders: list[WeeklyLeader] = []
    for week in range(1, league.current_week):
        best = None
        best_score = -1.0
        for team in league.teams:
            if week <= len(team.scores) and team.scores[week - 1] is not None:
                score = float(team.scores[week - 1])
                if score > best_score:
                    best_score = score
                    best = team
        if best is not None:
            leaders.append(
                WeeklyLeader(week=week, team_id=best.team_id, team_name=best.team_name, score=best_score)
            )
    return WeeklyLeadersResponse(leaders=leaders)
