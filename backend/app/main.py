from __future__ import annotations

from typing import Optional

from functools import lru_cache
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from app.auth_hub import require_hub, set_auth_cookie
from app.config import Settings, get_settings
from app.domain import (
    build_all_time,
    build_all_time_ratings,
    build_matchups,
    build_playoffs,
    build_standings,
    build_team,
    build_teams,
    build_weekly_leaders,
    calculate_sagarin,
    season_team_ratings,
    week_status,
)
from app.espn.client import ESPNAccessError, LeagueClient
from app.exporters import pdf as pdf_export
from app.schemas.models import HealthResponse, LeagueInfo

app = FastAPI(title="ff-league-hub", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def settings() -> Settings:
    return get_settings()


@lru_cache
def client() -> LeagueClient:
    return LeagueClient(settings())


@app.middleware("http")
async def hub_auth_middleware(request: Request, call_next):
    try:
        require_hub(
            request,
            settings(),
            x_hub_password=request.headers.get("X-Hub-Password"),
            ff_hub_auth=request.cookies.get("ff_hub_auth"),
        )
    except HTTPException as exc:
        return JSONResponse({"detail": exc.detail}, status_code=exc.status_code)
    return await call_next(request)


class LoginBody(BaseModel):
    password: str


@app.post("/api/auth/login")
def login(body: LoginBody, response: Response):
    cfg = settings()
    if cfg.hub_password and body.password != cfg.hub_password:
        raise HTTPException(status_code=401, detail="Invalid password")
    if cfg.hub_password:
        set_auth_cookie(response, body.password)
    return {"ok": True}


@app.post("/api/auth/logout")
def logout(response: Response):
    response.delete_cookie("ff_hub_auth")
    return {"ok": True}


@app.get("/api/health", response_model=HealthResponse)
def health():
    cfg = settings()
    espn_ok, message = client().validate()
    return HealthResponse(
        ok=True,
        espn_ok=espn_ok,
        message=message,
        auth_required=bool(cfg.hub_password),
        demo_mode=cfg.demo_mode,
    )


def _league_info(league) -> LeagueInfo:
    cfg = settings()
    summary = (
        f"{cfg.h2h_win_points} pts per H2H win + {cfg.top_n_points} pt for a top-{cfg.top_n_bonus} "
        f"weekly score. Division winners lock seeds 1–2."
    )
    if cfg.demo_mode:
        summary = f"DEMO MODE (sample data) · {summary}"
    return LeagueInfo(
        name=league.settings.name,
        year=league.year,
        current_week=league.current_week,
        nfl_week=getattr(league, "nfl_week", None),
        team_count=len(league.teams),
        playoff_teams=cfg.playoff_teams,
        scoring_summary=summary,
    )


@app.get("/api/league", response_model=LeagueInfo)
def league_info():
    try:
        return _league_info(client().get_league())
    except ESPNAccessError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@app.get("/api/standings")
def standings():
    try:
        return build_standings(client().get_league(), settings())
    except ESPNAccessError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@app.get("/api/matchups")
def matchups(week: Optional[int] = Query(default=None)):
    try:
        return build_matchups(client().get_league(), week=week, settings=settings())
    except ESPNAccessError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@app.get("/api/teams")
def teams():
    try:
        return build_teams(client().get_league())
    except ESPNAccessError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@app.get("/api/teams/{team_id}")
def team_detail(team_id: int):
    try:
        team = build_team(client().get_league(), team_id)
    except ESPNAccessError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    if team is None:
        raise HTTPException(status_code=404, detail="Team not found")
    return team


@app.get("/api/weekly-leaders")
def weekly_leaders():
    try:
        return build_weekly_leaders(client().get_league())
    except ESPNAccessError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@app.get("/api/ratings/sagarin")
def ratings_sagarin():
    try:
        return calculate_sagarin(client().get_league())
    except ESPNAccessError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@app.get("/api/ratings/team")
def ratings_team(scope: str = Query(default="season")):
    try:
        league = client().get_league()
        if scope == "alltime":
            cfg = settings()
            return build_all_time_ratings(client(), cfg.history_start_year, cfg.year)
        return season_team_ratings(league)
    except ESPNAccessError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@app.get("/api/history/all-time")
def history_all_time(
    start: Optional[int] = Query(default=None),
    end: Optional[int] = Query(default=None),
):
    cfg = settings()
    start_year = start or cfg.history_start_year
    end_year = end or cfg.year
    try:
        return build_all_time(client(), start_year, end_year)
    except ESPNAccessError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@app.get("/api/playoffs")
def playoffs():
    try:
        return build_playoffs(client().get_league(), settings())
    except ESPNAccessError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@app.get("/api/week-status")
def week_status_endpoint(week: Optional[int] = Query(default=None)):
    try:
        return week_status(client().get_league(), week=week)
    except ESPNAccessError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@app.get("/api/export/pdf/{report}")
def export_pdf(report: str):
    cfg = settings()
    try:
        league_obj = client().get_league()
        info = _league_info(league_obj)
        if report == "weekly":
            payload = pdf_export.weekly_pdf(
                info,
                build_standings(league_obj, cfg),
                build_matchups(league_obj, settings=cfg),
                build_teams(league_obj),
                build_weekly_leaders(league_obj),
                season_team_ratings(league_obj),
            )
            filename = "weekly_report.pdf"
        elif report == "alltime":
            history = build_all_time(client(), cfg.history_start_year, cfg.year)
            ratings = build_all_time_ratings(client(), cfg.history_start_year, cfg.year)
            payload = pdf_export.alltime_pdf(history, ratings)
            filename = "alltime_report.pdf"
        elif report == "sagarin":
            payload = pdf_export.sagarin_pdf(info, calculate_sagarin(league_obj))
            filename = "sagarin_report.pdf"
        elif report == "playoffs":
            payload = pdf_export.playoffs_pdf(info, build_playoffs(league_obj, cfg))
            filename = "playoff_report.pdf"
        else:
            raise HTTPException(status_code=404, detail="Unknown report. Use weekly|alltime|sagarin|playoffs")
    except ESPNAccessError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    return StreamingResponse(
        iter([payload]),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


def _mount_frontend() -> None:
    candidate = settings().resolved_static_dir
    if not (candidate.is_dir() and (candidate / "index.html").exists()):
        return
    assets = candidate / "assets"
    if assets.is_dir():
        app.mount("/assets", StaticFiles(directory=assets), name="assets")

    @app.get("/{full_path:path}")
    async def spa(full_path: str, directory: Path = candidate):
        if full_path.startswith("api/"):
            raise HTTPException(status_code=404, detail="Not found")
        file_path = directory / full_path
        if full_path and file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(directory / "index.html")


_mount_frontend()
