import { getCostsByService } from "@/lib/api";
import ServiceChart from "@/components/ServiceChart";

export default async function ByServicePage() {
  const date = "2026-03-15";
  const data = await getCostsByService(date);

  const services = data.services
    .map((s) => ({ name: s.SK, cost: Math.round(s.totalCost * 100) / 100 }))
    .sort((a, b) => b.cost - a.cost);

  return (
    <div>
      <h1 className="text-2xl font-bold mb-2">Coûts par service</h1>
      <p className="text-gray-600 mb-8">Date : {date}</p>

      <ServiceChart services={services} />

      {/* Tableau détaillé */}
      <div className="bg-white rounded-lg shadow mt-6">
        <table className="w-full">
          <thead>
            <tr className="border-b text-left text-sm text-gray-600">
              <th className="p-4">Service</th>
              <th className="p-4 text-right">Coût</th>
            </tr>
          </thead>
          <tbody>
            {services.map((s) => (
              <tr key={s.name} className="border-b last:border-0 hover:bg-gray-50">
                <td className="p-4 font-medium">{s.name}</td>
                <td className="p-4 text-right">${s.cost.toFixed(2)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
