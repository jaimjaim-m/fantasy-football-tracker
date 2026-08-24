from __future__ import annotations

from app.schemas.models import (
    HeatmapCell,
    HeatmapRow,
    SagarinResponse,
    SagarinRow,
    TeamRatingRow,
    TeamRatingsResponse,
)


def _valid_scores(team) -> list[float]:
    return [float(s) for s in team.scores if s is not None]


def calculate_sagarin(league) -> SagarinResponse:
    teams = league.teams
    n = len(teams)
    total_wins = [0] * n
    total_losses = [0] * n
    opponents_faced: list[set[int]] = [set() for _ in range(n)]

    for week in range(1, league.current_week + 1):
        try:
            for matchup in league.box_scores(week):
                home_id = matchup.home_team.team_id
                away = getattr(matchup, "away_team", None)
                if away is None:
                    continue
                home_idx = next((i for i, t in enumerate(teams) if t.team_id == home_id), None)
                away_idx = next((i for i, t in enumerate(teams) if t.team_id == away.team_id), None)
                if home_idx is not None and away_idx is not None:
                    opponents_faced[home_idx].add(away.team_id)
                    opponents_faced[away_idx].add(home_id)
        except Exception:
            pass

        week_scores: list[tuple[int, float]] = []
        for i, team in enumerate(teams):
            if week <= len(team.scores) and team.scores[week - 1] is not None:
                week_scores.append((i, float(team.scores[week - 1])))
        if not week_scores:
            continue
        week_scores.sort(key=lambda item: item[1], reverse=True)
        for rank, (idx, _) in enumerate(week_scores):
            wins = len(week_scores) - rank - 1
            losses = rank
            total_wins[idx] += wins
            total_losses[idx] += losses

    raw: list[dict] = []
    for i, team in enumerate(teams):
        games = total_wins[i] + total_losses[i]
        win_pct = total_wins[i] / games if games else 0.0
        rating = 100 + (win_pct - 0.5) * 200
        scores = _valid_scores(team)
        nonzero = [s for s in scores if s > 0]
        raw.append(
            {
                "team": team,
                "sagarin_rating": rating,
                "total_wins": total_wins[i],
                "total_losses": total_losses[i],
                "win_pct": win_pct,
                "avg_score": sum(scores) / len(scores) if scores else 0.0,
                "max_score": max(scores) if scores else 0.0,
                "min_score": min(nonzero) if nonzero else 0.0,
                "points_for": float(team.points_for or 0),
                "actual_wins": team.wins,
                "actual_losses": team.losses,
                "opponents": opponents_faced[i],
            }
        )
    raw.sort(key=lambda item: item["sagarin_rating"], reverse=True)

    id_to_rating = {item["team"].team_id: item["sagarin_rating"] for item in raw}
    league_avg = sum(item["sagarin_rating"] for item in raw) / len(raw) if raw else 100.0
    for item in raw:
        opp = [id_to_rating[oid] for oid in item["opponents"] if oid in id_to_rating]
        item["sos"] = sum(opp) / len(opp) if opp else league_avg

    pf_ranks = {item["team"].team_id: i + 1 for i, item in enumerate(sorted(raw, key=lambda x: x["points_for"], reverse=True))}
    win_ranks = {
        item["team"].team_id: i + 1
        for i, item in enumerate(
            sorted(
                raw,
                key=lambda x: x["actual_wins"] / (x["actual_wins"] + x["actual_losses"])
                if (x["actual_wins"] + x["actual_losses"])
                else 0,
                reverse=True,
            )
        )
    }
    avg_ranks = {item["team"].team_id: i + 1 for i, item in enumerate(sorted(raw, key=lambda x: x["avg_score"], reverse=True))}

    rows = [
        SagarinRow(
            rank=i + 1,
            team_id=item["team"].team_id,
            team_name=item["team"].team_name,
            sagarin_rating=item["sagarin_rating"],
            hypothetical_record=f"{item['total_wins']}-{item['total_losses']}",
            win_pct=item["win_pct"],
            avg_score=item["avg_score"],
            max_score=item["max_score"],
            min_score=item["min_score"],
            strength_of_schedule=item["sos"],
            points_for=item["points_for"],
            actual_record=f"{item['actual_wins']}-{item['actual_losses']}",
            pf_rank=pf_ranks[item["team"].team_id],
            win_pct_rank=win_ranks[item["team"].team_id],
            avg_score_rank=avg_ranks[item["team"].team_id],
        )
        for i, item in enumerate(raw)
    ]

    weeks = []
    for week in range(1, league.current_week + 1):
        if any(week <= len(t.scores) and t.scores[week - 1] and t.scores[week - 1] > 0 for t in teams):
            weeks.append(week)

    heatmap: list[HeatmapRow] = []
    for item in raw:
        team = item["team"]
        cells: list[HeatmapCell] = []
        for week in weeks:
            if week <= len(team.scores) and team.scores[week - 1] is not None and team.scores[week - 1] > 0:
                score = float(team.scores[week - 1])
                week_scores = sorted(
                    [
                        float(t.scores[week - 1])
                        for t in teams
                        if week <= len(t.scores) and t.scores[week - 1] is not None and t.scores[week - 1] > 0
                    ],
                    reverse=True,
                )
                rank = week_scores.index(score) + 1 if week_scores else None
                cells.append(HeatmapCell(week=week, rank=rank, score=score))
            else:
                cells.append(HeatmapCell(week=week, rank=None, score=None))
        heatmap.append(HeatmapRow(team_id=team.team_id, team_name=team.team_name, cells=cells))

    return SagarinResponse(rows=rows, heatmap=heatmap, weeks=weeks)


def season_team_ratings(league) -> TeamRatingsResponse:
    all_scores: list[float] = []
    total_wins = total_losses = 0
    for team in league.teams:
        all_scores.extend(s for s in team.scores if s is not None and s > 0)
        total_wins += team.wins
        total_losses += team.losses
    league_avg_ppg = sum(all_scores) / len(all_scores) if all_scores else 0.0
    games = total_wins + total_losses
    league_avg_win = total_wins / games if games else 0.0

    rows: list[TeamRatingRow] = []
    for team in league.teams:
        valid = [s for s in team.scores if s is not None and s > 0]
        ppg = sum(valid) / len(valid) if valid else 0.0
        team_games = team.wins + team.losses
        win_pct = team.wins / team_games if team_games else 0.0
        ppg_rating = (ppg / league_avg_ppg) * 100 if league_avg_ppg else 100.0
        win_rating = (win_pct / league_avg_win) * 100 if league_avg_win else 100.0
        rows.append(
            TeamRatingRow(
                name=team.team_name,
                overall_rating=(ppg_rating + win_rating) / 2,
                ppg_rating=ppg_rating,
                win_pct_rating=win_rating,
                ppg=ppg,
                win_pct=win_pct,
                wins=team.wins,
                losses=team.losses,
                games_played=len(valid),
            )
        )
    rows.sort(key=lambda r: r.overall_rating, reverse=True)
    return TeamRatingsResponse(
        scope="season",
        league_avg_ppg=league_avg_ppg,
        league_avg_win_pct=league_avg_win,
        rows=rows,
    )
