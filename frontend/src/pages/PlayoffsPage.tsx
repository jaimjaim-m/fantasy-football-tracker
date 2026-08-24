import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api";
import type { PlayoffsResponse } from "../types";
import { ErrorBox, Loading } from "../components/Layout";

export function PlayoffsPage() {
  const [data, setData] = useState<PlayoffsResponse | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    api<PlayoffsResponse>("/api/playoffs")
      .then(setData)
      .catch((err) => setError(err.message));
  }, []);

  if (error) return <ErrorBox message={error} />;
  if (!data) return <Loading />;

  return (
    <>
      <div className="panel">
        <h2>If playoffs started today</h2>
        <p className="muted">Based on current custom standings through week {data.current_week}.</p>
        <h3>Wild card</h3>
        <table>
          <thead>
            <tr>
              <th>Match</th>
              <th>Teams</th>
            </tr>
          </thead>
          <tbody>
            {data.wild_card.map((m) => (
              <tr key={m.label}>
                <td>{m.label}</td>
                <td>
                  {m.seed1}) {m.team1}
                  {m.team2 ? ` vs ${m.seed2}) ${m.team2}` : ""}
                  {m.note ? ` — ${m.note}` : ""}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        <h3>Semifinals</h3>
        <table>
          <thead>
            <tr>
              <th>Match</th>
              <th>Detail</th>
            </tr>
          </thead>
          <tbody>
            {data.semifinals.map((m) => (
              <tr key={m.label}>
                <td>{m.label}</td>
                <td>
                  {m.seed1}) {m.team1} {m.note || ""}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        <h3>Championship</h3>
        <p>
          {data.championship.team1} vs {data.championship.team2}
        </p>
      </div>

      <div className="panel">
        <h2>Playoff profiles</h2>
        <table>
          <thead>
            <tr>
              <th>Seed</th>
              <th>Team</th>
              <th>Record</th>
              <th>PF</th>
              <th>Avg</th>
              <th>Recent</th>
            </tr>
          </thead>
          <tbody>
            {data.profiles.map((p) => (
              <tr key={p.team_id}>
                <td>{p.seed}</td>
                <td>
                  <Link to={`/teams/${p.team_id}`}>{p.team_name}</Link>
                </td>
                <td>{p.record}</td>
                <td>{p.points_for.toFixed(1)}</td>
                <td>{p.avg_score.toFixed(1)}</td>
                <td>{p.recent_form.map((s) => s.toFixed(1)).join(", ") || "—"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {data.head_to_head.length > 0 && (
        <div className="panel">
          <h2>Head-to-head among playoff teams</h2>
          <table>
            <thead>
              <tr>
                <th>Team 1</th>
                <th>Team 2</th>
                <th>Record</th>
              </tr>
            </thead>
            <tbody>
              {data.head_to_head.map((h, idx) => (
                <tr key={idx}>
                  <td>{h.team1}</td>
                  <td>{h.team2}</td>
                  <td>
                    {h.wins}-{h.losses}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </>
  );
}
