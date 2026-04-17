import { getRecommendations } from "@/lib/api";

const severityConfig: Record<string, { bg: string; text: string; dot: string; label: string }> = {
  high: { bg: "bg-[#FEE2E2]", text: "text-[#991B1B]", dot: "bg-[#EF4444]", label: "Critique" },
  medium: { bg: "bg-[#FEF3C7]", text: "text-[#92400E]", dot: "bg-[#F59E0B]", label: "Moyen" },
  low: { bg: "bg-[#D1FAE5]", text: "text-[#065F46]", dot: "bg-[#10B981]", label: "Faible" },
};

export default async function RecommendationsPage() {
  const data = await getRecommendations();

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-[#1E1B4B]">Recommandations</h1>
        <p className="text-[#475569] mt-1">
          {data.count} recommandation{data.count > 1 ? "s" : ""} active{data.count > 1 ? "s" : ""}
        </p>
      </div>

      {data.count === 0 ? (
        <div className="bg-[#D1FAE5] border border-[#10B981] rounded-xl p-8 text-center">
          <div className="w-12 h-12 mx-auto mb-3 rounded-full bg-[#10B981] flex items-center justify-center">
            <svg className="w-6 h-6 text-white" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3">
              <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
            </svg>
          </div>
          <p className="text-[#065F46] font-semibold">Aucun gaspillage détecté</p>
          <p className="text-[#065F46]/80 text-sm mt-1">Ton infrastructure est optimisée.</p>
        </div>
      ) : (
        <div className="space-y-3">
          {data.recommendations.map((rec) => {
            const cfg = severityConfig[rec.severity] || severityConfig.low;
            return (
              <div
                key={rec.SK}
                className="bg-white rounded-xl p-5 border border-[#E0E7FF] hover:border-[#6366F1] transition-colors duration-150"
              >
                <div className="flex items-start gap-3">
                  <span className={`mt-1 w-2 h-2 rounded-full ${cfg.dot}`} />
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1 flex-wrap">
                      <span className={`${cfg.bg} ${cfg.text} px-2 py-0.5 rounded text-xs font-semibold`}>
                        {cfg.label}
                      </span>
                      <span className="text-xs text-[#475569] font-mono">{rec.type}</span>
                    </div>
                    <h3 className="text-base font-semibold text-[#1E1B4B] mb-1">{rec.title}</h3>
                    <p className="text-sm text-[#475569]">{rec.description}</p>
                    {rec.estimatedWaste && (
                      <div className="mt-3 inline-flex items-center gap-2 bg-[#FEE2E2] text-[#991B1B] px-3 py-1 rounded-lg text-sm font-semibold">
                        Gaspillage estimé : ${rec.estimatedWaste}/mois
                      </div>
                    )}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
