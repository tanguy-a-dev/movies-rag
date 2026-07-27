import type { AskResponse, HistoryTurn, SearchResponse } from "./types";

const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

async function post<T>(path: string, body: unknown): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });

  if (!response.ok) {
    const detail = await response.json().catch(() => null);
    throw new Error(detail?.detail ?? `Request failed with status ${response.status}`);
  }

  return response.json();
}

export interface MovieFilters {
  includeAdult: boolean;
  popularOnly: boolean;
  highlyRatedOnly: boolean;
}

export function ask(
  question: string,
  history: HistoryTurn[],
  filters: MovieFilters,
): Promise<AskResponse> {
  return post("/ask", {
    question,
    history,
    include_adult: filters.includeAdult,
    popular_only: filters.popularOnly,
    highly_rated_only: filters.highlyRatedOnly,
  });
}

export function search(
  question: string,
  topK: number,
  filters: MovieFilters,
): Promise<SearchResponse> {
  return post("/search", {
    question,
    top_k: topK,
    include_adult: filters.includeAdult,
    popular_only: filters.popularOnly,
    highly_rated_only: filters.highlyRatedOnly,
  });
}
