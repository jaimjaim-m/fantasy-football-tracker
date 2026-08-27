from __future__ import annotations

from typing import List, Literal, Optional

from pydantic import BaseModel, Field

SeedBand = Literal["leader", "playoff", "bubble", "out"]


class HealthResponse(BaseModel):
    ok: bool
    espn_ok: bool
    message: str
    auth_required: bool
    demo_mode: bool = False


class LeagueInfo(BaseModel):
    name: str
    year: int
    current_week: int
    nfl_week: Optional[int] = None
    team_count: int
    playoff_teams: int
    scoring_summary: str


class StandingRow(BaseModel):
    seed: int
    team_id: int
    team_name: str
    owner_name: Optional[str] = None
    division: str
    wins: int
    losses: int
    record: str
    h2h_points: int
    top6_points: int
    total_points: int
    points_for: float
    points_against: float
    streak: int
    is_division_leader: bool
    band: SeedBand


class StandingsResponse(BaseModel):
    week: int
    rows: List[StandingRow]


class MatchupSide(BaseModel):
    team_id: int
    team_name: str
    score: Optional[float]
    top_n: bool = False


class MatchupRow(BaseModel):
    home: MatchupSide
    away: Optional[MatchupSide] = None


class MatchupsResponse(BaseModel):
    week: int
    top_n: int
    matchups: List[MatchupRow]


class WeeklyScore(BaseModel):
    week: int
    score: Optional[float]


class RosterPlayer(BaseModel):
    name: str
    position: Optional[str] = None
    slot: Optional[str] = None
    points: Optional[float] = None
    projected: Optional[float] = None
    injured: bool = False


class TeamSummary(BaseModel):
    team_id: int
    team_name: str
    owner_name: Optional[str] = None
    division: str
    wins: int
    losses: int
    points_for: float
    points_against: float
    avg_points: float
    highest_score: float
    lowest_score: float
    weekly_scores: List[WeeklyScore] = Field(default_factory=list)
    roster: List[RosterPlayer] = Field(default_factory=list)


class TeamsResponse(BaseModel):
    teams: List[TeamSummary]


class WeeklyLeader(BaseModel):
    week: int
    team_id: int
    team_name: str
    score: float


class WeeklyLeadersResponse(BaseModel):
    leaders: List[WeeklyLeader]


class SagarinRow(BaseModel):
    rank: int
    team_id: int
    team_name: str
    sagarin_rating: float
    hypothetical_record: str
    win_pct: float
    avg_score: float
    max_score: float
    min_score: float
    strength_of_schedule: float
    points_for: float
    actual_record: str
    pf_rank: int
    win_pct_rank: int
    avg_score_rank: int


class HeatmapCell(BaseModel):
    week: int
    rank: Optional[int]
    score: Optional[float]


class HeatmapRow(BaseModel):
    team_id: int
    team_name: str
    cells: List[HeatmapCell]


class SagarinResponse(BaseModel):
    rows: List[SagarinRow]
    heatmap: List[HeatmapRow]
    weeks: List[int]


class TeamRatingRow(BaseModel):
    name: str
    overall_rating: float
    ppg_rating: float
    win_pct_rating: float
    ppg: float
    win_pct: float
    wins: int
    losses: int
    games_played: int
    seasons: Optional[str] = None


class TeamRatingsResponse(BaseModel):
    scope: Literal["season", "alltime"]
    league_avg_ppg: float
    league_avg_win_pct: float
    rows: List[TeamRatingRow]


class AllTimeRow(BaseModel):
    owner_name: str
    seasons: str
    wins: int
    losses: int
    win_pct: float
    points_for: float
    points_against: float
    avg_pf: float
    avg_pa: float


class AllTimeResponse(BaseModel):
    start_year: int
    end_year: int
    rows: List[AllTimeRow]


class PlayoffMatchup(BaseModel):
    label: str
    seed1: int
    team1: str
    seed2: Optional[int] = None
    team2: Optional[str] = None
    note: Optional[str] = None


class PlayoffProfile(BaseModel):
    seed: int
    team_id: int
    team_name: str
    record: str
    points_for: float
    points_against: float
    avg_score: float
    max_score: float
    min_score: float
    win_pct: float
    recent_form: List[float]


class HeadToHead(BaseModel):
    team1: str
    team2: str
    wins: int
    losses: int


class PlayoffsResponse(BaseModel):
    current_week: int
    wild_card: List[PlayoffMatchup]
    semifinals: List[PlayoffMatchup]
    championship: PlayoffMatchup
    profiles: List[PlayoffProfile]
    head_to_head: List[HeadToHead]


class WeekStatusResponse(BaseModel):
    week: int
    is_final: bool
    message: str
