// Mirrors ui/chainlit.py's CITATION_STRIP_PATTERN/strip_citations: strips "[id: X]"
// or "[id: X: title]" citation markers from LLM answers, keeping any trailing text.
const CITATION_PATTERN = /[[(](?:id:\s*)?\d+(?:[:\s]([^\])]*))?[\])]/g;

export function stripCitations(text: string): string {
  const stripped = text.replace(CITATION_PATTERN, (_match, trailing) => trailing ?? "");
  return stripped.replace(/[ \t]{2,}/g, " ").trim();
}
