# Architecture

## System overview

```
┌───────────────────┐         HTTPS/JSON          ┌───────────────────────┐
│   React + TS SPA   │ ───────────────────────────▶│   FastAPI backend     │
│   (Vite, Tailwind,  │◀───────────────────────────│   (Python 3.12)       │
│    Recharts)        │         REST API             │                       │
└───────────────────┘                              │  routers/ → crud.py   │
                                                     │  → SQLAlchemy models │
                                                     └───────────┬───────────┘
                                                                 │
                                                                 ▼
                                                     ┌───────────────────────┐
                                                     │   SQLite (acme_salary │
                                                     │   .db) — 10k employees│
                                                     └───────────────────────┘
```

In production, `nginx` (frontend container) serves the built static SPA and
reverse-proxies `/api/*` to the backend container — see `docker-compose.yml`.
In local dev, Vite's dev server proxies `/api/*` to `http://127.0.0.1:8000`
(`frontend/vite.config.ts`) so the SPA can call relative `/api/...` paths in
both environments without an env-specific base URL.

## Backend layering

```
routers/*.py   → HTTP concerns only: parse query params, call crud, map to
                 response models, raise HTTPException on 404s.
crud.py        → All business logic and SQL. Pure functions taking a
                 Session, easy to unit test without spinning up the app.
models.py      → SQLAlchemy ORM tables.
schemas.py     → Pydantic request/response contracts (independent of the ORM
                 shape, so the API contract can evolve without a DB migration
                 and vice versa).
```

This is a conventional layered structure, chosen deliberately over something
fancier (e.g. full DDD/hexagonal) — at this scope (2 entities, a handful of
endpoints) that would add indirection without buying anything. The one
non-obvious layering decision worth calling out: **`crud.py` doesn't return
ORM objects for the analytics endpoint** — it does the aggregation in SQL/
Python and returns typed Pydantic models directly. That keeps the router thin
and keeps the "what is a department average, exactly" question answered in
exactly one place, with direct unit tests on that function.

## The core data modeling decision: salary history, not a salary column

`Employee` does **not** have a `salary` column. Compensation lives in a
separate, append-only `SalaryRecord` table (`employee_id`, `base_salary`,
`currency`, `effective_date`, `reason`). "Give a raise" is an `INSERT`, never
an `UPDATE`. The employee's *current* salary is simply the record with the
latest `effective_date`.

Why this is worth the extra table for a take-home: it's the single decision
that most changes what the system can honestly claim to do. An HR system that
overwrites salary on edit can't answer "when did this person's pay last
change" or reconstruct payroll history — which is a real requirement for any
org handling compensation, not a hypothetical one. It also makes the API
naturally correct: `POST /employees/{id}/salary-records` can never
accidentally destroy history the way a `PUT` on a single column could.

## Performance at 10,000 rows

The one explicit performance constraint in the brief is "10,000 employees,"
so it's treated as real, not decorative:

- **The directory list never N+1s.** `crud.list_employees` computes each
  employee's current salary via a single query: a correlated subquery for
  "latest `effective_date` per employee" joined back to `salary_records`,
  joined once to `employees`. One round-trip regardless of page size.
- **Pagination and filtering happen in SQL** (`LIMIT`/`OFFSET` + indexed
  `WHERE` clauses on `department`, `country`, `job_level`, `status`), not in
  Python after loading everything into memory.
- **Indexes**: `department`, `country`, `job_level`, `status` are indexed
  columns on `Employee`; `(employee_id, effective_date)` is indexed on
  `SalaryRecord` since it's the access pattern for "current salary."
- **Measured, not assumed**: against the full 10k-row seeded database, both
  `GET /api/employees` (with search) and `GET /api/analytics/summary`
  respond in ~100ms on this machine — see `docs/AI_USAGE.md` for how this was
  verified during development, and the bug it surfaced.

At meaningfully larger scale (100k+, or multi-tenant) the next steps would be:
paginate analytics aggregation with materialized/cached summary tables
refreshed on write, move off SQLite to Postgres for concurrent writes, and
add a search index (Postgres full-text or similar) if free-text search
becomes a bottleneck.

## Why SQLite

The brief allows "any relational database... like SQLite." SQLite was kept
deliberately rather than reached for Postgres by default: for a single-writer
internal HR tool backed by a file, it has zero operational overhead (no
connection pool, no separate service to run/deploy), and the schema/queries
are plain SQLAlchemy Core-compatible SQL that would port to Postgres with a
one-line connection-string change if concurrent-write load ever demanded it.
Not reaching for a "bigger" database by default, when the simpler one
genuinely satisfies the requirement, is itself the engineering judgment call.

## Why FastAPI

Matches "backend language/framework as per JD (preferred)" for a
Python/AI-ML-leaning profile, plus: automatic OpenAPI docs at `/docs` for
free (useful for a reviewer to poke at the API directly), Pydantic validation
that doubles as the request/response contract, and `TestClient` makes the
test suite fast and dependency-light (see `docs/AI_USAGE.md` for the testing
approach).

## Frontend structure

```
src/
  api/client.ts     — typed fetch functions, one per endpoint
  types.ts          — TS types mirroring the backend Pydantic schemas
  lib/format.ts      — currency/date formatting helpers
  components/        — small shared UI (Layout/nav, StatusBadge)
  pages/              — one file per route (Directory, EmployeeDetail,
                        AddEmployee, Analytics)
```

No global state library — the app's state is "whatever the current page's
API call returned," which `useState`/`useEffect` per page handles without
the ceremony of Redux/Zustand for four screens. React Router handles
navigation; Recharts handles the two analytics charts.
