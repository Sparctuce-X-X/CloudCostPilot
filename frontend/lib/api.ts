// lib/api.ts
// Client API pour communiquer avec le backend CloudCostPilot sur AWS.

const API_URL = process.env.NEXT_PUBLIC_API_URL || "";

async function fetchAPI<T>(path: string, params?: Record<string, string>): Promise<T> {
  // Construire l'URL manuellement pour éviter les problèmes avec new URL()
  const queryString = params
    ? "?" + Object.entries(params).map(([k, v]) => `${k}=${encodeURIComponent(v)}`).join("&")
    : "";
  const fullUrl = `${API_URL}${path}${queryString}`;

  console.log("[API] Fetching:", fullUrl);
  const res = await fetch(fullUrl, { cache: "no-store" });
  if (!res.ok) {
    throw new Error(`API error: ${res.status} ${res.statusText}`);
  }
  return res.json();
}

// --- Types ---

export interface DailyCost {
  PK: string;
  SK: string;
  totalCost: number;
  itemCount: number;
  currency: string;
}

export interface ServiceCost {
  PK: string;
  SK: string;
  totalCost: number;
  itemCount: number;
}

export interface TagCost {
  PK: string;
  SK: string;
  team: string;
  date: string;
  totalCost: number;
}

export interface Recommendation {
  PK: string;
  SK: string;
  type: string;
  severity: string;
  title: string;
  description: string;
  estimatedWaste?: number;
  status: string;
  detectedAt: string;
}

// --- API calls ---

export async function getCosts(month: string) {
  return fetchAPI<{ month: string; dailyCosts: DailyCost[]; total: number }>("/costs", { month });
}

export async function getCostsByService(date: string) {
  return fetchAPI<{ date: string; services: ServiceCost[] }>("/costs/by-service", { date });
}

export async function getCostsByTag(month: string) {
  return fetchAPI<{ month: string; tagCosts: TagCost[] }>("/costs/by-tag", { month });
}

export async function getRecommendations() {
  return fetchAPI<{ recommendations: Recommendation[]; count: number }>("/recommendations");
}

export async function getAnomalies(month: string) {
  return fetchAPI<{ month: string; anomalies: Recommendation[]; count: number }>("/anomalies", { month });
}
