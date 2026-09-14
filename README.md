# 💰 ACME Salary Management

<h3 align="center">
  <strong>A modern, full-stack compensation management system built for ACME's global HR team.</strong>
</h3>
<p align="center">
  Manage employee compensation, preserve complete salary history, and analyze organization-wide pay data — all from one centralized system.
</p>

<p align="center">
  <a href="https://fastapi.tiangolo.com/">
    <img src="https://img.shields.io/badge/Backend-FastAPI-009688?logo=fastapi&logoColor=white" alt="FastAPI">
  </a>
  <a href="https://www.python.org/">
    <img src="https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white" alt="Python">
  </a>
  <a href="https://react.dev/">
    <img src="https://img.shields.io/badge/Frontend-React%2019-61DAFB?logo=react&logoColor=black" alt="React">
  </a>
  <a href="https://www.typescriptlang.org/">
    <img src="https://img.shields.io/badge/TypeScript-5-3178C6?logo=typescript&logoColor=white" alt="TypeScript">
  </a>
  <a href="https://www.sqlite.org/">
    <img src="https://img.shields.io/badge/Database-SQLite-003B57?logo=sqlite&logoColor=white" alt="SQLite">
  </a>
</p>

<p align="center">
  <a href="https://www.docker.com/">
    <img src="https://img.shields.io/badge/Containerized-Docker-2496ED?logo=docker&logoColor=white" alt="Docker">
  </a>
  <a href="https://pytest.org/">
    <img src="https://img.shields.io/badge/Tests-27%20Passing-4C9A2A?logo=pytest&logoColor=white" alt="Tests">
  </a>
  <img src="https://img.shields.io/badge/License-MIT-lightgrey" alt="MIT License">
</p>

---

## 📌 Overview

ACME's HR team manages compensation data for **10,000 employees across 6 countries**. Managing this information through spreadsheets is slow, error-prone, and difficult to analyze.

**ACME Salary Management** replaces spreadsheet-based compensation tracking with a centralized, API-first web application.

The system enables HR teams to:

* 🔍 Search and filter employees efficiently
* 👤 View complete employee profiles
* 💰 Track salary and compensation changes
* 📝 Preserve a complete salary history
* ➕ Add new employees
* 🚫 Soft-deactivate employees without losing historical data
* 📊 Analyze compensation data across departments, countries, and job levels

> **Core Design Principle:** Salary history is append-only.
> A salary change creates a new compensation record instead of overwriting previous data.

This ensures the system can always answer:

**Who was paid what, when, and why?**

---

## ✨ Key Features

| Area                          | Capability                                                                               |
| ----------------------------- | ---------------------------------------------------------------------------------------- |
| 🔍 **Employee Directory**     | Search by name, email, or ID with filters for department, country, and employment status |
| 📄 **Employee Profile**       | View complete employee details and full compensation history                             |
| 💰 **Salary Management**      | Record raises and compensation adjustments without overwriting previous records          |
| 📝 **Audit-Friendly History** | Every salary record includes effective date and reason                                   |
| ➕ **Employee Management**     | Add employees with an initial salary record                                              |
| 🚫 **Soft Delete**            | Deactivate employees while preserving employment and compensation history                |
| 📊 **Analytics Dashboard**    | Analyze headcount, pay distribution, department metrics, countries, and job levels       |
| ⚡ **Performance**             | Server-side filtering and pagination designed for 10,000 employees                       |
| 🧪 **Testing**                | 27 automated pytest tests with isolated in-memory databases                              |

---

## 🏗️ Architecture

```text
┌─────────────────────────────────────────────────────┐
│                   React Frontend                    │
│                                                     │
│  React 19 • TypeScript • Vite • Tailwind CSS v4    │
│  React Router • Recharts                           │
└───────────────────────┬─────────────────────────────┘
                        │
                        │ REST API
                        ▼
┌─────────────────────────────────────────────────────┐
│                   FastAPI Backend                   │
│                                                     │
│  FastAPI • Pydantic • SQLAlchemy                    │
│                                                     │
│  Routers → Business Logic → Database Layer          │
└───────────────────────┬─────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────┐
│                     Database                        │
│                                                     │
│                  SQLite                            │
│                                                     │
│         Employee 1 ─────────── N SalaryRecord      │
└─────────────────────────────────────────────────────┘
```

---

## 🛠️ Tech Stack

### Backend

* Python 3.12
* FastAPI
* SQLAlchemy 2.0
* Pydantic v2
* Uvicorn

### Frontend

* React 19
* TypeScript
* Vite
* Tailwind CSS v4
* React Router
* Recharts

### Database

* SQLite
* SQLAlchemy ORM

### Testing

* pytest
* Isolated in-memory SQLite database

