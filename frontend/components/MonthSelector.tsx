"use client";

import { useRouter, useSearchParams, usePathname } from "next/navigation";
import { Suspense } from "react";

const MONTHS = [
  { value: "2026-03", label: "Mars 2026" },
  { value: "2026-04", label: "Avril 2026" },
];

interface Props {
  current: string;
}

function MonthSelectorInner({ current }: Props) {
  const router = useRouter();
  const searchParams = useSearchParams();
  const pathname = usePathname();

  const handleChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const params = new URLSearchParams(searchParams.toString());
    params.set("month", e.target.value);
    router.push(`${pathname}?${params.toString()}`);
  };

  return (
    <select
      value={current}
      onChange={handleChange}
      className="text-sm bg-white border border-[#E0E7FF] rounded-lg px-3 py-2 text-[#1E1B4B] font-medium cursor-pointer hover:border-[#6366F1] focus:outline-none focus:ring-2 focus:ring-[#6366F1]/30 transition-colors duration-150"
      aria-label="Sélectionner un mois"
    >
      {MONTHS.map((m) => (
        <option key={m.value} value={m.value}>
          {m.label}
        </option>
      ))}
    </select>
  );
}

export default function MonthSelector(props: Props) {
  return (
    <Suspense fallback={<div className="w-[140px] h-10 rounded-lg bg-[#F5F3FF]" />}>
      <MonthSelectorInner {...props} />
    </Suspense>
  );
}
