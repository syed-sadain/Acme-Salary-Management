# AI Usage Notes

This project was built with Claude (Anthropic) as an agentic coding assistant,
operating directly in a sandboxed dev environment with shell/file/test-runner
access — not copy-pasting from a chat window. This document is an honest
account of the workflow, the prompts driving it, and, more usefully, the
places AI-assisted iteration changed the outcome.

## Workflow

1. **Requirements before code.** The assessment brief was given as-is and the
   first deliverable produced was `docs/REQUIREMENTS.md` — goal, in-scope
   features, and an explicit list of what's deliberately excluded and why.
   This came *before* any schema or endpoint was written, on purpose: the
   scope-cutting decisions (no FX conversion, no auth, no payroll/tax, no
   bulk import) are product decisions, not implementation details, and they
   shaped what the schema needed to support.

2. **Backend first, seeded and exercised before the frontend existed.** Models
   → schemas → CRUD/business-logic layer → routers → seed script, each
   written, then actually run — not just written and assumed correct. The
   seed script was smoke-tested at `--count 200` before ever running the full
   10,000, and the API was started and hit with real HTTP requests against
   the full seeded dataset (`curl`, timed) before writing a single frontend
   line.

3. **Tests written against real behavior, not aspirational behavior.** 27
   backend unit tests were added covering employee CRUD, the append-only
   salary-history contract, pagination/filtering/search, and analytics
   aggregation — using an isolated in-memory SQLite database per test via a
   pytest fixture, so the suite runs in well under a second with no shared
   state between tests.

4. **Frontend design was planned as tokens before code**, per the working
   agreement to avoid generic "AI-generated dashboard" defaults (cream +
   terracotta, dark + neon, uniform rounded SaaS cards). The direction chosen
   — a compensation *ledger* aesthetic (serif display type, tabular numbers,
   hairline dividers, one amber accent reserved for money figures) — was
   picked because it's grounded in what the product actually is, not
   because it's a safe default.

5. **Commits track the above as it happened**, not squashed into one
   "initial commit" at the end: requirements → backend core → backend tests
   → a real bug fix found during verification (below) → frontend scaffold →
   frontend pages → deployment artifacts.

## Where verification changed the actual design

The most consequential thing AI-assisted iteration caught here wasn't a
syntax error — it was a **quietly wrong aggregate**. After seeding the full
10,000-employee dataset and hitting `/api/analytics/summary` for real, the
department and job-level breakdowns were averaging raw salary figures across
employees paid in INR, USD, EUR, GBP, CAD, and AUD into one number labeled
with whichever currency happened to be seen last for that group. It would
have looked completely plausible in a demo and been simply wrong.

The fix — introduced a currency-independent "pay index" (salary ÷ that
employee's own country's entry-level base pay) for any grouping that spans
countries, and reserved raw currency averages for groupings where every
member shares one currency (`by_country`) — is recorded as its own commit
(`fix(analytics): stop blending currencies...`) with a regression test
(`test_by_department_never_naively_averages_across_currencies`) and a direct
unit test on the aggregation helper (`test_group_salary_stats_raises_on_mixed_currency_within_a_group`)
so the mistake can't silently come back. This is exactly the class of bug
that's easy for both a human and an AI assistant to introduce by generalizing
a working single-currency test case (India-only) to production data that
spans currencies — it only surfaced by actually running the aggregation
against realistic multi-country data instead of trusting the query would
"obviously" generalize.

## Trade-offs made explicitly, not by default

- **SQLite over Postgres**: matches the brief's suggestion, avoids
  operational overhead not justified at this scope; documented migration
  path in `docs/ARCHITECTURE.md` if concurrent writes ever demand it.
- **No FX conversion**: rather than silently picking a conversion rate and a
  staleness policy, salaries stay in local currency and cross-currency
  analytics use the pay-index approach above. An honest simplification
  beats a confident wrong number.
- **Soft delete, not hard delete**: `DELETE /employees/{id}` marks the
  employee inactive and preserves their salary history, because an HR system
  that lets someone's compensation history disappear when they leave the
  company is not a system an HR team could actually rely on.
- **No auth**: explicitly named as the first thing to add before any real
  deployment, in `docs/REQUIREMENTS.md`, rather than silently omitted.

## What AI did *not* decide unsupervised

Every schema field, every deliberately-out-of-scope item, and the final
visual direction were reviewed against the brief's actual persona (an HR
manager, not an engineer) before being built — e.g., the analytics page
explicitly explains *why* department figures are a "pay index" rather than
a raw salary number, because an HR manager reading that number needs to
trust it without reading the source code.
