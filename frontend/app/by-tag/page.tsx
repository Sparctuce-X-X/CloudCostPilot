import { getCostsByTag } from "@/lib/api";

export default async function ByTagPage() {
  const month = "2026-03";
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
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-[#1E1B4B]">Coûts par équipe</h1>
        <p className="text-[#475569] mt-1">Mois : {month}</p>
      </div>

      <div className="bg-white rounded-xl border border-[#E0E7FF] overflow-hidden">
        <table className="w-full">
          <thead className="bg-[#F5F3FF]">
            <tr className="text-left text-xs uppercase tracking-wider text-[#475569]">
              <th className="px-6 py-3 font-semibold">Équipe</th>
              <th className="px-6 py-3 text-right font-semibold">Total</th>
              <th className="px-6 py-3 text-right font-semibold">% du total</th>
              <th className="px-6 py-3 font-semibold">Répartition</th>
            </tr>
          </thead>
          <tbody>
            {teams.map((t) => {
              const pct = grandTotal > 0 ? (t.total / grandTotal) * 100 : 0;
              const isUntagged = t.team === "untagged";
              return (
                <tr key={t.team} className="border-t border-[#E0E7FF] hover:bg-[#F5F3FF] transition-colors duration-150">
                  <td className="px-6 py-4 font-medium">
                    {isUntagged ? (
                      <span className="inline-flex items-center gap-2 text-[#EF4444]">
                        <span className="w-2 h-2 rounded-full bg-[#EF4444]" />
                        {t.team}
                      </span>
                    ) : (
                      <span className="text-[#1E1B4B]">{t.team}</span>
                    )}
                  </td>
                  <td className="px-6 py-4 text-right text-[#1E1B4B]">${t.total.toFixed(2)}</td>
                  <td className="px-6 py-4 text-right text-[#475569]">{pct.toFixed(1)}%</td>
                  <td className="px-6 py-4">
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
            <tr className="font-bold text-[#1E1B4B]">
              <td className="px-6 py-4">Total</td>
              <td className="px-6 py-4 text-right">${grandTotal.toFixed(2)}</td>
              <td className="px-6 py-4 text-right">100%</td>
              <td className="px-6 py-4" />
            </tr>
          </tfoot>
        </table>
      </div>
    </div>
  );
}
