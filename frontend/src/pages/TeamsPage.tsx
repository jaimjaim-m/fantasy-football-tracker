import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api } from "../api";
import type { TeamSummary } from "../types";
import { ErrorBox, Loading } from "../components/Layout";

export function TeamsPage() {
  const [teams, setTeams] = useState<TeamSummary[] | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    api<{ teams: TeamSummary[] }>("/api/teams")
      .then((data) => setTeams(data.teams))
      .catch((err) => setError(err.message));
  }, []);

  if (error) return <ErrorBox message={error} />;
  if (!teams) return <Loading />;

  return (
    <div className="panel">
      <h2>Teams</h2>
      <table>
        <thead>
          <tr>
            <th>Team</th>
            <th>Owner</th>
            <th>Record</th>
            <th>Avg</th>
            <th>High</th>
            <th>Low</th>
            <th>PF</th>
          </tr>
        </thead>
        <tbody>
          {teams.map((team) => (
            <tr key={team.team_id}>
              <td>
                <Link to={`/teams/${team.team_id}`}>{team.team_name}</Link>
              </td>
              <td>{team.owner_name || "—"}</td>
              <td>
                {team.wins}-{team.losses}
              </td>
              <td>{team.avg_points.toFixed(1)}</td>
              <td>{team.highest_score.toFixed(1)}</td>
              <td>{team.lowest_score.toFixed(1)}</td>
              <td>{team.points_for.toFixed(1)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export function TeamDetailPage() {
  const { teamId } = useParams();
  const [team, setTeam] = useState<TeamSummary | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!teamId) return;
    api<TeamSummary>(`/api/teams/${teamId}`)
      .then(setTeam)
      .catch((err) => setError(err.message));
  }, [teamId]);

  if (error) return <ErrorBox message={error} />;
  if (!team) return <Loading />;

  return (
    <>
      <div className="panel">
        <h2>{team.team_name}</h2>
        <p className="muted">
          {team.owner_name || "Unknown owner"} · {team.division} · {team.wins}-{team.losses}
        </p>
        <table>
          <thead>
            <tr>
              <th>PF</th>
              <th>PA</th>
              <th>Avg</th>
              <th>High</th>
              <th>Low</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>{team.points_for.toFixed(1)}</td>
              <td>{team.points_against.toFixed(1)}</td>
              <td>{team.avg_points.toFixed(1)}</td>
              <td>{team.highest_score.toFixed(1)}</td>
              <td>{team.lowest_score.toFixed(1)}</td>
            </tr>
          </tbody>
        </table>
      </div>
      <div className="panel">
        <h2>Weekly scores</h2>
        <table>
          <thead>
            <tr>
              <th>Week</th>
              <th>Score</th>
            </tr>
          </thead>
          <tbody>
            {team.weekly_scores.map((w) => (
              <tr key={w.week}>
                <td>{w.week}</td>
                <td>{w.score == null ? "—" : w.score.toFixed(1)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {team.roster.length > 0 && (
        <div className="panel">
          <h2>Roster</h2>
          <table>
            <thead>
              <tr>
                <th>Player</th>
                <th>Pos</th>
                <th>Slot</th>
                <th>Pts</th>
                <th>Proj</th>
              </tr>
            </thead>
            <tbody>
              {team.roster.map((p, idx) => (
                <tr key={`${p.name}-${idx}`}>
                  <td>
                    {p.name}
                    {p.injured ? " ⚠" : ""}
                  </td>
                  <td>{p.position || "—"}</td>
                  <td>{p.slot || "—"}</td>
                  <td>{p.points == null ? "—" : p.points.toFixed(1)}</td>
                  <td>{p.projected == null ? "—" : p.projected.toFixed(1)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </>
  );
}
