import { NavLink, Outlet } from "react-router-dom";

const navItems = [
  { to: "/", label: "Directory", end: true },
  { to: "/analytics", label: "Analytics" },
];

export default function Layout() {
  return (
    <div className="min-h-screen flex">
      <aside className="w-64 shrink-0 border-r border-(--color-line) bg-(--color-paper-raised) flex flex-col">
        <div className="px-6 pt-8 pb-6">
          <p className="font-display text-2xl leading-none text-(--color-ink)">
            Acme
          </p>
          <p className="font-display text-2xl leading-none text-(--color-amber) -mt-1">
            Compensation
          </p>
          <p className="mt-3 text-xs text-(--color-ink-faint)">
            HR console &middot; global payroll ledger
          </p>
        </div>

        <nav className="flex-1 px-3">
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.end}
              className={({ isActive }) =>
                `block rounded px-3 py-2 mb-1 text-sm transition-colors ${
                  isActive
                    ? "bg-(--color-amber-soft) text-(--color-ink) font-medium"
                    : "text-(--color-ink-soft) hover:bg-(--color-paper) hover:text-(--color-ink)"
                }`
              }
            >
              {item.label}
            </NavLink>
          ))}
        </nav>

        <div className="px-6 py-5 border-t border-(--color-line) text-xs text-(--color-ink-faint)">
          10,000 employee records
          <br />6 countries
        </div>
      </aside>

      <main className="flex-1 min-w-0">
        <Outlet />
      </main>
    </div>
  );
}
