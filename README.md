# ACME Salary Management
**A web-based compensation system of record for ACME's global HR team — replacing spreadsheets for 10,000 employees across 6 countries.**

Built for the HR Manager persona: browse and search the directory, review and adjust individual compensation with a full audit trail, and answer org-wide "how do we pay people" questions from a live dashboard.

<p align="center">
 <a href="https://fastapi.tiangolo.com/"><img alt="Backend: FastAPI" src="https://img.shields.io/badge/backend-FastAPI-009688?logo=fastapi&logoColor=white"></a>
 <a href="https://www.python.org/"><img alt="Python 3.12" src="https://img.shields.io/badge/python-3.12-3776AB?logo=python&logoColor=white"></a>
 <a href="https://www.sqlalchemy.org/"><img alt="SQLAlchemy" src="https://img.shields.io/badge/ORM-SQLAlchemy-D71F00"></a>
 <a href="https://www.sqlite.org/"><img alt="Database: SQLite" src="https://img.shields.io/badge/database-SQLite-003B57?logo=sqlite&logoColor=white"></a>
 <br>
 <a href="https://react.dev/"><img alt="React 19" src="https://img.shields.io/badge/React-19-61DAFB?logo=react&logoColor=black"></a>
 <a href="https://www.typescriptlang.org/"><img alt="TypeScript" src="https://img.shields.io/badge/TypeScript-5-3178C6?logo=typescript&logoColor=white"></a>
 <a href="https://vitejs.dev/"><img alt="Vite" src="https://img.shields.io/badge/Vite-8-646CFF?logo=vite&logoColor=white"></a>
 <a href="https://tailwindcss.com/"><img alt="Tailwind CSS v4" src="https://img.shields.io/badge/Tailwind_CSS-v4-06B6D4?logo=tailwindcss&logoColor=white"></a>
 <br>
 <a href="https://pytest.org/"><img alt="Tests: 27 passing" src="https://img.shields.io/badge/tests-27_passing-4C9A2A?logo=pytest&logoColor=white"></a>
 <a href="docker-compose.yml"><img alt="Docker Compose" src="https://img.shields.io/badge/docker-compose-2496ED?logo=docker&logoColor=white"></a>
 <a href="docs/REQUIREMENTS.md"><img alt="Docs" src="https://img.shields.io/badge/docs-requirements%20%7C%20architecture-informational"></a>
 <img alt="License: MIT" src="https://img.shields.io/badge/license-MIT-lightgrey">
</p>

---

## Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Getting Started](#getting-started)
  - [Option A — Docker (one command)](#option-a--docker-one-command)
  - [Option B — Local, without Docker](#option-b--local-without-docker)
- [Project Structure](#project-structure)
- [API Reference](#api-reference)
- [Data Model](#data-model)
- [Testing](#testing)
- [Seed Data](#seed-data)
- [Performance](#performance)
- [Design Decisions](#design-decisions)
- [Deliberately Out of Scope](#deliberately-out-of-scope)
- [Documentation](#documentation)

---

## Overview
ACME's HR team currently manages salary data for 10,000 employees across 6 countries in spreadsheets — slow, error-prone, and impossible to query. This project replaces that with an API-first web application that gives the HR Manager two things spreadsheets can't:

1. **A trustworthy system of record** — every salary change is an immutable, dated ledger entry with a reason. Compensation history is never overwritten.
2. **Answers about pay** — an analytics dashboard that slices headcount and pay by department, country, and job level, without exporting to Excel.

> **Why this matters:** the core design decision is that an employee has *no* `salary` column. "Give a raise" is an `INSERT`, not an `UPDATE` — so the system can always reconstruct who was paid what, when, and why.

## Features
| Area | Capability |
|---|---|
| **Directory** | Search by name/email/ID, filter by department, country, and status; server-side paginated over 10,000 rows with no lag |
| **Employee profile** | Full employment details plus a **compensation ledger** — every salary record ever created, dated, with a reason |
| **Record a change** | Raises and adjustments are appended as new dated records; history is preserved by construction |
| **Add / deactivate** | New-hire form with a required starting salary; deactivation is a **soft delete** so history survives offboarding |
| **Analytics** | Headcount KPIs, average pay index by department, org-wide pay distribution histogram, and breakdowns by country and job level |

## Tech Stack
| Layer | Technology |
|---|---|
| **Backend** | Python 3.12 · FastAPI · SQLAlchemy 2.0 · Pydantic v2 · Uvicorn |
| **Database** | SQLite (file-backed, zero-ops) |
| **Frontend** | React 19 · TypeScript · Vite · Tailwind CSS v4 · React Router · Recharts |
| **Testing** | pytest — 27 tests, isolated in-memory SQLite per test |
| **Packaging** | Docker · Docker Compose · nginx |

## Getting Started
### Option A — Docker (one command)

```bash
docker compose up --build
```

| Service | URL |
|---|---|
| Frontend (SPA) | http://localhost:3000 |
| Backend API docs | http://localhost:8000/docs |

The backend image **seeds 10,000 employees at build time**, so the container is immediately demo-able with no extra steps. See [`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md) for deploying to a public URL.

### Option B — Local, without Docker
**Backend**

```bash
cd backend
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
python seed.py --count 10000 --reset
uvicorn app.main:app --reload --port 8000
```

→ API at http://localhost:8000 · interactive docs at http://localhost:8000/docs
**Frontend**

```bash
cd frontend
npm install
npm run dev
```

→ App at http://localhost:5173 (Vite proxies `/api/*` to the backend on `:8000`)

## Project Structure
```
acme-salary-mgmt/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI app, CORS, router registration
│   │   ├── models.py        # SQLAlchemy ORM tables
│   │   ├── schemas.py       # Pydantic request/response contracts
│   │   ├── crud.py          # All business logic & SQL (pure, testable)
│   │   ├── constants.py     # Country pay bands, departments, job levels
│   │   ├── database.py      # Engine & session management
│   │   └── routers/         # employees.py, analytics.py — HTTP layer only
│   ├── tests/               # 27 pytest tests (isolated in-memory DB each)
│   ├── seed.py              # 10,000-employee seeder
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── api/client.ts    # Typed fetch functions, one per endpoint
│   │   ├── types.ts         # TS types mirroring backend schemas
│   │   ├── lib/format.ts    # Currency & date formatting
│   │   ├── components/      # Layout, StatusBadge
│   │   ├── pages/           # Directory, EmployeeDetail, AddEmployee, Analytics
│   │   └── index.css        # Tailwind v4 @theme design tokens
│   └── Dockerfile
├── docs/
│   ├── REQUIREMENTS.md      # Goal, scope, deliberate non-goals
│   ├── ARCHITECTURE.md      # System design & trade-offs
│   ├── DEPLOYMENT.md        # How to ship it to a public URL
│   └── AI_USAGE.md          # How AI tools were used (and checked)
├── docker-compose.yml
└── README.md
```

**Backend layering** — `routers/` handles HTTP only → `crud.py` holds every query and business rule as pure functions taking a `Session` → `models.py` and `schemas.py` define storage and wire contracts independently, so the API can evolve without a migration and vice versa.

## API Reference
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health` | Liveness check |
| `GET` | `/api/employees` | Paginated, searchable, filterable directory |
| `POST` | `/api/employees` | Create an employee with an initial salary record |
| `GET` | `/api/employees/{id}` | Full profile + complete salary history |
| `DELETE` | `/api/employees/{id}` | Soft delete (marks inactive, keeps history) |
| `POST` | `/api/employees/{id}/salary-records` | Append a salary change |
| `GET` | `/api/reference-data` | Departments, countries, job levels |
| `GET` | `/api/analytics/summary` | Org-wide compensation aggregates |

Full interactive schema: **http://localhost:8000/docs** (auto-generated by FastAPI).

## Data Model
```
┌──────────────────────┐          ┌───────────────────────────┐
│      Employee        │ 1      N │       SalaryRecord        │
│──────────────────────│──────────│───────────────────────────│
│ id                   │          │ id                        │
│ first_name           │          │ employee_id  (FK)         │
│ last_name            │          │ base_salary               │
│ email                │          │ currency                  │
│ department   (idx)   │          │ bonus_target_pct          │
│ job_title            │          │ effective_date            │
│ job_level    (idx)   │          │ reason                    │
│ country      (idx)   │          └───────────────────────────┘
│ hire_date            │           append-only · never updated
│ status       (idx)   │
│ manager_id           │           "Current salary" = the record
└──────────────────────┘           with the latest effective_date
```

## Testing
```bash
cd backend
source venv/bin/activate
pytest -v
```

**27 tests, all passing**, in well under a second. Each test runs against an isolated in-memory SQLite database via a pytest fixture — no shared state, no sleeps, no network. Coverage spans:

- Employee CRUD and soft-delete semantics
- The append-only salary-history contract (raises never mutate prior records)
- Pagination, filtering, and search correctness
- Analytics aggregation — including a regression test that cross-currency groups are **never naively averaged**

## Seed Data
```bash
python seed.py                    # 10,000 employees (default)
python seed.py --count 500        # smaller set for fast local testing
python seed.py --reset            # drop & recreate tables first
```

Salaries are **not uniformly random**: each employee's pay is built from their country's base band × their job level's multiplier × individual variance, so the analytics show a distribution that actually resembles an org's pay structure. See `backend/app/constants.py`.

## Performance

The brief's one hard constraint — 10,000 employees — is treated as a real requirement:

- **No N+1 queries.** `crud.list_employees` resolves each employee's current salary in a single query (correlated subquery for "latest record per employee", joined once).
- **Filtering and pagination happen in SQL**, never in Python after loading everything.
- **Indexed access patterns:** `department`, `country`, `job_level`, `status` on `Employee`; `(employee_id, effective_date)` on `SalaryRecord`.
- **Measured, not assumed:** `/api/employees` (with search) and `/api/analytics/summary` each respond in ~100 ms against the full 10k dataset.

## Design Decisions
| Decision | Rationale |
|---|---|
| **Salary history, not a salary column** | An HR system that overwrites pay on edit can't reconstruct payroll history — a real requirement, not a nice-to-have. Append-only makes correctness structural. |
| **Currency-independent "pay index"** | Grouping raw salaries across INR/USD/EUR/GBP/CAD/AUD produces a confident wrong number. Cross-currency analytics use *salary ÷ country entry-level base*; raw averages are reserved for single-currency groups. |
| **SQLite over Postgres** | Zero operational overhead for a single-writer internal tool; plain SQLAlchemy means a one-line connection-string change to port if write load ever demands it. |
| **Soft delete** | An employee leaving the company must not erase their compensation history. |
| **FastAPI** | Matches the JD's Python-leaning profile; free OpenAPI docs and Pydantic validation that doubles as the API contract. |

More detail in [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).

## Deliberately Out of Scope
Excluded on purpose — not by oversight. Full reasoning in [`docs/REQUIREMENTS.md`](docs/REQUIREMENTS.md):

- **Authentication / roles / multi-tenancy** — single HR-Manager persona; the first thing to add before real deployment.
- **Live FX conversion** — needs real rates and an as-of-date policy; honest simplification beats a wrong number.
- **Payroll / tax processing** — this is a system of record, not a payroll engine.
- **Bulk CSV import UI** — the seed script satisfies the 10k requirement.
- **Org-chart visualization** — `manager_id` is modeled; no UI yet.
- **Demographic pay-equity analysis** — valuable but requires sensitive data; off-limits here.

## Documentation
| Document | Contents |
|---|---|
| [`docs/REQUIREMENTS.md`](docs/REQUIREMENTS.md) | Goal, scope, and deliberate non-goals — **read this first** |
| [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) | System design, layering, and trade-offs |
| [`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md) | Shipping to a public URL (Docker & split hosting) |
| [`docs/AI_USAGE.md`](docs/AI_USAGE.md) | How AI tools were used and where verification caught real bugs |

---

<p align="center"><sub>Built as a product-focused engineering exercise — optimising for clear thinking, sound architecture, and maintainable code over unnecessary complexity.</sub></p>