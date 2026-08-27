export type LeagueInfo = {
  name: string;
  year: number;
  current_week: number;
  nfl_week?: number | null;
  team_count: number;
  playoff_teams: number;
  scoring_summary: string;
};

export type StandingRow = {
  seed: number;
  team_id: number;
  team_name: string;
  owner_name?: string | null;
  division: string;
  wins: number;
  losses: number;
  record: string;
  h2h_points: number;
  top6_points: number;
  total_points: number;
  points_for: number;
  points_against: number;
  streak: number;
  is_division_leader: boolean;
  band: "leader" | "playoff" | "bubble" | "out";
};

export type MatchupsResponse = {
  week: number;
  top_n: number;
  matchups: Array<{
    home: { team_id: number; team_name: string; score: number | null; top_n: boolean };
    away: { team_id: number; team_name: string; score: number | null; top_n: boolean } | null;
  }>;
};

export type TeamSummary = {
  team_id: number;
  team_name: string;
  owner_name?: string | null;
  division: string;
  wins: number;
  losses: number;
  points_for: number;
  points_against: number;
  avg_points: number;
  highest_score: number;
  lowest_score: number;
  weekly_scores: Array<{ week: number; score: number | null }>;
  roster: Array<{
    name: string;
    position?: string | null;
    slot?: string | null;
    points?: number | null;
    projected?: number | null;
    injured: boolean;
  }>;
};

export type SagarinResponse = {
  rows: Array<{
    rank: number;
    team_id: number;
    team_name: string;
    sagarin_rating: number;
    hypothetical_record: string;
    win_pct: number;
    avg_score: number;
    max_score: number;
    min_score: number;
    strength_of_schedule: number;
    points_for: number;
    actual_record: string;
    pf_rank: number;
    win_pct_rank: number;
    avg_score_rank: number;
  }>;
  heatmap: Array<{
    team_id: number;
    team_name: string;
    cells: Array<{ week: number; rank: number | null; score: number | null }>;
  }>;
  weeks: number[];
};

export type TeamRatingsResponse = {
  scope: "season" | "alltime";
  league_avg_ppg: number;
  league_avg_win_pct: number;
  rows: Array<{
    name: string;
    overall_rating: number;
    ppg_rating: number;
    win_pct_rating: number;
    ppg: number;
    win_pct: number;
    wins: number;
    losses: number;
    games_played: number;
    seasons?: string | null;
  }>;
};

export type AllTimeResponse = {
  start_year: number;
  end_year: number;
  rows: Array<{
    owner_name: string;
    seasons: string;
    wins: number;
    losses: number;
    win_pct: number;
    points_for: number;
    points_against: number;
    avg_pf: number;
    avg_pa: number;
  }>;
};

export type PlayoffsResponse = {
  current_week: number;
  wild_card: Array<{
    label: string;
    seed1: number;
    team1: string;
    seed2?: number | null;
    team2?: string | null;
    note?: string | null;
  }>;
  semifinals: Array<{
    label: string;
    seed1: number;
    team1: string;
    note?: string | null;
  }>;
  championship: { team1: string; team2?: string | null };
  profiles: Array<{
    seed: number;
    team_id: number;
    team_name: string;
    record: string;
    points_for: number;
    points_against: number;
    avg_score: number;
    max_score: number;
    min_score: number;
    win_pct: number;
    recent_form: number[];
  }>;
  head_to_head: Array<{ team1: string; team2: string; wins: number; losses: number }>;
};

export type HealthResponse = {
  ok: boolean;
  espn_ok: boolean;
  message: string;
  auth_required: boolean;
  demo_mode?: boolean;
};
