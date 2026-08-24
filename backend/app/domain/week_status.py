from __future__ import annotations

from app.schemas.models import WeekStatusResponse


def week_status(league, week: int | None = None) -> WeekStatusResponse:
    check_week = league.current_week if week is None else week
    if check_week < 1:
        return WeekStatusResponse(week=check_week, is_final=False, message=f"Week {check_week} is not valid")
    if check_week > league.current_week:
        return WeekStatusResponse(
            week=check_week,
            is_final=False,
            message=f"Week {check_week} is in the future (current week: {league.current_week})",
        )

    incomplete: list[str] = []
    teams_with_scores = 0
    teams_with_zero = 0
    all_final = True

    for team in league.teams:
        if check_week > len(team.scores) or team.scores[check_week - 1] is None:
            all_final = False
            break
        score = team.scores[check_week - 1]
        if score == 0.0:
            teams_with_zero += 1
        else:
            teams_with_scores += 1

    if teams_with_zero > 0 and teams_with_scores == 0:
        all_final = False

    try:
        matchups = league.box_scores(check_week)
    except Exception as exc:
        return WeekStatusResponse(week=check_week, is_final=False, message=f"Error checking week {check_week}: {exc}")

    if not matchups:
        return WeekStatusResponse(week=check_week, is_final=False, message=f"No matchups found for week {check_week}")

    for matchup in matchups:
        home = getattr(matchup, "home_score", None)
        away = getattr(matchup, "away_score", None)
        home_name = matchup.home_team.team_name
        away_name = matchup.away_team.team_name if getattr(matchup, "away_team", None) else "BYE"
        if home is None or away is None or (home == 0.0 and away == 0.0):
            all_final = False
            incomplete.append(f"{home_name} vs {away_name}")

    if all_final:
        return WeekStatusResponse(
            week=check_week,
            is_final=True,
            message=f"Week {check_week} is final — all games complete including Monday Night Football",
        )
    detail = ", ".join(incomplete) if incomplete else "Some teams may not have final scores"
    return WeekStatusResponse(
        week=check_week,
        is_final=False,
        message=f"Week {check_week} is not final. Incomplete: {detail}",
    )
