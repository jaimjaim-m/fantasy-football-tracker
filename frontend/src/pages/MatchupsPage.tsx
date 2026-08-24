import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api";
import type { MatchupsResponse } from "../types";
import { ErrorBox, Loading } from "../components/Layout";

export function MatchupsPage() {
  const [data, setData] = useState<MatchupsResponse | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    api<MatchupsResponse>("/api/matchups")
      .then(setData)
      .catch((err) => setError(err.message));
  }, []);

  if (error) return <ErrorBox message={error} />;
  if (!data) return <Loading />;

  return (
    <div className="panel">
      <h2>Week {data.week} matchups</h2>
      <p className="muted">★ marks a top-{data.top_n} weekly score (bonus point).</p>
      <div className="scoreboard">
        {data.matchups.map((m, idx) => (
          <div className="matchup" key={idx}>
            <div className="side">
              <Link to={`/teams/${m.home.team_id}`}>
                {m.home.team_name}
                {m.home.top_n ? <span className="badge">TOP {data.top_n}</span> : null}
              </Link>
              <div className="score">{m.home.score == null ? "—" : m.home.score.toFixed(1)}</div>
            </div>
            <div className="muted">vs</div>
            <div className="side away">
              {m.away ? (
                <>
                  <Link to={`/teams/${m.away.team_id}`}>
                    {m.away.team_name}
                    {m.away.top_n ? <span className="badge">TOP {data.top_n}</span> : null}
                  </Link>
                  <div className="score">{m.away.score == null ? "—" : m.away.score.toFixed(1)}</div>
                </>
              ) : (
                <div>BYE</div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
