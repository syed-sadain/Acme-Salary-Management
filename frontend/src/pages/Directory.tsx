import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { fetchEmployees, fetchReferenceData } from "../api/client";
import type { EmployeeListItem, ReferenceData } from "../types";
import StatusBadge from "../components/StatusBadge";
import { formatMoney } from "../lib/format";

const PAGE_SIZE = 25;

export default function Directory() {
  const [items, setItems] = useState<EmployeeListItem[]>([]);
  const [total, setTotal] = useState(0);
  const [totalPages, setTotalPages] = useState(1);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);

  const [search, setSearch] = useState("");
  const [department, setDepartment] = useState("");
  const [country, setCountry] = useState("");
  const [status, setStatus] = useState("");

  const [ref, setRef] = useState<ReferenceData | null>(null);

  useEffect(() => {
    fetchReferenceData().then(setRef);
  }, []);

  useEffect(() => {
    setLoading(true);
    const handle = setTimeout(() => {
      fetchEmployees({
        page,
        page_size: PAGE_SIZE,
        search: search || undefined,
        department: department || undefined,
        country: country || undefined,
        status: status || undefined,
      })
        .then((res) => {
          setItems(res.items);
          setTotal(res.total);
          setTotalPages(res.total_pages);
        })
        .finally(() => setLoading(false));
    }, 250); // debounce search-as-you-type
    return () => clearTimeout(handle);
  }, [page, search, department, country, status]);

  // Any filter change resets to page 1.
  useEffect(() => {
    setPage(1);
  }, [search, department, country, status]);

  return (
    <div className="px-10 py-8 max-w-[1400px]">
      <header className="mb-8">
        <h1 className="font-display text-3xl text-(--color-ink)">
          Employee directory
        </h1>
        <p className="mt-1 text-sm text-(--color-ink-soft)">
          {total.toLocaleString()} people on record. Search, filter, and open
          a profile to review or adjust compensation.
        </p>
      </header>

      <div className="flex flex-wrap items-center gap-3 mb-5">
        <input
          type="text"
          placeholder="Search by name, email, or employee ID"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="flex-1 min-w-[260px] rounded border border-(--color-line) bg-(--color-paper-raised) px-3 py-2 text-sm placeholder:text-(--color-ink-faint) focus:border-(--color-amber) focus:outline-none"
        />
        <select
          value={department}
          onChange={(e) => setDepartment(e.target.value)}
          className="rounded border border-(--color-line) bg-(--color-paper-raised) px-3 py-2 text-sm"
        >
          <option value="">All departments</option>
          {ref?.departments.map((d) => (
            <option key={d} value={d}>
              {d}
            </option>
          ))}
        </select>
        <select
          value={country}
          onChange={(e) => setCountry(e.target.value)}
          className="rounded border border-(--color-line) bg-(--color-paper-raised) px-3 py-2 text-sm"
        >
          <option value="">All countries</option>
          {ref?.countries.map((c) => (
            <option key={c.name} value={c.name}>
              {c.name}
            </option>
          ))}
        </select>
        <select
          value={status}
          onChange={(e) => setStatus(e.target.value)}
          className="rounded border border-(--color-line) bg-(--color-paper-raised) px-3 py-2 text-sm"
        >
          <option value="">All statuses</option>
          <option value="active">Active</option>
          <option value="inactive">Inactive</option>
        </select>
        <Link
          to="/employees/new"
          className="ml-auto rounded bg-(--color-ink) px-4 py-2 text-sm font-medium text-white hover:bg-black transition-colors"
        >
          Add employee
        </Link>
      </div>

      <div className="rounded border border-(--color-line) bg-(--color-paper-raised) overflow-hidden">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-(--color-line) text-left text-xs text-(--color-ink-faint)">
              <th className="px-4 py-3 font-medium">Employee</th>
              <th className="px-4 py-3 font-medium">Department</th>
              <th className="px-4 py-3 font-medium">Level</th>
              <th className="px-4 py-3 font-medium">Country</th>
              <th className="px-4 py-3 font-medium text-right">
                Current salary
              </th>
              <th className="px-4 py-3 font-medium">Status</th>
            </tr>
          </thead>
          <tbody>
            {items.map((emp) => (
              <tr
                key={emp.id}
                className="border-b border-(--color-line) last:border-0 hover:bg-(--color-paper) transition-colors"
              >
                <td className="px-4 py-3">
                  <Link
                    to={`/employees/${emp.id}`}
                    className="block hover:underline"
                  >
                    <span className="font-medium text-(--color-ink)">
                      {emp.first_name} {emp.last_name}
                    </span>
                    <span className="block text-xs text-(--color-ink-faint)">
                      {emp.employee_code} &middot; {emp.job_title}
                    </span>
                  </Link>
                </td>
                <td className="px-4 py-3 text-(--color-ink-soft)">
                  {emp.department}
                </td>
                <td className="px-4 py-3 text-(--color-ink-soft)">
                  {emp.job_level.split(" - ")[0]}
                </td>
                <td className="px-4 py-3 text-(--color-ink-soft)">
                  {emp.country}
                </td>
                <td className="px-4 py-3 text-right tabular font-medium text-(--color-ink)">
                  {emp.current_salary != null && emp.currency
                    ? formatMoney(emp.current_salary, emp.currency)
                    : "—"}
                </td>
                <td className="px-4 py-3">
                  <StatusBadge status={emp.status} />
                </td>
              </tr>
            ))}

            {!loading && items.length === 0 && (
              <tr>
                <td
                  colSpan={6}
                  className="px-4 py-12 text-center text-(--color-ink-faint)"
                >
                  No employees match these filters. Try clearing a filter or
                  the search box.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      <div className="flex items-center justify-between mt-4 text-sm text-(--color-ink-soft)">
        <span>
          Page {page} of {totalPages}
        </span>
        <div className="flex gap-2">
          <button
            onClick={() => setPage((p) => Math.max(1, p - 1))}
            disabled={page <= 1}
            className="rounded border border-(--color-line) px-3 py-1.5 disabled:opacity-40 hover:bg-(--color-paper) transition-colors"
          >
            Previous
          </button>
          <button
            onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
            disabled={page >= totalPages}
            className="rounded border border-(--color-line) px-3 py-1.5 disabled:opacity-40 hover:bg-(--color-paper) transition-colors"
          >
            Next
          </button>
        </div>
      </div>
    </div>
  );
}
