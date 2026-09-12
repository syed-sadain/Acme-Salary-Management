export default function StatusBadge({ status }: { status: string }) {
  const isActive = status === "active";
  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full border px-2.5 py-0.5 text-xs font-medium ${
        isActive
          ? "border-(--color-positive)/25 bg-(--color-positive-soft) text-(--color-positive)"
          : "border-(--color-warning)/25 bg-(--color-warning-soft) text-(--color-warning)"
      }`}
    >
      <span
        className={`h-1.5 w-1.5 rounded-full ${
          isActive ? "bg-(--color-positive)" : "bg-(--color-warning)"
        }`}
      />
      {isActive ? "Active" : "Inactive"}
    </span>
  );
}