### DevOps & Deployment

* Docker
* Docker Compose
* nginx

---

## 🚀 Getting Started

### Option 1 — Run with Docker

The fastest way to run the complete application:

```bash
docker compose up --build
```

Once the containers are running:

| Service              | URL                        |
| -------------------- | -------------------------- |
| 🌐 Frontend          | http://localhost:3000      |
| ⚙️ Backend API       | http://localhost:8000      |
| 📚 API Documentation | http://localhost:8000/docs |

The application includes seed data for **10,000 employees**, making it ready for demonstration and testing.

---

## 💻 Option 2 — Run Locally

### Backend Setup

```bash
cd backend
```

Create a virtual environment:

```bash
python -m venv venv
```

### Windows PowerShell

```powershell
venv\Scripts\Activate.ps1
```

### macOS / Linux

```bash
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Seed the database:

```bash
python seed.py --count 10000 --reset
```

Start the FastAPI server:

```bash
uvicorn app.main:app --reload --port 8000
```

Backend will be available at:

```text
http://localhost:8000
```

Interactive API documentation:

```text
http://localhost:8000/docs
```

---

### Frontend Setup

Open a new terminal:

```bash
cd frontend
```

Install dependencies:

```bash
npm install
```

Start the development server:

```bash
npm run dev
```

The frontend will be available at:

```text
http://localhost:5173
```

## Deploy It Live

The frontend is Vercel-native; the backend needs a host with a writable disk
(SQLite is a file). Full runbook in [`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md).

| Piece | Host | One-line why |
|---|---|---|
| Frontend (React SPA) | **Vercel** | Static build — Vercel's sweet spot |
| Backend (FastAPI) | **Render** / **Railway** | Long-running process + persistent disk for SQLite |

```text
1. Backend  → Render "New → Blueprint" (reads render.yaml); note the URL
2. Frontend → edit frontend/vercel.json, set the /api rewrite to that URL
3. Vercel   → "Add New → Project", Root Directory = frontend, deploy
```

> **Why not the backend on Vercel?** Vercel functions run on an ephemeral,
> read-only filesystem. A SQLite-backed server would lose its 10,000 seeded rows
> on every cold start. Vercel hosts the frontend; the backend lives on a
> container host where the file persists across restarts.

---

## 📁 Project Structure

```text
acme-salary-mgmt/
│
├── backend/
│   ├── app/
│   │   ├── routers/
│   │   │   ├── employees.py
│   │   │   └── analytics.py
│   │   │
│   │   ├── main.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── crud.py
│   │   ├── constants.py
│   │   └── database.py
│   │
│   ├── tests/
│   ├── seed.py
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/
│   ├── src/
│   │   ├── api/
│   │   │   └── client.ts
│   │   │
│   │   ├── components/
│   │   ├── pages/
│   │   ├── lib/
│   │   ├── types.ts
│   │   └── index.css
│   │
│   └── Dockerfile
│
├── docs/
│   ├── REQUIREMENTS.md
│   ├── ARCHITECTURE.md
│   ├── DEPLOYMENT.md
│   └── AI_USAGE.md
│
├── docker-compose.yml
└── README.md
```

---

## 🔌 API Reference

| Method   | Endpoint                             | Description                                              |
| -------- | ------------------------------------ | -------------------------------------------------------- |
| `GET`    | `/api/health`                        | Application health check                                 |
| `GET`    | `/api/employees`                     | Paginated, searchable, and filterable employee directory |
| `POST`   | `/api/employees`                     | Create a new employee with an initial salary record      |
| `GET`    | `/api/employees/{id}`                | Retrieve employee profile and complete salary history    |
| `DELETE` | `/api/employees/{id}`                | Soft-deactivate an employee                              |
| `POST`   | `/api/employees/{id}/salary-records` | Add a new salary or compensation record                  |
| `GET`    | `/api/reference-data`                | Retrieve departments, countries, and job levels          |
| `GET`    | `/api/analytics/summary`             | Retrieve organization-wide compensation analytics        |

### Interactive API Documentation

FastAPI automatically provides interactive Swagger documentation:

```text
http://localhost:8000/docs
```

---

## 🗄️ Data Model

The application uses an append-only compensation history model.

```text
┌──────────────────────┐
│       Employee       │
├──────────────────────┤
│ id                   │
│ first_name           │
│ last_name            │
│ email                │
│ department           │
│ job_title            │
│ job_level            │
│ country              │
│ hire_date            │
│ status               │
│ manager_id           │
└──────────┬───────────┘
           │
           │ 1 : N
           ▼
┌───────────────────────────┐
│       SalaryRecord        │
├───────────────────────────┤
│ id                        │
│ employee_id (FK)          │
│ base_salary               │
│ currency                  │
│ bonus_target_pct          │
│ effective_date            │
│ reason                    │
└───────────────────────────┘
```

