import { getCosts, getCostsByTag } from "@/lib/api";
import OverviewCharts from "@/components/OverviewCharts";

export default async function Home() {
  const month = "2026-03";
  const [costs, tags] = await Promise.all([
    getCosts(month),
    getCostsByTag(month),
  ]);

  // Agréger les coûts par équipe
  const teamTotals: Record<string, number> = {};
  for (const tag of tags.tagCosts) {
    teamTotals[tag.team] = (teamTotals[tag.team] || 0) + tag.totalCost;
  }
  const teamData = Object.entries(teamTotals)
    .map(([team, total]) => ({ team, total: Math.round(total * 100) / 100 }))
    .sort((a, b) => b.total - a.total);

  return (
    <div>
      <h1 className="text-2xl font-bold mb-2">Dashboard FinOps</h1>
      <p className="text-gray-600 mb-8">Mois : {month}</p>

      {/* KPIs */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        <div className="bg-white rounded-lg shadow p-6 border border-gray-200">
          <p className="text-sm text-gray-600">Total du mois</p>
          <p className="text-3xl font-bold">${costs.total.toFixed(2)}</p>
        </div>
        <div className="bg-white rounded-lg shadow p-6 border border-gray-200">
          <p className="text-sm text-gray-600">Moyenne / jour</p>
          <p className="text-3xl font-bold">
            ${(costs.total / (costs.dailyCosts.length || 1)).toFixed(2)}
          </p>
        </div>
        <div className="bg-white rounded-lg shadow p-6 border border-gray-200">
          <p className="text-sm text-gray-600">Equipes</p>
          <p className="text-3xl font-bold">{teamData.length}</p>
        </div>
      </div>

      {/* Charts */}
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
