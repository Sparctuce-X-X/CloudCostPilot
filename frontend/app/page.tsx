import { getCosts, getCostsByTag } from "@/lib/api";
import OverviewCharts from "@/components/OverviewCharts";
import MonthSelector from "@/components/MonthSelector";
import { formatMonth } from "@/lib/format";

const DEFAULT_MONTH = "2026-03";

export default async function Home({
  searchParams,
}: {
  searchParams: Promise<{ month?: string }>;
}) {
  const params = await searchParams;
  const month = params.month || DEFAULT_MONTH;

  // Calculer le mois précédent pour comparer l'évolution
  const [year, monthNum] = month.split("-").map(Number);
  const prevDate = new Date(year, monthNum - 2, 1);
  const prevMonth = `${prevDate.getFullYear()}-${String(prevDate.getMonth() + 1).padStart(2, "0")}`;

  const [costs, tags, prevCosts] = await Promise.all([
    getCosts(month),
    getCostsByTag(month),
    getCosts(prevMonth).catch(() => ({ total: 0, dailyCosts: [] })),
  ]);

  // Calcul de l'évolution en %
  const evolution = prevCosts.total > 0
    ? ((costs.total - prevCosts.total) / prevCosts.total) * 100
    : null;

  const teamTotals: Record<string, number> = {};
  for (const tag of tags.tagCosts) {
    teamTotals[tag.team] = (teamTotals[tag.team] || 0) + tag.totalCost;
  }
  const teamData = Object.entries(teamTotals)
    .map(([team, total]) => ({ team, total: Math.round(total * 100) / 100 }))
    .sort((a, b) => b.total - a.total);

  const avgPerDay = costs.total / (costs.dailyCosts.length || 1);

  return (
    <div>
      <div className="mb-6 md:mb-8 flex items-start justify-between gap-4 flex-wrap">
        <div>
          <h1 className="text-2xl md:text-3xl font-bold text-[#1E1B4B]">Dashboard FinOps</h1>
          <p className="text-sm md:text-base text-[#475569] mt-1">Analyse des coûts AWS — {formatMonth(month)}</p>
        </div>
        <MonthSelector current={month} />
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 mb-6 md:mb-8">
        <div className="bg-white rounded-xl p-5 md:p-6 border border-[#E0E7FF]">
          <div className="flex items-center gap-2 mb-2">
            <div className="w-8 h-8 rounded-lg bg-[#6366F1]/10 flex items-center justify-center shrink-0">
              <svg className="w-4 h-4 text-[#6366F1]" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                <path strokeLinecap="round" strokeLinejoin="round" d="M12 6v12m-3-2.818l.879.659c1.171.879 3.07.879 4.242 0 1.172-.879 1.172-2.303 0-3.182C13.536 12.219 12.768 12 12 12c-2.21 0-4-1.79-4-4s1.79-4 4-4 4 1.79 4 4" />
              </svg>
            </div>
            <p className="text-sm text-[#475569]">Total du mois</p>
          </div>
          <p className="text-2xl md:text-3xl font-bold text-[#1E1B4B]">${costs.total.toFixed(2)}</p>
          {evolution !== null && (
            <div className="mt-2 flex items-center gap-1">
              <span
                className={`inline-flex items-center gap-1 text-xs font-semibold px-2 py-0.5 rounded ${
                  evolution > 0
                    ? "bg-[#FEE2E2] text-[#991B1B]"
                    : evolution < 0
                    ? "bg-[#D1FAE5] text-[#065F46]"
                    : "bg-[#F5F3FF] text-[#475569]"
                }`}
              >
                {evolution > 0 ? "▲" : evolution < 0 ? "▼" : "—"}{" "}
                {Math.abs(evolution).toFixed(1)}%
              </span>
              <span className="text-xs text-[#475569]">vs {formatMonth(prevMonth)}</span>
            </div>
          )}
        </div>

        <div className="bg-white rounded-xl p-5 md:p-6 border border-[#E0E7FF]">
          <div className="flex items-center gap-2 mb-2">
            <div className="w-8 h-8 rounded-lg bg-[#818CF8]/10 flex items-center justify-center shrink-0">
              <svg className="w-4 h-4 text-[#818CF8]" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                <path strokeLinecap="round" strokeLinejoin="round" d="M3 13.125C3 12.504 3.504 12 4.125 12h2.25c.621 0 1.125.504 1.125 1.125v6.75C7.5 20.496 6.996 21 6.375 21h-2.25A1.125 1.125 0 013 19.875v-6.75zM9.75 8.625c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125v11.25c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V8.625z" />
              </svg>
            </div>
            <p className="text-sm text-[#475569]">Moyenne / jour</p>
          </div>
          <p className="text-2xl md:text-3xl font-bold text-[#1E1B4B]">${avgPerDay.toFixed(2)}</p>
        </div>

        <div className="bg-white rounded-xl p-5 md:p-6 border border-[#E0E7FF] sm:col-span-2 lg:col-span-1">
          <div className="flex items-center gap-2 mb-2">
            <div className="w-8 h-8 rounded-lg bg-[#10B981]/10 flex items-center justify-center shrink-0">
              <svg className="w-4 h-4 text-[#10B981]" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                <path strokeLinecap="round" strokeLinejoin="round" d="M18 18.72a9.094 9.094 0 003.741-.479 3 3 0 00-4.682-2.72m.94 3.198l.001.031c0 .225-.012.447-.037.666A11.944 11.944 0 0112 21c-2.17 0-4.207-.576-5.963-1.584A6.062 6.062 0 016 18.719m12 0a5.971 5.971 0 00-.941-3.197m0 0A5.995 5.995 0 0012 12.75a5.995 5.995 0 00-5.058 2.772m0 0a3 3 0 00-4.681 2.72 8.986 8.986 0 003.74.477m.94-3.197a5.971 5.971 0 00-.94 3.197M15 6.75a3 3 0 11-6 0 3 3 0 016 0zm6 3a2.25 2.25 0 11-4.5 0 2.25 2.25 0 014.5 0zm-13.5 0a2.25 2.25 0 11-4.5 0 2.25 2.25 0 014.5 0z" />
              </svg>
            </div>
            <p className="text-sm text-[#475569]">Équipes</p>
          </div>
          <p className="text-2xl md:text-3xl font-bold text-[#1E1B4B]">{teamData.length}</p>
        </div>
      </div>

      <OverviewCharts
        dailyCosts={costs.dailyCosts.map((d) => ({
          date: d.SK,
          cost: Math.round(d.totalCost * 100) / 100,
        }))}
        teamData={teamData}
      />
    </div>
  );
}
