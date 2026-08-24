import { FormEvent, useEffect, useState } from "react";
import { Navigate, Route, Routes } from "react-router-dom";
import { api, clearHubPassword, setHubPassword } from "./api";
import { Layout } from "./components/Layout";
import { AllTimePage } from "./pages/AllTimePage";
import { ExportsPage } from "./pages/ExportsPage";
import { MatchupsPage } from "./pages/MatchupsPage";
import { PlayoffsPage } from "./pages/PlayoffsPage";
import { RatingsPage } from "./pages/RatingsPage";
import { StandingsPage } from "./pages/StandingsPage";
import { TeamDetailPage, TeamsPage } from "./pages/TeamsPage";
import type { HealthResponse, LeagueInfo } from "./types";

export default function App() {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [league, setLeague] = useState<LeagueInfo | null>(null);
  const [needsLogin, setNeedsLogin] = useState(false);
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  async function bootstrap() {
    const h = await api<HealthResponse>("/api/health");
    setHealth(h);
    if (h.auth_required) {
      try {
        const info = await api<LeagueInfo>("/api/league");
        setLeague(info);
        setNeedsLogin(false);
      } catch (err) {
        if (err instanceof Error && (err as Error & { status?: number }).status === 401) {
          setNeedsLogin(true);
          return;
        }
        throw err;
      }
    } else {
      setLeague(await api<LeagueInfo>("/api/league"));
    }
  }

  useEffect(() => {
    bootstrap().catch((err) => setError(err.message));
  }, []);

  async function onLogin(event: FormEvent) {
    event.preventDefault();
    setError("");
    try {
      await api("/api/auth/login", { method: "POST", body: JSON.stringify({ password }) });
      setHubPassword(password);
      setNeedsLogin(false);
      setLeague(await api<LeagueInfo>("/api/league"));
    } catch {
      clearHubPassword();
      setError("Incorrect password");
    }
  }

  if (needsLogin) {
    return (
      <form className="panel login" onSubmit={onLogin}>
        <h2>League hub login</h2>
        <p className="muted">Enter the shared password from your commissioner.</p>
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="Hub password"
          autoFocus
        />
        {error ? <p className="error">{error}</p> : null}
        <button type="submit">Enter</button>
      </form>
    );
  }

  if (error && !league) {
    return (
      <div className="app-shell">
        <div className="panel error">{error}</div>
        {health && !health.espn_ok ? (
          <div className="panel muted">
            ESPN auth failed. Update SWID / ESPN_S2 with <code>ff-hub cookies extract</code> or refresh host secrets.
          </div>
        ) : null}
      </div>
    );
  }

  return (
    <Layout league={league}>
      <Routes>
        <Route path="/" element={<StandingsPage />} />
        <Route path="/matchups" element={<MatchupsPage />} />
        <Route path="/teams" element={<TeamsPage />} />
        <Route path="/teams/:teamId" element={<TeamDetailPage />} />
        <Route path="/ratings" element={<RatingsPage />} />
        <Route path="/all-time" element={<AllTimePage />} />
        <Route path="/playoffs" element={<PlayoffsPage />} />
        <Route path="/exports" element={<ExportsPage />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Layout>
  );
}
