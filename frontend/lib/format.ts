// lib/format.ts — Utilitaires de formatage.

const MONTHS_FR = [
  "Janvier", "Février", "Mars", "Avril", "Mai", "Juin",
  "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre",
];

/** Formate "2026-03" en "Mars 2026". */
export function formatMonth(yyyymm: string): string {
  const [year, month] = yyyymm.split("-").map(Number);
  if (!year || !month || month < 1 || month > 12) return yyyymm;
  return `${MONTHS_FR[month - 1]} ${year}`;
}

/** Formate "2026-03-15" en "15 Mars 2026". */
export function formatDate(yyyymmdd: string): string {
  const [year, month, day] = yyyymmdd.split("-").map(Number);
  if (!year || !month || !day) return yyyymmdd;
  return `${day} ${MONTHS_FR[month - 1]} ${year}`;
}
