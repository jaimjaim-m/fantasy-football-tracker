from __future__ import annotations

from collections import defaultdict

from app.config import Settings, get_settings


def owner_name(team) -> str | None:
    from app.espn.client import owner_name as _owner_name

    return _owner_name(team)


def streak_value(team) -> int:
    length = getattr(team, "streak_length", 0) or 0
    kind = str(getattr(team, "streak_type", "")).upper()
    if kind in ("W", "WIN"):
        return length
    if kind in ("L", "LOSS"):
        return -length
    return 0


def weekly_scores_and_ranks(league) -> dict[int, list[tuple[float, int]]]:
    """team_id -> list of (score, rank) for completed weeks before current_week."""
    weekly: dict[int, list[tuple[float, int]]] = defaultdict(list)
    for week in range(1, league.current_week):
        week_scores: list[tuple[object, float]] = []
        for team in league.teams:
            if week <= len(team.scores) and team.scores[week - 1] is not None:
                week_scores.append((team, team.scores[week - 1]))
        week_scores.sort(key=lambda item: item[1], reverse=True)
        for rank, (team, score) in enumerate(week_scores, 1):
            weekly[team.team_id].append((score, rank))
    return weekly


def custom_points(league, settings: Settings | None = None) -> dict[int, dict[str, int]]:
    settings = settings or get_settings()
    weekly = weekly_scores_and_ranks(league)
    points: dict[int, dict[str, int]] = defaultdict(lambda: {"h2h_points": 0, "top6_points": 0})
    for team in league.teams:
        points[team.team_id]["h2h_points"] = team.wins * settings.h2h_win_points
        top_n = sum(1 for _, rank in weekly.get(team.team_id, []) if rank <= settings.top_n_bonus)
        points[team.team_id]["top6_points"] = top_n * settings.top_n_points
    return points


def ordered_standings(league, settings: Settings | None = None) -> list[dict]:
    """Division winners occupy seeds 1-2; remaining teams by total points then PF."""
    settings = settings or get_settings()
    points = custom_points(league, settings)
    records: list[dict] = []
    for team in league.teams:
        h2h = points[team.team_id]["h2h_points"]
        top6 = points[team.team_id]["top6_points"]
        records.append(
            {
                "team": team,
                "division": getattr(team, "division_name", "") or "",
                "h2h": h2h,
                "top6": top6,
                "total": h2h + top6,
                "pf": float(team.points_for or 0),
                "pa": float(team.points_against or 0),
                "streak": streak_value(team),
            }
        )

    division_best: dict[str, dict] = {}
    for rec in records:
        div = rec["division"] or "_none"
        current = division_best.get(div)
        if current is None or (rec["total"], rec["pf"]) > (current["total"], current["pf"]):
            division_best[div] = rec

    leaders = list(division_best.values())
    leaders.sort(key=lambda rec: (rec["total"], rec["pf"]), reverse=True)
    leader_ids = {id(rec["team"]) for rec in leaders}
    others = [rec for rec in records if id(rec["team"]) not in leader_ids]
    others.sort(key=lambda rec: (rec["total"], rec["pf"]), reverse=True)
    ordered = leaders + others
    for rec in ordered:
        rec["is_division_leader"] = id(rec["team"]) in leader_ids
    return ordered


def seed_band(seed: int, is_leader: bool, playoff_teams: int) -> str:
    if is_leader or seed <= 2:
        return "leader"
    if seed <= playoff_teams:
        return "playoff"
    if seed <= playoff_teams + 2:
        return "bubble"
    return "out"
