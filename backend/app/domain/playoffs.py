from __future__ import annotations

from app.config import Settings, get_settings
from app.domain.scoring import ordered_standings
from app.schemas.models import HeadToHead, PlayoffMatchup, PlayoffProfile, PlayoffsResponse


def _stats(team, league) -> dict:
    valid = [s for s in team.scores if s is not None and s > 0]
    recent = []
    for week in range(max(1, league.current_week - 2), league.current_week + 1):
        if week <= len(team.scores) and team.scores[week - 1] and team.scores[week - 1] > 0:
            recent.append(float(team.scores[week - 1]))
    games = team.wins + team.losses
    return {
        "record": f"{team.wins}-{team.losses}",
        "points_for": float(team.points_for or 0),
        "points_against": float(team.points_against or 0),
        "avg_score": sum(valid) / len(valid) if valid else 0.0,
        "max_score": max(valid) if valid else 0.0,
        "min_score": min(valid) if valid else 0.0,
        "win_pct": team.wins / games if games else 0.0,
        "recent_form": recent,
    }


def _h2h(team1, team2, league) -> tuple[int, int]:
    wins = losses = 0
    for week in range(1, league.current_week + 1):
        try:
            matchups = league.box_scores(week)
        except Exception:
            continue
        for matchup in matchups:
            home, away = matchup.home_team, getattr(matchup, "away_team", None)
            if away is None:
                continue
            ids = {home.team_id, away.team_id}
            if team1.team_id not in ids or team2.team_id not in ids:
                continue
            if matchup.home_score is None or matchup.away_score is None:
                continue
            if home.team_id == team1.team_id:
                if matchup.home_score > matchup.away_score:
                    wins += 1
                elif matchup.away_score > matchup.home_score:
                    losses += 1
            else:
                if matchup.away_score > matchup.home_score:
                    wins += 1
                elif matchup.home_score > matchup.away_score:
                    losses += 1
    return wins, losses


def build_playoffs(league, settings: Settings | None = None) -> PlayoffsResponse:
    settings = settings or get_settings()
    ordered = ordered_standings(league, settings)
    teams = [rec["team"] for rec in ordered[: settings.playoff_teams]]
    names = [t.team_name for t in teams]
    while len(names) < 6:
        names.append("TBD")
        teams.append(None)

    wild_card = [
        PlayoffMatchup(label="Byes", seed1=1, team1=names[0], seed2=2, team2=names[1], note="First-round byes"),
        PlayoffMatchup(label="WC-B", seed1=3, team1=names[2], seed2=6, team2=names[5]),
        PlayoffMatchup(label="WC-A", seed1=4, team1=names[3], seed2=5, team2=names[4]),
    ]
    semifinals = [
        PlayoffMatchup(label="SF-1", seed1=1, team1=names[0], note="vs winner of WC-B (3 vs 6)"),
        PlayoffMatchup(label="SF-2", seed1=2, team1=names[1], note="vs winner of WC-A (4 vs 5)"),
    ]
    championship = PlayoffMatchup(label="CHAMP", seed1=0, team1="Winner SF-1", team2="Winner SF-2")

    profiles: list[PlayoffProfile] = []
    real_teams = [t for t in teams if t is not None]
    for seed, team in enumerate(real_teams, 1):
        stats = _stats(team, league)
        profiles.append(
            PlayoffProfile(
                seed=seed,
                team_id=team.team_id,
                team_name=team.team_name,
                **stats,
            )
        )

    h2h_rows: list[HeadToHead] = []
    for i, team1 in enumerate(real_teams):
        for team2 in real_teams[i + 1 :]:
            wins, losses = _h2h(team1, team2, league)
            if wins + losses:
                h2h_rows.append(HeadToHead(team1=team1.team_name, team2=team2.team_name, wins=wins, losses=losses))

    return PlayoffsResponse(
        current_week=league.current_week,
        wild_card=wild_card,
        semifinals=semifinals,
        championship=championship,
        profiles=profiles,
        head_to_head=h2h_rows,
    )
