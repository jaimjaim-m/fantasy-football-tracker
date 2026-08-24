# Fantasy League Hub

Cloud-friendly rewrite of the 2025 ESPN fantasy tracker: authenticate to ESPN once as the commissioner, serve a mobile-friendly dashboard and PDF exports for the whole league.

## Features

- ESPN private-league auth via `SWID` + `espn_s2` cookies ([espn-api](https://github.com/cwendt94/espn-api))
- Custom scoring: **2 pts per H2H win + 1 pt for a top-6 weekly score**
- Division winners locked into seeds **1–2**
- Standings, matchups, team pages, Sagarin ratings + heatmap, season/all-time ratings, all-time owner records, playoff bracket
- Structured JSON under `/api/*` and PDF downloads under `/api/export/pdf/{weekly|alltime|sagarin|playoffs}`
- Optional shared `HUB_PASSWORD` so a public URL is not fully open

## Quick start (local)

Requires **Python 3.9+** (3.11+ preferred) and **Node 20+** for the frontend.

```bash
cp .env.example .env
# Paste LEAGUE_ID, YEAR, SWID, ESPN_S2 into .env
# Tip: copy cookies from last year’s tracker, then refresh if validate fails:
#   ff-hub cookies extract

cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -e .

# Validate ESPN cookies
ff-hub cookies validate

uvicorn app.main:app --reload --port 8000
```

In another terminal:

```bash
cd frontend
npm install
npm run dev
```

Open http://127.0.0.1:5173 (Vite proxies `/api` to the backend). For a production-style single process after `npm run build`, open http://127.0.0.1:8000 — FastAPI serves the built UI from `frontend/dist`.

## Cookie management

ESPN cookies expire periodically. On a cloud host there is no Chrome session, so refreshing is a commissioner task:

1. Locally run `ff-hub cookies extract` (or copy cookies from browser DevTools → Application → Cookies → `fantasy.espn.com`)
2. Update `.env` locally and re-test with `ff-hub cookies validate`
3. Update the same values as secrets on Railway / Fly and redeploy (or restart)

## Deploy (Railway / Fly)

Build with the included `Dockerfile` (builds the React UI, then serves it from FastAPI).

Set these environment variables / secrets:

| Variable | Required | Notes |
|----------|----------|-------|
| `LEAGUE_ID` | yes | From your ESPN league URL |
| `YEAR` | yes | Season year |
| `SWID` | yes | ESPN cookie |
| `ESPN_S2` | yes | ESPN cookie (often URL-encoded) |
| `HUB_PASSWORD` | recommended | Shared league password |
| `CACHE_TTL_SECONDS` | no | Default `180` |
| `HISTORY_START_YEAR` | no | Default `2016` |
| `PLAYOFF_TEAMS` | no | Default `6` |

Expose port `8000`. Members open the public URL, enter `HUB_PASSWORD` if set, and never need ESPN logins.

### Railway

1. Create a new project from this repo
2. Add the secrets above
3. Deploy the Dockerfile (Railway detects it automatically)
4. Share the generated URL with the league

### Fly.io

```bash
fly launch --dockerfile Dockerfile
fly secrets set LEAGUE_ID=... YEAR=2026 SWID=... ESPN_S2=... HUB_PASSWORD=...
fly deploy
```

## API overview

- `GET /api/health` — app + ESPN cookie status (no hub password required)
- `POST /api/auth/login` — `{ "password": "..." }`
- `GET /api/league|standings|matchups|teams|weekly-leaders|playoffs|week-status`
- `GET /api/ratings/sagarin` · `GET /api/ratings/team?scope=season|alltime`
- `GET /api/history/all-time?start=&end=`
- `GET /api/export/pdf/{weekly|alltime|sagarin|playoffs}`

## Project layout

```
backend/app/          FastAPI, ESPN client, domain logic, PDF exporters, CLI
frontend/             Vite + React dashboard
Dockerfile            Multi-stage production image
.env.example          Config template
```

Previous season scripts remain in `~/Documents/fantasy_football_tracker` for reference; this repo is a clean rewrite.
