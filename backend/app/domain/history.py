from __future__ import annotations

from app.espn.client import ESPNAccessError, LeagueClient, owner_name
from app.schemas.models import AllTimeResponse, AllTimeRow, TeamRatingRow, TeamRatingsResponse


def _load_years(client: LeagueClient, start_year: int, end_year: int):
    leagues = []
    for year in range(start_year, end_year + 1):
        try:
            leagues.append((year, client.get_league(year)))
        except (ESPNAccessError, Exception):
            continue
    return leagues


def build_all_time(client: LeagueClient, start_year: int, end_year: int) -> AllTimeResponse:
    aggregates: dict[str, dict] = {}
    for year, league in _load_years(client, start_year, end_year):
        for team in league.teams:
            name = owner_name(team)
            if not name:
                continue
            entry = aggregates.setdefault(
                name,
                {
                    "owner_name": name,
                    "seasons": set(),
                    "wins": 0,
                    "losses": 0,
                    "points_for": 0.0,
                    "points_against": 0.0,
                },
            )
            entry["seasons"].add(year)
            entry["wins"] += team.wins or 0
            entry["losses"] += team.losses or 0
            entry["points_for"] += float(team.points_for or 0)
            entry["points_against"] += float(team.points_against or 0)

    rows: list[AllTimeRow] = []
    for entry in aggregates.values():
        games = entry["wins"] + entry["losses"]
        seasons = sorted(entry["seasons"])
        span = f"{seasons[0]}-{seasons[-1]}" if seasons else "-"
        rows.append(
            AllTimeRow(
                owner_name=entry["owner_name"],
                seasons=span,
                wins=entry["wins"],
                losses=entry["losses"],
                win_pct=(entry["wins"] / games) if games else 0.0,
                points_for=entry["points_for"],
                points_against=entry["points_against"],
                avg_pf=(entry["points_for"] / games) if games else 0.0,
                avg_pa=(entry["points_against"] / games) if games else 0.0,
            )
        )
    rows.sort(key=lambda r: (r.win_pct, r.points_for), reverse=True)
    return AllTimeResponse(start_year=start_year, end_year=end_year, rows=rows)


def build_all_time_ratings(client: LeagueClient, start_year: int, end_year: int) -> TeamRatingsResponse:
    owners: dict[str, dict] = {}
    league_games = 0
    league_points = 0.0
    league_wins = 0
    league_losses = 0

    for year, league in _load_years(client, start_year, end_year):
        for team in league.teams:
            name = owner_name(team)
            if not name:
                continue
            games_played = len([s for s in team.scores if s is not None and s > 0])
            team_points = sum(s for s in team.scores if s is not None and s > 0)
            entry = owners.setdefault(
                name,
                {
                    "seasons": set(),
                    "wins": 0,
                    "losses": 0,
                    "games_played": 0,
                    "total_points": 0.0,
                },
            )
            entry["seasons"].add(year)
            entry["wins"] += team.wins or 0
            entry["losses"] += team.losses or 0
            entry["games_played"] += games_played
            entry["total_points"] += team_points
            league_games += games_played
            league_points += team_points
            league_wins += team.wins or 0
            league_losses += team.losses or 0

    avg_ppg = league_points / league_games if league_games else 0.0
    total_wl = league_wins + league_losses
    avg_win = league_wins / total_wl if total_wl else 0.0

    rows: list[TeamRatingRow] = []
    for name, stats in owners.items():
        ppg = stats["total_points"] / stats["games_played"] if stats["games_played"] else 0.0
        games = stats["wins"] + stats["losses"]
        win_pct = stats["wins"] / games if games else 0.0
        ppg_rating = (ppg / avg_ppg) * 100 if avg_ppg else 100.0
        win_rating = (win_pct / avg_win) * 100 if avg_win else 100.0
        seasons = sorted(stats["seasons"])
        span = f"{seasons[0]}-{seasons[-1]}" if len(seasons) > 1 else (str(seasons[0]) if seasons else "-")
        rows.append(
            TeamRatingRow(
                name=name,
                overall_rating=(ppg_rating + win_rating) / 2,
                ppg_rating=ppg_rating,
                win_pct_rating=win_rating,
                ppg=ppg,
                win_pct=win_pct,
                wins=stats["wins"],
                losses=stats["losses"],
                games_played=stats["games_played"],
                seasons=span,
            )
        )
    rows.sort(key=lambda r: r.overall_rating, reverse=True)
    return TeamRatingsResponse(scope="alltime", league_avg_ppg=avg_ppg, league_avg_win_pct=avg_win, rows=rows)
