import { useEffect, useRef, useState } from "react";
import ReactMarkdown from "react-markdown";
import { ask } from "../api";
import type { MovieFilters } from "../api";
import { linkifyCitations } from "../citations";
import type { ChatMessage, HistoryTurn } from "../types";

// Movie links should open in a new tab rather than navigating away from the chat.
const markdownComponents = {
  a: (props: React.ComponentPropsWithoutRef<"a">) => (
    <a {...props} target="_blank" rel="noopener noreferrer" />
  ),
};

const MAX_HISTORY_TURNS = 5;

function cacheKey(question: string, filters: MovieFilters): string {
  const normalized = question.trim().split(/\s+/).join(" ").toLowerCase();
  return `${filters.includeAdult}:${filters.popularOnly}:${filters.highlyRatedOnly}:${normalized}`;
}

function ChatPage() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [includeAdult, setIncludeAdult] = useState(false);
  const [popularOnly, setPopularOnly] = useState(true);
  const [highlyRatedOnly, setHighlyRatedOnly] = useState(false);

  const historyRef = useRef<HistoryTurn[]>([]);
  const cacheRef = useRef<Map<string, ChatMessage>>(new Map());
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    const question = input.trim();
    if (!question || loading) return;

    setInput("");
    setMessages((prev) => [...prev, { role: "user", content: question }]);
    setLoading(true);

    const filters: MovieFilters = { includeAdult, popularOnly, highlyRatedOnly };
    const key = cacheKey(question, filters);
    const cached = cacheRef.current.get(key);
    if (cached) {
      setMessages((prev) => [...prev, cached]);
      setLoading(false);
      return;
    }

    try {
      const result = await ask(question, historyRef.current, filters);

      let content = linkifyCitations(result.answer);
      if (!result.validated) {
        content +=
          "\n\n⚠️ This answer may reference a movie not found in our database " +
          `(ids: ${result.hallucinated_ids.join(", ")}).`;
      }

      const message: ChatMessage = { role: "assistant", content };
      cacheRef.current.set(key, message);

      historyRef.current = [
        ...historyRef.current,
        {
          question,
          answer: result.answer,
          movie_ids: result.sources
            .map((s) => s.movie_id)
            .filter((id): id is number => id !== null),
        },
      ].slice(-MAX_HISTORY_TURNS);

      setMessages((prev) => [...prev, message]);
    } catch (err) {
      const detail = err instanceof Error ? err.message : "Could not reach the API.";
      setMessages((prev) => [...prev, { role: "error", content: detail }]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="chat">
      <div className="chat-options">
        <label className="toggle-control" htmlFor="chat-include-adult">
          <input
            id="chat-include-adult"
            type="checkbox"
            checked={includeAdult}
            onChange={(e) => setIncludeAdult(e.target.checked)}
          />
          Show mature content
        </label>

        <label className="toggle-control" htmlFor="chat-popular-only">
          <input
            id="chat-popular-only"
            type="checkbox"
            checked={popularOnly}
            onChange={(e) => setPopularOnly(e.target.checked)}
          />
          Popular movies only
        </label>

        <label className="toggle-control" htmlFor="chat-highly-rated-only">
          <input
            id="chat-highly-rated-only"
            type="checkbox"
            checked={highlyRatedOnly}
            onChange={(e) => setHighlyRatedOnly(e.target.checked)}
          />
          Highly rated only
        </label>
      </div>

      <div className="chat-messages">
        {messages.map((message, i) => (
          <div key={i} className={`bubble ${message.role}`}>
            {message.role === "assistant" ? (
              <ReactMarkdown components={markdownComponents}>
                {message.content}
              </ReactMarkdown>
            ) : (
              message.content
            )}
          </div>
        ))}
        {loading && <div className="bubble assistant loading">Thinking…</div>}
        <div ref={bottomRef} />
      </div>

      <form className="chat-input" onSubmit={handleSubmit}>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask for a movie recommendation…"
          disabled={loading}
        />
        <button type="submit" disabled={loading || !input.trim()}>
          Send
        </button>
      </form>
    </div>
  );
}

export default ChatPage;
