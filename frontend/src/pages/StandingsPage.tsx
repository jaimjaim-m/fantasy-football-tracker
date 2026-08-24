import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api";
import type { StandingRow } from "../types";
import { ErrorBox, Loading } from "../components/Layout";

export function StandingsPage() {
  const [rows, setRows] = useState<StandingRow[] | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    api<{ rows: StandingRow[] }>("/api/standings")
      .then((data) => setRows(data.rows))
      .catch((err) => setError(err.message));
  }, []);

  if (error) return <ErrorBox message={error} />;
  if (!rows) return <Loading />;

  return (
    <div className="panel">
      <h2>Standings</h2>
      <p className="muted">Division leaders are seeds 1–2. Yellow / blue / beige / pink bands match last year’s PDF seeding colors.</p>
      <table>
        <thead>
          <tr>
            <th>Seed</th>
            <th>Team</th>
            <th>Div</th>
            <th>Record</th>
            <th>H2H</th>
            <th>Top6</th>
            <th>Total</th>
            <th>PF</th>
            <th>PA</th>
            <th>Streak</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((row) => (
            <tr key={row.team_id} className={`band-${row.band}`}>
              <td>{row.seed}</td>
              <td>
                <Link to={`/teams/${row.team_id}`}>{row.team_name}</Link>
              </td>
              <td>{row.division}</td>
              <td>{row.record}</td>
              <td>{row.h2h_points}</td>
              <td>{row.top6_points}</td>
              <td>{row.total_points}</td>
              <td>{row.points_for.toFixed(1)}</td>
              <td>{row.points_against.toFixed(1)}</td>
              <td>{row.streak}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
