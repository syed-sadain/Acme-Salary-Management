# Deployment Guide

The brief asks for **"fully functional deployed software."** This document
records how to take the repo from "runs locally" to "public URL a reviewer can
open," including the choices and caveats.

## TL;DR — the recommended live setup (Vercel + Render)

| Piece | Host | Why |
|-------|------|-----|
| Frontend (React SPA) | **Vercel** | Static build; Vercel's sweet spot |
| Backend (FastAPI) | **Render** or **Railway** | Needs a long-running process + a writable disk for SQLite |

> **Why not the backend on Vercel?** Vercel runs serverless functions on an
> ephemeral, read-only filesystem. This backend is a persistent Uvicorn process
> whose data is a SQLite *file* (`sqlite:///./acme_salary.db`). On Vercel that
> file would be wiped on every cold start — so the 10,000 seed rows wouldn't
> exist at request time. Use Vercel for the frontend and a container host for
> the backend. (The frontend is 100% Vercel-native; only the backend isn't.)

### Step 1 — Deploy the backend (Render, one click)

1. Render Dashboard → **New → Blueprint** → select this repo. Render reads
   [`render.yaml`](../render.yaml), which:
   - installs `backend/requirements.txt`,
   - runs `python seed.py --count 10000 --reset`,
   - starts `uvicorn app.main:app --host 0.0.0.0 --port $PORT`,
   - mounts a **1 GB persistent disk** at `/var/data` and points
     `DATABASE_URL` at `sqlite:////var/data/acme_salary.db` so data survives
     restarts.
2. Note the public URL, e.g. `https://acme-salary-api.onrender.com`.
3. Verify: `GET https://acme-salary-api.onrender.com/api/health` → `{"status":"ok"}`.

*(Railway instead? Same idea — set the **root directory** to `backend`, the
start command from `backend/Procfile`, add a persistent volume, and set
`DATABASE_URL` to a path on that volume.)*

### Step 2 — Point the frontend at the backend
Open [`frontend/vercel.json`](../frontend/vercel.json) and replace the
placeholder in the `/api/(.*)` rewrite with your backend URL from Step 1:

```json
{ "source": "/api/(.*)", "destination": "https://acme-salary-api.onrender.com/api/$1" }
```

(Alternatively, skip the rewrite and set the Vercel env var
`VITE_API_BASE_URL=https://acme-salary-api.onrender.com/api` — `src/api/client.ts`
reads it at build time and falls back to the relative `/api` path otherwise.)

### Step 3 — Deploy the frontend on Vercel
1. Vercel → **Add New → Project** → import this repo.
2. **Root Directory**: `frontend`  ← important
3. Framework preset auto-detects **Vite**: build `npm run build`, output `dist`.
4. Deploy. You get a live URL like `https://acme-salary-management.vercel.app`.

The bundled [`frontend/vercel.json`](../frontend/vercel.json) also adds the SPA
fallback rewrite so client-side routes (`/employees/42`, `/analytics`) work on
hard refresh instead of 404-ing — a step people usually forget.

### Step 4 — Verify the deployed app
- [ ] Open the Vercel URL → Directory loads ~10,000 records across pages
- [ ] Search + department/country/status filters narrow results (server-side)
- [ ] Open a profile → "Record a change" appends a new ledger row (history kept)
- [ ] `/analytics` renders KPIs + both charts
- [ ] Hard-refresh a deep link like `/employees/42` → still works (SPA fallback)

## Option A — single host with Docker (fastest, one URL)

Everything is already wired: `docker-compose.yml` builds the backend and the
frontend (nginx serves the built SPA and reverse-proxies `/api/*` to the
backend). The backend image seeds 10,000 employees at build time.

```bash
docker compose up --build
# Frontend:      http://localhost:3000
# Backend docs:  http://localhost:8000/docs
```

To put this on the public internet, any container host works (a small VM with
Docker, Fly.io, Railway, Render "Docker" service). The only change needed is to
publish the ports the host expects and, if the platform terminates TLS, leave
the internal setup as-is — nginx already proxies `/api` so the SPA makes
relative calls and needs no build-time API URL.

## Option B — split hosting (frontend on Vercel/Netlify, backend on Render/Fly)

More representative of a real setup, and what I'd do for a longer-lived demo.

1. **Backend** (Render Web Service / Fly.io):
   - Build from `backend/` using its `Dockerfile` (or `pip install -r
     requirements.txt` + `uvicorn app.main:app --host 0.0.0.0 --port $PORT`).
   - Run `python seed.py --count 10000 --reset` once (build step or a one-off
     job) so the deployed DB has data. Note the SQLite file must live on a
     persistent volume, or the seed must re-run on each deploy — SQLite on an
     ephemeral filesystem loses data between restarts. This is the one real
     operational wrinkle of choosing SQLite (documented in
     `ARCHITECTURE.md`); at "real deployment" scale the answer is Postgres.
   - Note the public URL, e.g. `https://acme-salary-api.onrender.com`.

2. **Frontend** (Vercel/Netlify): deploy `frontend/` as a static site (`npm run
   build` → `dist/`). Because the SPA calls relative `/api/*` paths, point a
   rewrite/proxy at the backend URL:
   - Vercel: `vercel.json` → `{ "rewrites": [{ "source": "/api/(.*)",
     "destination": "https://acme-salary-api.onrender.com/api/$1" }] }`
   - Netlify: `_redirects` → `/api/*  https://acme-salary-api.onrender.com/api/:splat  200`
   - (Alternatively, set `VITE_API_BASE_URL` and read it in `api/client.ts`;
     the relative-path proxy avoids that build-time coupling.)

## What is *not* included, and why

- **Auth**: the brief is a single HR-Manager persona; adding auth would be
  boilerplate that doesn't demonstrate the modeling being assessed. It is
  named in `REQUIREMENTS.md` as the first thing to add before any real
  deployment — and a public URL is exactly the "real deployment" that would
  require it. For a take-home demo link, the reviewer is the trusted user.
- **Managed Postgres / migrations**: SQLite + `create_all` is sufficient for a
  v1 system of record. A production rollout would add Alembic and Postgres
  (see the migration path in `ARCHITECTURE.md`).

## Verification checklist for the deployed instance

- [ ] `GET <backend>/api/health` returns `{"status":"ok"}`
- [ ] `<frontend>/` loads the Directory and shows ~10,000 records across pages
- [ ] Search + department/country/status filters narrow results (server-side)
- [ ] Open a profile → "Record a change" adds a new ledger row (history kept)
- [ ] `/analytics` renders KPIs + both charts
