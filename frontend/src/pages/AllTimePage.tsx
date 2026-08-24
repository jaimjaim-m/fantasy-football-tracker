import { useEffect, useState } from "react";
import { api } from "../api";
import type { AllTimeResponse, TeamRatingsResponse } from "../types";
import { ErrorBox, Loading } from "../components/Layout";

export function AllTimePage() {
  const [history, setHistory] = useState<AllTimeResponse | null>(null);
  const [ratings, setRatings] = useState<TeamRatingsResponse | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    Promise.all([
      api<AllTimeResponse>("/api/history/all-time"),
      api<TeamRatingsResponse>("/api/ratings/team?scope=alltime"),
    ])
      .then(([h, r]) => {
        setHistory(h);
        setRatings(r);
      })
      .catch((err) => setError(err.message));
  }, []);

  if (error) return <ErrorBox message={error} />;
  if (!history || !ratings) return <Loading />;

  return (
    <>
      <div className="panel">
        <h2>
          All-time records ({history.start_year}–{history.end_year})
        </h2>
        <table>
          <thead>
            <tr>
              <th>Owner</th>
              <th>Seasons</th>
              <th>W</th>
              <th>L</th>
              <th>Win%</th>
              <th>PF</th>
              <th>PA</th>
              <th>Avg PF</th>
              <th>Avg PA</th>
            </tr>
          </thead>
          <tbody>
            {history.rows.map((row) => (
              <tr key={row.owner_name}>
                <td>{row.owner_name}</td>
                <td>{row.seasons}</td>
                <td>{row.wins}</td>
                <td>{row.losses}</td>
                <td>{row.win_pct.toFixed(3)}</td>
                <td>{row.points_for.toFixed(1)}</td>
                <td>{row.points_against.toFixed(1)}</td>
                <td>{row.avg_pf.toFixed(1)}</td>
                <td>{row.avg_pa.toFixed(1)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="panel">
        <h2>All-time owner ratings</h2>
        <table>
          <thead>
            <tr>
              <th>Owner</th>
              <th>Overall+</th>
              <th>PPG+</th>
              <th>Win%+</th>
              <th>PPG</th>
              <th>Win%</th>
              <th>Record</th>
              <th>Seasons</th>
            </tr>
          </thead>
          <tbody>
            {ratings.rows.map((row) => (
              <tr key={row.name}>
                <td>{row.name}</td>
                <td>{row.overall_rating.toFixed(1)}</td>
                <td>{row.ppg_rating.toFixed(1)}</td>
                <td>{row.win_pct_rating.toFixed(1)}</td>
                <td>{row.ppg.toFixed(1)}</td>
                <td>{row.win_pct.toFixed(3)}</td>
                <td>
                  {row.wins}-{row.losses}
                </td>
                <td>{row.seasons || "—"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </>
  );
}