### Compensation History

An employee does **not** have a single mutable `salary` column.

Instead:

```text
New Salary Change
        │
        ▼
INSERT New SalaryRecord
        │
        ▼
Previous Records Remain Unchanged
```

The current salary is determined from the record with the latest `effective_date`.

This approach provides a reliable and auditable compensation history.

---

## 🧪 Testing

Run the backend test suite:

```bash
cd backend
```

Activate the virtual environment:

```bash
source venv/bin/activate
```

Then run:

```bash
pytest -v
```

### Test Coverage

The project includes **27 automated tests** covering:

* Employee creation and retrieval
* Employee updates and soft-delete behavior
* Salary history preservation
* Append-only compensation records
* Pagination
* Search functionality
* Filtering
* Analytics aggregation
* Cross-currency calculation safeguards

Each test uses an isolated in-memory SQLite database to avoid shared state and ensure reliable test execution.

---

## 🌱 Seed Data

Generate employee data with:

```bash
python seed.py
```

By default:

```text
10,000 employees
```

Generate a smaller dataset:

```bash
python seed.py --count 500
```

Reset and recreate the database:

```bash
python seed.py --reset
```

Employee salaries are generated using country-based pay bands, job-level multipliers, and individual variance to create a more realistic organizational compensation distribution.

---

## ⚡ Performance

The system is designed with the **10,000 employee requirement** as a core constraint.

### Performance Considerations

* ⚡ Server-side pagination
* 🔍 SQL-based filtering and search
* 🚫 No N+1 query patterns
* 📌 Indexed fields for common filtering operations
* 🗄️ Efficient retrieval of the latest salary record
* 📊 Analytics calculated at the database level

Indexed access patterns include:

```text
Employee
├── department
├── country
├── job_level
└── status

SalaryRecord
└── (employee_id, effective_date)
```

The `/api/employees` and `/api/analytics/summary` endpoints are designed to respond efficiently against the full 10,000 employee dataset.

---

## 🧠 Key Design Decisions

| Decision                           | Rationale                                                                      |
| ---------------------------------- | ------------------------------------------------------------------------------ |
| **Append-only salary history**     | Compensation changes never overwrite historical records                        |
| **No mutable salary column**       | The system can reconstruct historical compensation at any point in time        |
| **Soft delete**                    | Employee history remains available after offboarding                           |
| **Currency-independent pay index** | Avoids incorrect averaging of raw salaries across different currencies         |
| **SQLite**                         | Provides zero operational overhead for this application                        |
| **FastAPI**                        | Provides validation, OpenAPI documentation, and a clean API-first architecture |
| **Layered backend design**         | Separates HTTP handling, business logic, database models, and API schemas      |
| **Server-side pagination**         | Prevents loading all 10,000 employee records into the browser                  |

---

## 📊 Analytics

The analytics dashboard provides organization-wide insights, including:

* Total employee headcount
* Department-level compensation metrics
* Country-level breakdowns
* Job-level breakdowns
* Pay distribution
* Average compensation indexes

### Cross-Currency Consideration

Raw salaries in currencies such as:

```text
INR • USD • EUR • GBP • CAD • AUD
```

should not be naively averaged together.

For cross-country comparisons, the application uses a normalized **pay index** rather than presenting misleading raw currency averages.

---

## 🔐 Out of Scope

The following features were intentionally excluded from the current implementation:

* Authentication
* Role-based access control
* Multi-tenancy
* Live foreign exchange conversion
* Payroll processing
* Tax calculations
* Bulk CSV import UI
* Organization chart visualization
* Demographic pay-equity analysis

These are valid production features but are outside the scope of the current application.

---

## 📚 Documentation

Additional project documentation is available in the `docs` directory:

| Document          | Description                               |
| ----------------- | ----------------------------------------- |
| `REQUIREMENTS.md` | Project goals, scope, and non-goals       |
| `ARCHITECTURE.md` | System design and architectural decisions |
| `DEPLOYMENT.md`   | Deployment instructions                   |
| `AI_USAGE.md`     | AI tool usage and verification process    |

---

## 🎯 Engineering Principles

This project focuses on:

* **Correctness over shortcuts**
* **Maintainability over unnecessary complexity**
* **Clear separation of concerns**
* **Preserving historical business data**
* **Efficient handling of realistic data volumes**
* **Testable business logic**
* **Production-oriented API design**

---

<p align="center">
  <sub>
    Built as a product-focused engineering exercise — optimizing for clear architecture,
    maintainable code, reliable data handling, and practical scalability.
  </sub>
</p>
