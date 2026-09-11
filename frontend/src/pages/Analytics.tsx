import { useEffect, useState } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { fetchAnalyticsSummary } from "../api/client";
import type { AnalyticsSummary } from "../types";

export default function Analytics() {
  const [data, setData] = useState<AnalyticsSummary | null>(null);

  useEffect(() => {
    fetchAnalyticsSummary().then(setData);
  }, []);

  if (!data) {
    return <div className="px-10 py-8 text-(--color-ink-soft)">Loading…</div>;
  }

  const deptChart = data.by_department.map((d) => ({
    name: d.group,
    index: d.avg_pay_index,
  }));

  const histChart = data.pay_index_histogram.map((b) => ({
    name: `${b.range_start.toFixed(1)}–${b.range_end.toFixed(1)}x`,
    count: b.count,
  }));

  return (
    <div className="px-10 py-8 max-w-[1400px]">
      <header className="mb-8">
        <h1 className="font-display text-3xl text-(--color-ink)">
          How we pay people
        </h1>
        <p className="mt-1 text-sm text-(--color-ink-soft) max-w-2xl">
          Org-wide compensation patterns across departments, countries, and
          levels. Salaries stay in local currency — department and level
          figures use a pay index (salary ÷ that country's entry-level base)
          so nothing gets falsely averaged across currencies.
        </p>
      </header>

      <div className="grid grid-cols-4 gap-4 mb-8">
        <Kpi label="Total employees" value={data.total_employees.toLocaleString()} />
        <Kpi label="Active" value={data.active_employees.toLocaleString()} accent="positive" />
        <Kpi label="Inactive" value={data.inactive_employees.toLocaleString()} accent="warning" />
        <Kpi label="Countries" value={String(data.by_country.length)} />
      </div>

      <div className="grid grid-cols-2 gap-6 mb-8">
        <Panel title="Average pay index by department">
          <p className="text-xs text-(--color-ink-faint) mb-3">
            1.0x = that country's entry-level base pay
          </p>
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={deptChart} layout="vertical" margin={{ left: 24 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#E3E8EF" horizontal={false} />
              <XAxis type="number" tick={{ fontSize: 12, fill: "#475467" }} />
              <YAxis
                type="category"
                dataKey="name"
                width={140}
                tick={{ fontSize: 12, fill: "#475467" }}
              />
              <Tooltip
                formatter={(v) => [`${Number(v).toFixed(2)}x`, "Avg pay index"]}
                contentStyle={{ fontSize: 12, borderRadius: 4, borderColor: "#E3E8EF" }}
              />
              <Bar dataKey="index" fill="#B8860B" radius={[0, 3, 3, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </Panel>

        <Panel title="Org-wide pay distribution">
          <p className="text-xs text-(--color-ink-faint) mb-3">
            Headcount by pay index bucket, across all countries
          </p>
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={histChart}>
              <CartesianGrid strokeDasharray="3 3" stroke="#E3E8EF" vertical={false} />
              <XAxis dataKey="name" tick={{ fontSize: 11, fill: "#475467" }} />
              <YAxis tick={{ fontSize: 12, fill: "#475467" }} />
              <Tooltip contentStyle={{ fontSize: 12, borderRadius: 4, borderColor: "#E3E8EF" }} />
              <Bar dataKey="count" fill="#101828" radius={[3, 3, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </Panel>
      </div>

      <div className="grid grid-cols-2 gap-6">
        <Panel title="By country">
          <Table
            rows={data.by_country.map((c) => ({
              label: c.group,
              headcount: c.headcount,
              value: `${c.avg_salary.toLocaleString()} ${c.currency}`,
              sub: `median ${c.median_salary.toLocaleString()} ${c.currency}`,
            }))}
          />
        </Panel>
        <Panel title="By job level">
          <Table
            rows={data.by_level.map((l) => ({
              label: l.group,
              headcount: l.headcount,
              value: `${l.avg_pay_index.toFixed(2)}x`,
              sub: `median ${l.median_pay_index.toFixed(2)}x`,
            }))}
          />
        </Panel>
      </div>
    </div>
  );
}

function Kpi({
  label,
  value,
  accent,
}: {
  label: string;
  value: string;
  accent?: "positive" | "warning";
}) {
  const color =
    accent === "positive"
      ? "text-(--color-positive)"
      : accent === "warning"
        ? "text-(--color-warning)"
        : "text-(--color-ink)";
  return (
    <div className="rounded border border-(--color-line) bg-(--color-paper-raised) px-5 py-4">
      <p className="text-xs text-(--color-ink-faint)">{label}</p>
      <p className={`font-display text-3xl mt-1 tabular ${color}`}>{value}</p>
    </div>
  );
}

function Panel({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="rounded border border-(--color-line) bg-(--color-paper-raised) p-5">
      <h2 className="text-xs font-medium text-(--color-ink-faint) mb-1">
        {title}
      </h2>
      {children}
    </div>
  );
}

function Table({
  rows,
}: {
  rows: { label: string; headcount: number; value: string; sub: string }[];
}) {
  return (
    <table className="w-full text-sm mt-2">
      <tbody>
        {rows.map((r) => (
          <tr key={r.label} className="border-b border-(--color-line) last:border-0">
            <td className="py-2.5 pr-3">
              <p className="text-(--color-ink)">{r.label}</p>
              <p className="text-xs text-(--color-ink-faint)">
                {r.headcount.toLocaleString()} people
              </p>
            </td>
            <td className="py-2.5 text-right tabular">
              <p className="font-medium text-(--color-ink)">{r.value}</p>
              <p className="text-xs text-(--color-ink-faint)">{r.sub}</p>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
