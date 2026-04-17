import { getCostsByTag } from "@/lib/api";

export default async function ByTagPage() {
  const month = "2026-03";
  const data = await getCostsByTag(month);

  // Agréger par équipe
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
      <h1 className="text-2xl font-bold mb-2">Coûts par equipe</h1>
      <p className="text-gray-600 mb-8">Mois : {month}</p>

      <div className="bg-white rounded-lg shadow">
        <table className="w-full">
          <thead>
            <tr className="border-b text-left text-sm text-gray-600">
              <th className="p-4">Equipe</th>
              <th className="p-4 text-right">Total</th>
              <th className="p-4 text-right">% du total</th>
              <th className="p-4">Repartition</th>
            </tr>
          </thead>
          <tbody>
            {teams.map((t) => {
              const pct = grandTotal > 0 ? (t.total / grandTotal) * 100 : 0;
              return (
                <tr key={t.team} className="border-b last:border-0 hover:bg-gray-50">
                  <td className="p-4 font-medium">
                    {t.team === "untagged" ? (
                      <span className="text-red-600">{t.team}</span>
                    ) : (
                      t.team
                    )}
                  </td>
                  <td className="p-4 text-right">${t.total.toFixed(2)}</td>
                  <td className="p-4 text-right">{pct.toFixed(1)}%</td>
                  <td className="p-4">
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className={`h-2 rounded-full ${
                          t.team === "untagged" ? "bg-red-500" : "bg-blue-500"
                        }`}
                        style={{ width: `${pct}%` }}
                      />
                    </div>
                  </td>
                </tr>
              );
            })}
          </tbody>
          <tfoot>
            <tr className="bg-gray-50 font-bold">
              <td className="p-4">Total</td>
              <td className="p-4 text-right">${grandTotal.toFixed(2)}</td>
              <td className="p-4 text-right">100%</td>
              <td className="p-4" />
            </tr>
          </tfoot>
        </table>
      </div>
    </div>
  );
}
