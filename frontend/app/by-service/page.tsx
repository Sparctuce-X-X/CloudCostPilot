import { getCostsByService } from "@/lib/api";
import ServiceChart from "@/components/ServiceChart";

export default async function ByServicePage() {
  const date = "2026-03-15";
  const data = await getCostsByService(date);

  const services = data.services
    .map((s) => ({ name: s.SK, cost: Math.round(s.totalCost * 100) / 100 }))
    .sort((a, b) => b.cost - a.cost);

  const total = services.reduce((s, x) => s + x.cost, 0);

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-[#1E1B4B]">Coûts par service</h1>
        <p className="text-[#475569] mt-1">Date : {date}</p>
      </div>

      <ServiceChart services={services} />

      <div className="bg-white rounded-xl mt-6 border border-[#E0E7FF] overflow-hidden">
        <table className="w-full">
          <thead className="bg-[#F5F3FF]">
            <tr className="text-left text-xs uppercase tracking-wider text-[#475569]">
              <th className="px-6 py-3 font-semibold">Service</th>
              <th className="px-6 py-3 text-right font-semibold">Coût</th>
              <th className="px-6 py-3 text-right font-semibold">%</th>
            </tr>
          </thead>
          <tbody>
            {services.map((s) => {
              const pct = total > 0 ? (s.cost / total) * 100 : 0;
              return (
                <tr key={s.name} className="border-t border-[#E0E7FF] hover:bg-[#F5F3FF] transition-colors duration-150">
                  <td className="px-6 py-4 font-medium text-[#1E1B4B]">{s.name}</td>
                  <td className="px-6 py-4 text-right text-[#1E1B4B]">${s.cost.toFixed(2)}</td>
                  <td className="px-6 py-4 text-right text-[#475569]">{pct.toFixed(1)}%</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
