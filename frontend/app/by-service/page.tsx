import { getCostsByService } from "@/lib/api";
import ServiceChart from "@/components/ServiceChart";
import MonthSelector from "@/components/MonthSelector";
import { formatMonth, formatDate } from "@/lib/format";

const DEFAULT_MONTH = "2026-03";

export default async function ByServicePage({
  searchParams,
}: {
  searchParams: Promise<{ month?: string }>;
}) {
  const params = await searchParams;
  const month = params.month || DEFAULT_MONTH;
  // On prend le 15 du mois par défaut (milieu de période)
  const date = `${month}-15`;
  const data = await getCostsByService(date);

  const services = data.services
    .map((s) => ({ name: s.SK, cost: Math.round(s.totalCost * 100) / 100 }))
    .sort((a, b) => b.cost - a.cost);

  const total = services.reduce((s, x) => s + x.cost, 0);

  return (
    <div>
      <div className="mb-6 md:mb-8 flex items-start justify-between gap-4 flex-wrap">
        <div>
          <h1 className="text-2xl md:text-3xl font-bold text-[#1E1B4B]">Coûts par service</h1>
          <p className="text-sm md:text-base text-[#475569] mt-1">
            Répartition au {formatDate(date)} — {formatMonth(month)}
          </p>
        </div>
        <MonthSelector current={month} />
      </div>

      <ServiceChart services={services} />

      <div className="bg-white rounded-xl mt-4 md:mt-6 border border-[#E0E7FF] overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full min-w-[480px]">
            <thead className="bg-[#F5F3FF]">
              <tr className="text-left text-xs uppercase tracking-wider text-[#475569]">
                <th className="px-4 md:px-6 py-3 font-semibold">Service</th>
                <th className="px-4 md:px-6 py-3 text-right font-semibold">Coût</th>
                <th className="px-4 md:px-6 py-3 text-right font-semibold">%</th>
              </tr>
            </thead>
            <tbody>
              {services.map((s) => {
                const pct = total > 0 ? (s.cost / total) * 100 : 0;
                return (
                  <tr key={s.name} className="border-t border-[#E0E7FF] hover:bg-[#F5F3FF] transition-colors duration-150">
                    <td className="px-4 md:px-6 py-4 font-medium text-[#1E1B4B] text-sm md:text-base">{s.name}</td>
                    <td className="px-4 md:px-6 py-4 text-right text-[#1E1B4B] text-sm md:text-base">${s.cost.toFixed(2)}</td>
                    <td className="px-4 md:px-6 py-4 text-right text-[#475569] text-sm md:text-base">{pct.toFixed(1)}%</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
