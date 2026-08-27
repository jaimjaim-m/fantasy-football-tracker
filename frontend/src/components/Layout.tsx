import React from "react";
import { NavLink } from "react-router-dom";
import type { LeagueInfo } from "../types";

export function Layout({
  league,
  demoMode = false,
  children,
}: {
  league: LeagueInfo | null;
  demoMode?: boolean;
  children: React.ReactNode;
}) {
  const links = [
    ["/", "Standings"],
    ["/matchups", "Matchups"],
    ["/teams", "Teams"],
    ["/ratings", "Ratings"],
    ["/all-time", "All-time"],
    ["/playoffs", "Playoffs"],
    ["/exports", "Exports"],
  ] as const;

  return (
    <div className="app-shell">
      <header className="topbar">
        <div className="brand">
          <h1>
            {league?.name || "Fantasy League Hub"}
            {demoMode ? <span className="demo-pill">Demo</span> : null}
          </h1>
          <p>
            {league
              ? `${league.year} · Week ${league.current_week} · ${league.scoring_summary}`
              : "Loading league…"}
          </p>
        </div>
        <nav className="nav">
          {links.map(([to, label]) => (
            <NavLink key={to} to={to} end={to === "/"} className={({ isActive }) => (isActive ? "active" : "")}>
              {label}
            </NavLink>
          ))}
        </nav>
      </header>
      {children}
    </div>
  );
}

export function Loading() {
  return <div className="panel muted">Loading…</div>;
}

export function ErrorBox({ message }: { message: string }) {
  return <div className="panel error">{message}</div>;
}
