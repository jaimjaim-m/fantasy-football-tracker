from __future__ import annotations
from app.config import Settings, get_settings
from app.schemas.models import MatchupRow, MatchupSide, MatchupsResponse, WeeklyLeader, WeeklyLeadersResponse


def _week_ranks(league, week: int) -> dict[int, tuple[float, int]]:
    scores: list[tuple[object, float]] = []
    for team in league.teams:
        if week <= len(team.scores) and team.scores[week - 1] is not None:
            scores.append((team, float(team.scores[week - 1])))
    scores.sort(key=lambda item: item[1], reverse=True)
    return {team.team_id: (score, rank) for rank, (team, score) in enumerate(scores, 1)}


def build_matchups(league, week: int | None = None, settings: Settings | None = None) -> MatchupsResponse:
    settings = settings or get_settings()
    display_week = week if week is not None else max(1, league.current_week - 1)
    ranks = _week_ranks(league, display_week)
    top_ids = {team_id for team_id, (_, rank) in ranks.items() if rank <= settings.top_n_bonus}

    matchups: list[MatchupRow] = []
    try:
        boxes = league.box_scores(display_week)
    except Exception:
        boxes = []

    for matchup in boxes:
        home = matchup.home_team
        home_score = getattr(matchup, "home_score", None)
        away = getattr(matchup, "away_team", None)
        away_score = getattr(matchup, "away_score", None)
        matchups.append(
            MatchupRow(
                home=MatchupSide(
                    team_id=home.team_id,
                    team_name=home.team_name,
                    score=None if home_score is None else float(home_score),
                    top_n=home.team_id in top_ids,
                ),
                away=None
                if away is None
                else MatchupSide(
                    team_id=away.team_id,
                    team_name=away.team_name,
                    score=None if away_score is None else float(away_score),
                    top_n=away.team_id in top_ids,
                ),
            )
        )
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
