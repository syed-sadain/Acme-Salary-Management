import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { createEmployee, fetchReferenceData } from "../api/client";
import type { ReferenceData } from "../types";

const emptyForm = {
  first_name: "",
  last_name: "",
  email: "",
  department: "",
  job_title: "",
  job_level: "",
  country: "",
  hire_date: new Date().toISOString().slice(0, 10),
  base_salary: "",
  bonus_target_pct: "10",
};

export default function AddEmployee() {
  const navigate = useNavigate();
  const [ref, setRef] = useState<ReferenceData | null>(null);
  const [form, setForm] = useState(emptyForm);
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    fetchReferenceData().then((data) => {
      setRef(data);
      setForm((f) => ({
        ...f,
        department: f.department || data.departments[0],
        job_level: f.job_level || data.job_levels[0],
        country: f.country || data.countries[0].name,
      }));
    });
  }, []);

  const currency =
    ref?.countries.find((c) => c.name === form.country)?.currency ?? "USD";

  function set<K extends keyof typeof emptyForm>(key: K, value: string) {
    setForm((f) => ({ ...f, [key]: value }));
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setSaving(true);
    try {
      const employee = await createEmployee({
        first_name: form.first_name,
        last_name: form.last_name,
        email: form.email,
        department: form.department,
        job_title: form.job_title,
        job_level: form.job_level,
        country: form.country,
        hire_date: form.hire_date,
        status: "active",
        starting_salary: {
          base_salary: Number(form.base_salary),
          currency,
          bonus_target_pct: Number(form.bonus_target_pct),
          effective_date: form.hire_date,
          reason: "Initial hire",
        },
      });
      navigate(`/employees/${employee.id}`);
    } catch (err: unknown) {
      const message =
        (err as { response?: { data?: { detail?: string } } })?.response
          ?.data?.detail ??
        "Couldn't create this employee. Check the fields and try again.";
      setError(typeof message === "string" ? message : "Couldn't create this employee.");
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="px-10 py-8 max-w-[720px]">
      <h1 className="font-display text-3xl text-(--color-ink)">
        Add employee
      </h1>
      <p className="mt-1 text-sm text-(--color-ink-soft) mb-8">
        Every new hire starts with an initial compensation record — you can
        record raises later from their profile.
      </p>

      <form
        onSubmit={handleSubmit}
        className="rounded border border-(--color-line) bg-(--color-paper-raised) p-6 grid grid-cols-2 gap-4"
      >
        <Field label="First name">
          <input
            required
            value={form.first_name}
            onChange={(e) => set("first_name", e.target.value)}
            className="input"
          />
        </Field>
        <Field label="Last name">
          <input
            required
            value={form.last_name}
            onChange={(e) => set("last_name", e.target.value)}
            className="input"
          />
        </Field>
        <Field label="Email" full>
          <input
            required
            type="email"
            value={form.email}
            onChange={(e) => set("email", e.target.value)}
            className="input"
          />
        </Field>
        <Field label="Job title" full>
          <input
            required
            value={form.job_title}
            onChange={(e) => set("job_title", e.target.value)}
            className="input"
            placeholder="e.g. Senior Software Engineer"
          />
        </Field>
        <Field label="Department">
          <select
            value={form.department}
            onChange={(e) => set("department", e.target.value)}
            className="input"
          >
            {ref?.departments.map((d) => (
              <option key={d}>{d}</option>
            ))}
          </select>
        </Field>
        <Field label="Job level">
          <select
            value={form.job_level}
            onChange={(e) => set("job_level", e.target.value)}
            className="input"
          >
            {ref?.job_levels.map((l) => (
              <option key={l}>{l}</option>
            ))}
          </select>
        </Field>
        <Field label="Country">
          <select
            value={form.country}
            onChange={(e) => set("country", e.target.value)}
            className="input"
          >
            {ref?.countries.map((c) => (
              <option key={c.name}>{c.name}</option>
            ))}
          </select>
        </Field>
        <Field label="Hire date">
          <input
            required
            type="date"
            value={form.hire_date}
            onChange={(e) => set("hire_date", e.target.value)}
            className="input"
          />
        </Field>
        <Field label={`Starting base salary (${currency})`}>
          <input
            required
            type="number"
            min="1"
            value={form.base_salary}
            onChange={(e) => set("base_salary", e.target.value)}
            className="input"
          />
        </Field>
        <Field label="Bonus target (%)">
          <input
            type="number"
            min="0"
            max="100"
            value={form.bonus_target_pct}
            onChange={(e) => set("bonus_target_pct", e.target.value)}
            className="input"
          />
        </Field>

        {error && (
          <p className="col-span-2 text-sm text-(--color-warning)">{error}</p>
        )}

        <div className="col-span-2 flex justify-end gap-3 mt-2">
          <button
            type="button"
            onClick={() => navigate("/")}
            className="rounded border border-(--color-line) px-4 py-2 text-sm text-(--color-ink-soft) hover:bg-(--color-paper) transition-colors"
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={saving}
            className="rounded-md bg-(--color-ink) px-5 py-2 text-sm font-medium text-white shadow-sm disabled:opacity-50 hover:bg-black transition-colors"
          >
            {saving ? "Adding…" : "Add employee"}
          </button>
        </div>
      </form>
    </div>
  );
}

function Field({
  label,
  children,
  full,
}: {
  label: string;
  children: React.ReactNode;
  full?: boolean;
}) {
  return (
    <label className={`text-xs text-(--color-ink-soft) ${full ? "col-span-2" : ""}`}>
      {label}
      <div className="mt-1">{children}</div>
    </label>
  );
}
