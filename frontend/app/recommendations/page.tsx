import { getRecommendations } from "@/lib/api";

const severityColors: Record<string, string> = {
  high: "bg-red-100 text-red-800",
  medium: "bg-yellow-100 text-yellow-800",
  low: "bg-green-100 text-green-800",
};

export default async function RecommendationsPage() {
  const data = await getRecommendations();

  return (
    <div>
      <h1 className="text-2xl font-bold mb-2">Recommandations</h1>
      <p className="text-gray-600 mb-8">
        {data.count} recommandation{data.count > 1 ? "s" : ""} active{data.count > 1 ? "s" : ""}
      </p>

      {data.count === 0 ? (
        <div className="bg-green-50 border border-green-200 rounded-lg p-6 text-center">
          <p className="text-green-800 font-medium">Aucun gaspillage detecte. Beau travail !</p>
        </div>
      ) : (
        <div className="space-y-4">
          {data.recommendations.map((rec) => (
            <div key={rec.SK} className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center gap-3 mb-2">
                <span
                  className={`px-2 py-1 rounded text-xs font-semibold ${
                    severityColors[rec.severity] || "bg-gray-100 text-gray-800"
                  }`}
                >
                  {rec.severity.toUpperCase()}
                </span>
                <span className="text-xs text-gray-400">{rec.type}</span>
              </div>
              <h3 className="text-lg font-semibold mb-1">{rec.title}</h3>
              <p className="text-gray-600">{rec.description}</p>
              {rec.estimatedWaste && (
                <p className="mt-2 text-sm font-medium text-red-600">
                  Gaspillage estime : ${rec.estimatedWaste}/mois
                </p>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
