import { useEffect, useRef, useState } from "react";
import ReactMarkdown from "react-markdown";
import { ask } from "./api";
import { linkifyCitations } from "./citations";
import type { ChatMessage, HistoryTurn } from "./types";
import "./App.css";

// Movie links should open in a new tab rather than navigating away from the chat.
const markdownComponents = {
  a: (props: React.ComponentPropsWithoutRef<"a">) => (
    <a {...props} target="_blank" rel="noopener noreferrer" />
  ),
};

const MAX_HISTORY_TURNS = 5;

function cacheKey(question: string): string {
  return question.trim().split(/\s+/).join(" ").toLowerCase();
}

function App() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

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

    const key = cacheKey(question);
    const cached = cacheRef.current.get(key);
    if (cached) {
      setMessages((prev) => [...prev, cached]);
      setLoading(false);
      return;
    }

    try {
      const result = await ask(question, historyRef.current);

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
      <header className="chat-header">MoviesRAG</header>

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

export default App;
