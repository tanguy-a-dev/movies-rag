export interface HistoryTurn {
  question: string;
  answer: string;
  movie_ids: number[];
}

export interface Source {
  movie_id: number | null;
  title: string;
  genres: string | null;
  overview: string | null;
  poster_url: string | null;
  vote_average: number | null;
  popularity: number | null;
  release_date: string | null;
}

export interface AskResponse {
  question: string;
  answer: string;
  sources: Source[];
  validated: boolean;
  hallucinated_ids: number[];
}

export interface SearchResponse {
  question: string;
  results: Source[];
}

export interface ChatMessage {
  role: "user" | "assistant" | "error";
  content: string;
}
