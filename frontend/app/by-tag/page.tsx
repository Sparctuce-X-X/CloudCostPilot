import { getCostsByTag } from "@/lib/api";
import MonthSelector from "@/components/MonthSelector";
import { formatMonth } from "@/lib/format";

const DEFAULT_MONTH = "2026-03";

export default async function ByTagPage({
  searchParams,
}: {
  searchParams: Promise<{ month?: string }>;
}) {
  const params = await searchParams;
  const month = params.month || DEFAULT_MONTH;
  const data = await getCostsByTag(month);

  const teamTotals: Record<string, number> = {};
  for (const tag of data.tagCosts) {
    teamTotals[tag.team] = (teamTotals[tag.team] || 0) + tag.totalCost;
  }
  const teams = Object.entries(teamTotals)
    .map(([team, total]) => ({ team, total: Math.round(total * 100) / 100 }))
    .sort((a, b) => b.total - a.total);

  const grandTotal = teams.reduce((s, t) => s + t.total, 0);

  return (
    <div>
      <div className="mb-6 md:mb-8 flex items-start justify-between gap-4 flex-wrap">
        <div>
          <h1 className="text-2xl md:text-3xl font-bold text-[#1E1B4B]">Coûts par équipe</h1>
          <p className="text-sm md:text-base text-[#475569] mt-1">Répartition — {formatMonth(month)}</p>
        </div>
        <MonthSelector current={month} />
      </div>

      <div className="bg-white rounded-xl border border-[#E0E7FF] overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full min-w-[600px]">
            <thead className="bg-[#F5F3FF]">
              <tr className="text-left text-xs uppercase tracking-wider text-[#475569]">
                <th className="px-4 md:px-6 py-3 font-semibold">Équipe</th>
                <th className="px-4 md:px-6 py-3 text-right font-semibold">Total</th>
                <th className="px-4 md:px-6 py-3 text-right font-semibold hidden sm:table-cell">% du total</th>
                <th className="px-4 md:px-6 py-3 font-semibold">Répartition</th>
              </tr>
            </thead>
            <tbody>
              {teams.map((t) => {
                const pct = grandTotal > 0 ? (t.total / grandTotal) * 100 : 0;
                const isUntagged = t.team === "untagged";
                return (
                  <tr key={t.team} className="border-t border-[#E0E7FF] hover:bg-[#F5F3FF] transition-colors duration-150">
                    <td className="px-4 md:px-6 py-4 font-medium">
                      {isUntagged ? (
                        <span className="inline-flex items-center gap-2 text-[#EF4444] text-sm md:text-base">
                          <span className="w-2 h-2 rounded-full bg-[#EF4444]" />
                          {t.team}
                        </span>
                      ) : (
                        <span className="text-[#1E1B4B] text-sm md:text-base">{t.team}</span>
                      )}
                    </td>
                    <td className="px-4 md:px-6 py-4 text-right text-[#1E1B4B] text-sm md:text-base">${t.total.toFixed(2)}</td>
                    <td className="px-4 md:px-6 py-4 text-right text-[#475569] text-sm md:text-base hidden sm:table-cell">{pct.toFixed(1)}%</td>
                    <td className="px-4 md:px-6 py-4 min-w-[120px]">
                      <div className="w-full bg-[#F5F3FF] rounded-full h-2">
                        <div
                          className={`h-2 rounded-full transition-all duration-300 ${
                            isUntagged ? "bg-[#EF4444]" : "bg-[#6366F1]"
                          }`}
                          style={{ width: `${pct}%` }}
                        />
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
            <tfoot className="bg-[#F5F3FF] border-t-2 border-[#E0E7FF]">
              <tr className="font-bold text-[#1E1B4B] text-sm md:text-base">
                <td className="px-4 md:px-6 py-4">Total</td>
                <td className="px-4 md:px-6 py-4 text-right">${grandTotal.toFixed(2)}</td>
                <td className="px-4 md:px-6 py-4 text-right hidden sm:table-cell">100%</td>
                <td className="px-4 md:px-6 py-4" />
              </tr>
            </tfoot>
          </table>
        </div>
      </div>
    </div>
  );
}
