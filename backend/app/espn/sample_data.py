"""Deterministic sample league for local UI / link testing without ESPN auth."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class SampleSettings:
    name: str = "Demo Dynasty League"


@dataclass
class SamplePlayer:
    name: str
    position: str
    slot_position: str
    points: float
    projected_points: float
    injured: bool = False


@dataclass
class SampleTeam:
    team_id: int
    team_name: str
    division_name: str
    owners: list
    wins: int
    losses: int
    points_for: float
    points_against: float
    scores: List[Optional[float]]
    streak_length: int = 1
    streak_type: str = "W"
    roster: List[SamplePlayer] = field(default_factory=list)


@dataclass
class SampleMatchup:
    home_team: SampleTeam
    away_team: Optional[SampleTeam]
    home_score: Optional[float]
    away_score: Optional[float]


@dataclass
class SampleLeague:
    year: int
    current_week: int
    nfl_week: int
    teams: List[SampleTeam]
    settings: SampleSettings = field(default_factory=SampleSettings)
    _pairings: List[tuple] = field(default_factory=list)

    def box_scores(self, week: int) -> List[SampleMatchup]:
        if week < 1 or week > len(self._pairings):
            # Fall back to rotating pairings from week 1 template
            pairs = self._pairings[0] if self._pairings else []
        else:
            pairs = self._pairings[week - 1]
        matchups: List[SampleMatchup] = []
        for home_id, away_id in pairs:
            home = self._team(home_id)
            away = self._team(away_id) if away_id is not None else None
            home_score = home.scores[week - 1] if week <= len(home.scores) else None
            away_score = (
                away.scores[week - 1] if away is not None and week <= len(away.scores) else None
            )
            matchups.append(
                SampleMatchup(
                    home_team=home,
                    away_team=away,
                    home_score=home_score,
                    away_score=away_score,
                )
            )
        return matchups

    def _team(self, team_id: int) -> SampleTeam:
        for team in self.teams:
            if team.team_id == team_id:
                return team
        raise KeyError(team_id)


_OWNERS = [
    ("Alex Rivera", "East"),
    ("Jordan Lee", "East"),
    ("Sam Patel", "East"),
    ("Casey Nguyen", "East"),
    ("Morgan Blake", "East"),
    ("Riley Quinn", "East"),
    ("Taylor Brooks", "West"),
    ("Jamie Ortiz", "West"),
    ("Avery Kim", "West"),
    ("Cameron Diaz", "West"),
    ("Reese Park", "West"),
    ("Drew Santos", "West"),
]

_TEAM_NAMES = [
    "Gridiron Ghosts",
    "Endzone Express",
    "Blitz Brigade",
    "Touchdown Titans",
    "Red Zone Renegades",
    "Pigskin Pirates",
    "Fourth Down Force",
    "Hail Mary Heroes",
    "Sack Attack",
    "Audible Aces",
    "Snap Decision",
    "First Down Dynasty",
]

# Weekly scores weeks 1–7 (current_week = 8). Tuned so standings / top-6 look realistic.
_SCORES = [
    [118.4, 102.1, 131.2, 97.5, 124.0, 109.3, 115.8],
    [105.2, 128.7, 99.4, 112.0, 101.6, 119.5, 108.2],
    [94.1, 111.3, 120.5, 103.8, 98.2, 125.4, 91.7],
    [122.6, 88.4, 107.9, 130.1, 114.5, 96.0, 121.3],
    [101.0, 116.8, 93.2, 108.7, 127.3, 104.1, 99.5],
    [87.5, 100.2, 114.8, 95.6, 109.9, 91.4, 126.0],
    [133.1, 107.4, 98.6, 121.9, 103.2, 116.7, 94.8],
    [110.5, 124.3, 106.1, 89.7, 118.8, 102.4, 113.6],
    [96.8, 91.5, 125.7, 117.2, 92.4, 108.9, 104.0],
    [113.9, 119.0, 90.3, 104.5, 111.1, 97.8, 122.5],
    [99.6, 105.7, 112.4, 126.8, 95.0, 120.2, 100.9],
    [108.3, 97.1, 101.8, 92.9, 120.6, 113.0, 107.4],
]

_WINS = [5, 4, 3, 5, 4, 2, 5, 4, 3, 3, 4, 2]
_LOSSES = [2, 3, 4, 2, 3, 5, 2, 3, 4, 4, 3, 5]
_STREAKS = [
    (3, "W"),
    (1, "L"),
    (2, "L"),
    (2, "W"),
    (1, "W"),
    (3, "L"),
    (4, "W"),
    (2, "W"),
    (1, "L"),
    (2, "L"),
    (1, "W"),
    (4, "L"),
]

_ROSTER_TEMPLATES = [
    ("QB", "QB", "Starter QB"),
    ("RB", "RB", "Starter RB1"),
    ("RB", "RB", "Starter RB2"),
    ("WR", "WR", "Starter WR1"),
    ("WR", "WR", "Starter WR2"),
    ("TE", "TE", "Starter TE"),
    ("D/ST", "D/ST", "Team Defense"),
    ("K", "K", "Kicker"),
]


def _pairings_for_week(week: int) -> list[tuple[int, Optional[int]]]:
    """Rotate 12-team schedule into 6 matchups."""
    ids = list(range(1, 13))
    # Rotate everyone except team 1 (circle method)
    offset = (week - 1) % 11
    rotated = [ids[0]] + ids[1 + offset :] + ids[1 : 1 + offset]
    pairs = []
    for i in range(6):
        pairs.append((rotated[i], rotated[11 - i]))
    return pairs


def _build_roster(team_idx: int) -> list[SamplePlayer]:
    owner_first = _OWNERS[team_idx][0].split()[0]
    players = []
    for i, (pos, slot, label) in enumerate(_ROSTER_TEMPLATES):
        pts = 8.0 + ((team_idx + i) % 7) * 2.4
        players.append(
            SamplePlayer(
                name=f"{owner_first}'s {label}",
                position=pos,
                slot_position=slot,
                points=round(pts, 1),
                projected_points=round(pts + 1.5, 1),
                injured=team_idx == 5 and i == 1,
            )
        )
    return players


def build_sample_league(year: int = 2025, current_week: int = 8) -> SampleLeague:
    teams: list[SampleTeam] = []
    for i in range(12):
        scores = list(_SCORES[i][: current_week - 1])
        # Pad if somehow short
        while len(scores) < current_week - 1:
            scores.append(100.0)
        pf = float(sum(s for s in scores if s is not None))
        # Scale PA from opposite side of the table for variety
        pa = float(sum(_SCORES[11 - i][: current_week - 1]))
        # For historical years, nudge records slightly
        year_delta = max(0, 2025 - year)
        wins = max(0, _WINS[i] - (year_delta % 3))
        losses = max(0, _LOSSES[i] + (year_delta % 2))
        streak_len, streak_type = _STREAKS[i]
        teams.append(
            SampleTeam(
                team_id=i + 1,
                team_name=_TEAM_NAMES[i],
                division_name=_OWNERS[i][1],
                owners=[{"displayName": _OWNERS[i][0], "firstName": _OWNERS[i][0].split()[0], "lastName": _OWNERS[i][0].split()[-1]}],
                wins=wins,
                losses=losses,
                points_for=round(pf + year_delta * 12.5, 1),
                points_against=round(pa + year_delta * 8.0, 1),
                scores=scores,
                streak_length=streak_len,
                streak_type=streak_type,
                roster=_build_roster(i),
            )
        )

    pairings = [_pairings_for_week(w) for w in range(1, max(current_week, 1))]
    # Ensure at least one week of pairings exists for box_scores fallback
    if not pairings:
        pairings = [_pairings_for_week(1)]

    return SampleLeague(
        year=year,
        current_week=current_week,
        nfl_week=current_week,
        teams=teams,
        settings=SampleSettings(name="Demo Dynasty League"),
        _pairings=pairings,
    )
