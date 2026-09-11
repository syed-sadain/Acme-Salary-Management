export default function StatusBadge({ status }: { status: string }) {
  const isActive = status === "active";
  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full px-2.5 py-0.5 text-xs font-medium ${
        isActive
          ? "bg-(--color-positive-soft) text-(--color-positive)"
          : "bg-(--color-warning-soft) text-(--color-warning)"
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
