import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import {
  addSalaryRecord,
  deactivateEmployee,
  fetchEmployee,
} from "../api/client";
import type { EmployeeDetail as EmployeeDetailType } from "../types";
import StatusBadge from "../components/StatusBadge";
import { formatDate, formatMoney, initials } from "../lib/format";

export default function EmployeeDetail() {
  const { id } = useParams();
  const [employee, setEmployee] = useState<EmployeeDetailType | null>(null);
  const [showRaiseForm, setShowRaiseForm] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const load = () => {
    if (!id) return;
    fetchEmployee(Number(id)).then(setEmployee);
  };

  useEffect(load, [id]);

  if (!employee) {
    return <div className="px-10 py-8 text-(--color-ink-soft)">Loading…</div>;
  }

  const current = employee.salary_records[0];

  async function handleDeactivate() {
    if (!employee) return;
    if (!confirm(`Mark ${employee.first_name} ${employee.last_name} as inactive? Salary history is kept.`)) return;
    await deactivateEmployee(employee.id);
    load();
  }

  return (
    <div className="px-10 py-8 max-w-[1100px]">
      <Link
        to="/"
        className="text-sm text-(--color-ink-soft) hover:text-(--color-ink)"
      >
        ← Back to directory
      </Link>

      <div className="mt-4 flex items-start justify-between">
        <div className="flex items-center gap-4">
          <div className="h-14 w-14 rounded-full bg-(--color-amber-soft) text-(--color-amber) flex items-center justify-center font-display text-xl">
            {initials(employee.first_name, employee.last_name)}
          </div>
          <div>
            <h1 className="font-display text-3xl text-(--color-ink)">
              {employee.first_name} {employee.last_name}
            </h1>
            <p className="text-sm text-(--color-ink-soft) mt-0.5">
              {employee.job_title} &middot; {employee.department} &middot;{" "}
              {employee.employee_code}
            </p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <StatusBadge status={employee.status} />
          {employee.status === "active" && (
            <button
              onClick={handleDeactivate}
              className="rounded border border-(--color-line) px-3 py-1.5 text-sm text-(--color-ink-soft) hover:bg-(--color-paper) transition-colors"
            >
              Mark inactive
            </button>
          )}
        </div>
      </div>

      <div className="grid grid-cols-3 gap-6 mt-8">
        {/* Profile facts */}
        <div className="col-span-1 rounded border border-(--color-line) bg-(--color-paper-raised) p-5 h-fit">
          <h2 className="text-xs font-medium text-(--color-ink-faint) mb-4">
            Profile
          </h2>
          <dl className="space-y-3 text-sm">
            <Fact label="Email" value={employee.email} />
            <Fact label="Country" value={employee.country} />
            <Fact label="Job level" value={employee.job_level} />
            <Fact label="Hire date" value={formatDate(employee.hire_date)} />
            <Fact
              label="Current base salary"
              value={
                current
                  ? formatMoney(current.base_salary, current.currency)
                  : "—"
              }
              emphasize
            />
            <Fact
              label="Bonus target"
              value={current ? `${current.bonus_target_pct}%` : "—"}
            />
          </dl>
        </div>

        {/* Salary ledger */}
        <div className="col-span-2 rounded border border-(--color-line) bg-(--color-paper-raised) p-5">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xs font-medium text-(--color-ink-faint)">
              Compensation ledger
            </h2>
            <button
              onClick={() => setShowRaiseForm((v) => !v)}
              className="rounded bg-(--color-ink) px-3 py-1.5 text-xs font-medium text-white hover:bg-black transition-colors"
            >
              {showRaiseForm ? "Cancel" : "Record a change"}
            </button>
          </div>

          {showRaiseForm && (
            <RaiseForm
              employeeId={employee.id}
              defaultCurrency={current?.currency ?? employee.currency}
              onError={setError}
              onSaved={() => {
                setShowRaiseForm(false);
                load();
              }}
            />
          )}
          {error && (
            <p className="text-sm text-(--color-warning) mb-3">{error}</p>
          )}

          <ul>
            {employee.salary_records.map((record, i) => (
              <li
                key={record.id}
                className="flex items-start justify-between py-3 border-b border-(--color-line) last:border-0"
              >
                <div>
                  <p className="text-sm font-medium text-(--color-ink)">
                    {record.reason || "Salary record"}
                  </p>
                  <p className="text-xs text-(--color-ink-faint) mt-0.5">
                    Effective {formatDate(record.effective_date)}
                    {i === 0 && (
                      <span className="ml-2 text-(--color-positive)">
                        current
                      </span>
                    )}
                  </p>
                </div>
                <div className="text-right">
                  <p className="tabular text-sm font-medium text-(--color-ink)">
                    {formatMoney(record.base_salary, record.currency)}
                  </p>
                  <p className="text-xs text-(--color-ink-faint)">
                    {record.bonus_target_pct}% bonus target
                  </p>
                </div>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
}

function Fact({
  label,
  value,
  emphasize,
}: {
  label: string;
  value: string;
  emphasize?: boolean;
}) {
  return (
    <div className="flex items-baseline justify-between gap-3">
      <dt className="text-(--color-ink-faint)">{label}</dt>
      <dd
        className={`text-right tabular ${
          emphasize
            ? "font-display text-lg text-(--color-amber)"
            : "text-(--color-ink)"
        }`}
      >
        {value}
      </dd>
    </div>
  );
}

function RaiseForm({
  employeeId,
  defaultCurrency,
  onSaved,
  onError,
}: {
  employeeId: number;
  defaultCurrency: string;
  onSaved: () => void;
  onError: (msg: string | null) => void;
}) {
  const [baseSalary, setBaseSalary] = useState("");
  const [bonus, setBonus] = useState("0");
  const [effectiveDate, setEffectiveDate] = useState(
    new Date().toISOString().slice(0, 10),
  );
  const [reason, setReason] = useState("Annual merit increase");
  const [saving, setSaving] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    onError(null);
    setSaving(true);
    try {
      await addSalaryRecord(employeeId, {
        base_salary: Number(baseSalary),
        currency: defaultCurrency,
        bonus_target_pct: Number(bonus),
        effective_date: effectiveDate,
        reason,
      });
      onSaved();
    } catch {
      onError("Couldn't save that salary change. Check the amount and try again.");
    } finally {
      setSaving(false);
    }
  }

  return (
    <form
      onSubmit={handleSubmit}
      className="mb-5 rounded border border-(--color-line) bg-(--color-paper) p-4 grid grid-cols-2 gap-3"
    >
      <label className="text-xs text-(--color-ink-soft)">
        New base salary ({defaultCurrency})
        <input
          required
          type="number"
          min="1"
          value={baseSalary}
          onChange={(e) => setBaseSalary(e.target.value)}
          className="mt-1 w-full rounded border border-(--color-line) bg-(--color-paper-raised) px-2 py-1.5 text-sm"
        />
      </label>
      <label className="text-xs text-(--color-ink-soft)">
        Bonus target (%)
        <input
          type="number"
          min="0"
          max="100"
          value={bonus}
          onChange={(e) => setBonus(e.target.value)}
          className="mt-1 w-full rounded border border-(--color-line) bg-(--color-paper-raised) px-2 py-1.5 text-sm"
        />
      </label>
      <label className="text-xs text-(--color-ink-soft)">
        Effective date
        <input
          required
          type="date"
          value={effectiveDate}
          onChange={(e) => setEffectiveDate(e.target.value)}
          className="mt-1 w-full rounded border border-(--color-line) bg-(--color-paper-raised) px-2 py-1.5 text-sm"
        />
      </label>
      <label className="text-xs text-(--color-ink-soft)">
        Reason
        <select
          value={reason}
          onChange={(e) => setReason(e.target.value)}
          className="mt-1 w-full rounded border border-(--color-line) bg-(--color-paper-raised) px-2 py-1.5 text-sm"
        >
          <option>Annual merit increase</option>
          <option>Promotion</option>
          <option>Market adjustment</option>
          <option>Role change</option>
        </select>
      </label>
      <div className="col-span-2 flex justify-end">
        <button
          type="submit"
          disabled={saving}
          className="rounded bg-(--color-amber) px-4 py-1.5 text-sm font-medium text-white disabled:opacity-50 hover:brightness-95 transition-all"
        >
          {saving ? "Saving…" : "Save change"}
        </button>
      </div>
    </form>
  );
}
