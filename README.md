# ACME Salary Management

Web-based salary management for ACME's HR team — a replacement for
spreadsheet-based compensation tracking across 10,000 employees in 6
countries. Built for the HR Manager persona: browse/search the directory,
review and adjust an individual's compensation with a full history, and
answer org-wide "how do we pay people" questions from a dashboard.

- **Requirements**: [`docs/REQUIREMENTS.md`](docs/REQUIREMENTS.md) — read this first
- **Architecture**: [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)
- **AI usage notes**: [`docs/AI_USAGE.md`](docs/AI_USAGE.md)

## Stack

| Layer    | Choice                                                        |
|----------|-----------------------------------------------------------------|
| Backend  | Python 3.12, FastAPI, SQLAlchemy, SQLite                        |
| Frontend | React 19 + TypeScript, Vite, Tailwind CSS v4, Recharts          |
| Tests    | pytest (backend), 27 tests, isolated in-memory DB per test      |

## Run it — Docker (fastest)

```bash
docker compose up --build
```
- Frontend: http://localhost:3000 (nginx serves the built SPA and proxies `/api` to the backend)
- Backend API + docs: http://localhost:8000/docs
- The backend image seeds 10,000 employees at build time — no extra step needed.

## Run it — locally, without Docker

### Backend
```bash
cd backend
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
python seed.py --count 10000 --reset   # seeds ~10k employees, idempotent with --reset
uvicorn app.main:app --reload --port 8000
```
API now at http://localhost:8000, interactive docs at http://localhost:8000/docs.

### Frontend
```bash
cd frontend
npm install
npm run dev
```
App now at http://localhost:5173, proxying `/api/*` to the backend on `:8000`
(see `frontend/vite.config.ts`).

## Run the tests

```bash
cd backend
source venv/bin/activate
pytest -v
```
27 tests, run in well under a second (isolated in-memory SQLite per test —
no shared state, no sleeps, no network).

## Seed script options

```bash
python seed.py                    # 10,000 employees (default)
python seed.py --count 500        # smaller dataset for quick local testing
python seed.py --reset            # drop & recreate tables first
```
Salaries aren't uniform random — each employee's pay is built from their
country's base band × their job level's multiplier × individual variance, so
the analytics dashboard shows a distribution that actually looks like an
org's real pay structure (see `backend/app/constants.py` and `backend/seed.py`).

## What's in the app

- **Directory** (`/`) — searchable, filterable (department/country/status),
  server-side paginated table of all employees with their current salary.
- **Employee profile** (`/employees/:id`) — full profile + a compensation
  *ledger*: every salary change ever recorded, dated, with a reason. Record a
  new raise/adjustment without ever losing the old figures. Mark an employee
  inactive (soft delete — history is kept).
- **Add employee** (`/employees/new`) — new hire form with a required
  starting salary.
- **Analytics** (`/analytics`) — headcount KPIs, average pay index by
  department, org-wide pay distribution histogram, and breakdowns by country
  and job level. See `docs/REQUIREMENTS.md` and `docs/ARCHITECTURE.md` for
  why department/level figures are a currency-independent "pay index" rather
  than a raw salary average.

## What's deliberately not built, and why

See the "Deliberately Out of Scope" section of
[`docs/REQUIREMENTS.md`](docs/REQUIREMENTS.md) — short version: auth/roles,
FX conversion to one reporting currency, payroll/tax processing, bulk CSV
import, org-chart visualization, and demographic pay-equity analysis were all
excluded on purpose, not by oversight.
