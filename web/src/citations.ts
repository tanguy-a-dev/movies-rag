import { tmdbUrl } from "./tmdb";

// Matches the "[id: X]" (or "[id: X: trailing text]") citations the LLM is
// prompted to emit (see src/services/generation.py's PROMPT_TEMPLATE). Captures
// the numeric movie id so it can be turned into a link instead of just stripped.
const CITATION_PATTERN = /[[(](?:id:\s*)?(\d+)(?:[:\s][^\])]*)?[\])]/g;

export function linkifyCitations(text: string): string {
  const linked = text.replace(CITATION_PATTERN, (_match, id) => `[🔗](${tmdbUrl(id)})`);
  return linked.replace(/[ \t]{2,}/g, " ").trim();
}
