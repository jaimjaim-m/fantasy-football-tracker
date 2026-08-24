import { useEffect, useState } from "react";
import { api } from "../api";
import type { SagarinResponse, TeamRatingsResponse } from "../types";
import { ErrorBox, Loading } from "../components/Layout";

function rankColor(rank: number | null, nTeams: number): string {
  if (!rank) return "#314158";
  const t = (rank - 1) / Math.max(nTeams - 1, 1);
  const r = Math.round(t <= 0.5 ? t * 2 * 255 : 255);
  const g = Math.round(t <= 0.5 ? 255 : (2 - t * 2) * 255);
  return `rgb(${r}, ${g}, 40)`;
}

export function RatingsPage() {
  const [sagarin, setSagarin] = useState<SagarinResponse | null>(null);
  const [season, setSeason] = useState<TeamRatingsResponse | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    Promise.all([
      api<SagarinResponse>("/api/ratings/sagarin"),
      api<TeamRatingsResponse>("/api/ratings/team?scope=season"),
    ])
      .then(([s, t]) => {
        setSagarin(s);
        setSeason(t);
      })
      .catch((err) => setError(err.message));
  }, []);

  if (error) return <ErrorBox message={error} />;
  if (!sagarin || !season) return <Loading />;

  return (
    <>
      <div className="panel">
        <h2>Sagarin power ratings</h2>
        <p className="muted">100 ≈ average. SOS is the average rating of opponents faced.</p>
        <table>
          <thead>
            <tr>
              <th>Rank</th>
              <th>Team</th>
              <th>Rating</th>
              <th>All-play</th>
              <th>Avg</th>
              <th>SOS</th>
              <th>Actual</th>
            </tr>
          </thead>
          <tbody>
            {sagarin.rows.map((row) => (
              <tr key={row.team_id}>
                <td>{row.rank}</td>
                <td>{row.team_name}</td>
                <td>{row.sagarin_rating.toFixed(1)}</td>
                <td>{row.hypothetical_record}</td>
                <td>{row.avg_score.toFixed(1)}</td>
                <td>{row.strength_of_schedule.toFixed(1)}</td>
                <td>{row.actual_record}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="panel">
        <h2>Weekly rank heatmap</h2>
        <div className="heatmap" style={{ ["--weeks" as string]: sagarin.weeks.length }}>
          <div className="heatmap-row">
            <div className="muted">Team</div>
            {sagarin.weeks.map((w) => (
              <div key={w} className="muted" style={{ textAlign: "center" }}>
                W{w}
              </div>
            ))}
          </div>
          {sagarin.heatmap.map((row) => (
            <div className="heatmap-row" key={row.team_id}>
              <div>{row.team_name}</div>
              {row.cells.map((cell) => (
                <div
                  key={cell.week}
                  className="heatmap-cell"
                  style={{ background: rankColor(cell.rank, sagarin.heatmap.length) }}
                  title={cell.score == null ? "—" : `${cell.score.toFixed(1)} pts`}
                >
                  {cell.rank ?? "·"}
                </div>
              ))}
            </div>
          ))}
        </div>
      </div>

      <div className="panel">
        <h2>Season ratings (100 = average)</h2>
        <p className="muted">
          League avg PPG {season.league_avg_ppg.toFixed(1)} · Win% {season.league_avg_win_pct.toFixed(3)}
        </p>
        <table>
          <thead>
            <tr>
              <th>Team</th>
              <th>Overall+</th>
              <th>PPG+</th>
              <th>Win%+</th>
              <th>PPG</th>
              <th>Record</th>
            </tr>
          </thead>
          <tbody>
            {season.rows.map((row) => (
              <tr key={row.name}>
                <td>{row.name}</td>
                <td>{row.overall_rating.toFixed(1)}</td>
                <td>{row.ppg_rating.toFixed(1)}</td>
                <td>{row.win_pct_rating.toFixed(1)}</td>
                <td>{row.ppg.toFixed(1)}</td>
                <td>
                  {row.wins}-{row.losses}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </>
  );
}
