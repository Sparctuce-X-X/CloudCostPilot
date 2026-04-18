import { getAnomalies } from "@/lib/api";
import MonthSelector from "@/components/MonthSelector";
import { formatMonth } from "@/lib/format";

const DEFAULT_MONTH = "2026-03";

export default async function AnomaliesPage({
  searchParams,
}: {
  searchParams: Promise<{ month?: string }>;
}) {
  const params = await searchParams;
  const month = params.month || DEFAULT_MONTH;
  const data = await getAnomalies(month);

  return (
    <div>
      <div className="mb-6 md:mb-8 flex items-start justify-between gap-4 flex-wrap">
        <div>
          <h1 className="text-2xl md:text-3xl font-bold text-[#1E1B4B]">Anomalies de coût</h1>
          <p className="text-sm md:text-base text-[#475569] mt-1">
            Pics détectés automatiquement (moyenne mobile 7 jours, seuil +50%)
          </p>
        </div>
        <MonthSelector current={month} />
      </div>

      {data.count === 0 ? (
        <div className="bg-[#D1FAE5] border border-[#10B981] rounded-xl p-6 md:p-8 text-center">
          <div className="w-12 h-12 mx-auto mb-3 rounded-full bg-[#10B981] flex items-center justify-center">
            <svg className="w-6 h-6 text-white" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3">
              <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
            </svg>
          </div>
          <p className="text-[#065F46] font-semibold">Aucune anomalie détectée</p>
          <p className="text-[#065F46]/80 text-sm mt-1">Tes coûts sont stables sur ce mois.</p>
        </div>
      ) : (
        <>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
            <div className="bg-white rounded-xl p-5 border border-[#E0E7FF]">
              <p className="text-sm text-[#475569] mb-2">Anomalies détectées</p>
              <p className="text-3xl font-bold text-[#EF4444]">{data.count}</p>
            </div>
            <div className="bg-white rounded-xl p-5 border border-[#E0E7FF]">
              <p className="text-sm text-[#475569] mb-2">Mois analysé</p>
              <p className="text-2xl font-bold text-[#1E1B4B]">{formatMonth(month)}</p>
            </div>
            <div className="bg-white rounded-xl p-5 border border-[#E0E7FF] sm:col-span-2 lg:col-span-1">
              <p className="text-sm text-[#475569] mb-2">Règle active</p>
              <p className="text-base font-semibold text-[#1E1B4B]">Moyenne mobile 7j</p>
              <p className="text-xs text-[#475569] mt-1">Seuil d&apos;alerte : +50%</p>
            </div>
          </div>

          <div className="space-y-3">
            {data.anomalies.map((anom) => (
              <div key={anom.SK} className="bg-white rounded-xl p-5 border-l-4 border-l-[#EF4444] border border-[#E0E7FF]">
                <div className="flex items-start gap-3">
                  <div className="w-10 h-10 rounded-lg bg-[#FEE2E2] flex items-center justify-center shrink-0">
                    <svg className="w-5 h-5 text-[#EF4444]" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                      <path strokeLinecap="round" strokeLinejoin="round" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                    </svg>
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1 flex-wrap">
                      <span className="bg-[#FEE2E2] text-[#991B1B] px-2 py-0.5 rounded text-xs font-semibold">
                        ANOMALIE
                      </span>
                      <span className="text-xs text-[#475569] font-mono">{anom.type || "cost-spike"}</span>
                    </div>
                    <h3 className="text-base font-semibold text-[#1E1B4B] mb-1">{anom.title}</h3>
                    <p className="text-sm text-[#475569]">{anom.description}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );
}
