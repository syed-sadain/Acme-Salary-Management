# Requirements Document — ACME Salary Management System

## Goal
Replace ACME's spreadsheet-based salary tracking with a web application that lets an
HR Manager manage salary data for ~10,000 employees across multiple countries, and
answer organization-level questions about *how the org pays people* (headcount, pay
ranges, department/country cost breakdowns, distribution shape) without exporting to
Excel.

## Primary Persona
**HR Manager** — needs to: (1) look up and edit an individual employee's compensation,
(2) see the history of how that compensation changed, (3) understand pay patterns
across the org (by department, country, job level) to spot outliers, budget, and
report upward. They are not an engineer — the tool must be fast, filterable, and not
require SQL or spreadsheets.

## In Scope (v1)
- **Employee directory**: search, filter (department, country, employment status,
  job level), sort, paginate over 10,000 records without lag.
- **Employee profile**: personal/employment details + current compensation
  (base salary, currency, bonus target) + full **salary change history** (every
  raise/adjustment is a new dated record, never an overwrite — this is the audit
  trail an HR org legally needs).
- **Edit salary / give a raise**: recorded as a new salary-history row with an
  effective date and optional reason, instead of mutating the current value in place.
- **Add / deactivate employee** (soft delete — an org doesn't want salary history to
  vanish when someone leaves).
- **Org-wide analytics dashboard**: headcount, total annual payroll cost, average
  and median salary by department and by country, salary distribution histogram,
  top/bottom paid departments — the "answer questions about how we pay people" ask.
- **Seed data**: a script generating 10,000 realistic employees spread across 6
  countries, ~8 departments, and 5 job levels, with correlated (not random) salary
  bands so the analytics are actually meaningful to look at.
- **API-first backend** with automated tests around the core business logic
  (salary-history correctness, filtering/pagination, analytics aggregation).

## Deliberately Out of Scope (and why)
- **Authentication / roles / multi-tenant orgs** — the brief is a single HR Manager
  persona for one org. Bolting on auth would mostly be boilerplate that doesn't
  demonstrate the modeling/product thinking this exercise is testing. Noted as the
  first thing to add before any real deployment.
- **Multi-currency conversion to one reporting currency** — real FX conversion needs
  live rates and a "as-of-date" policy. Instead, salaries are stored in local currency
  and analytics are grouped **by country/currency** rather than falsely summed across
  currencies. This is an honest simplification rather than a wrong number.
- **Payroll execution / tax / statutory deductions** — this is a compensation
  *system of record*, not a payroll processor. Different regulatory domain per
  country, out of scope for a take-home.
- **Bulk CSV import / export UI** — the seed script covers the "10,000 employees"
  requirement; a general import pipeline (validation, conflict resolution) is a
  separate feature-sized effort.
- **Org chart / manager hierarchy visualization** — `manager_id` is modeled in the
  schema for future use, but no UI is built for it — not core to "manage salary data".
- **Demographic pay-equity analysis (gender/ethnicity pay gap)** — genuinely valuable
  in a real product, but requires sensitive personal data most orgs restrict tightly.
  Left out rather than modeled carelessly; analytics instead slice by department,
  country, and level, which are non-sensitive and still answer "how do we pay people".
- **Notifications / approval workflows for raises** — v1 is a system of record, not a
  workflow engine.

## Non-functional targets
- Employee list and analytics endpoints stay responsive (indexed queries, server-side
  pagination) at 10,000 rows — this is the one hard performance constraint given in
  the brief, so it's treated as a real requirement, not an afterthought.
- Backend is covered by fast, deterministic unit tests (no network, no sleep-based
  timing) around salary-history logic, filtering, and analytics math — the parts most
  likely to have an off-by-one or a silent wrong aggregate.
