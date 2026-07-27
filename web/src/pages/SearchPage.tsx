import { useState } from "react";
import { search } from "../api";
import { tmdbUrl } from "../tmdb";
import type { Source } from "../types";

function MovieCard({ movie }: { movie: Source }) {
  const content = (
    <>
      <div className="movie-poster">
        {movie.poster_url ? (
          <img src={movie.poster_url} alt={movie.title} loading="lazy" />
        ) : (
          <div className="movie-poster-placeholder">🎬</div>
        )}
      </div>
      <div className="movie-info">
        <h3>{movie.title}</h3>
        <div className="movie-meta">
          {movie.release_date && <span>{movie.release_date.slice(0, 4)}</span>}
          {movie.vote_average != null && <span>⭐ {movie.vote_average.toFixed(1)}</span>}
        </div>
        {movie.genres && <div className="movie-genres">{movie.genres}</div>}
      </div>
    </>
  );

  if (movie.movie_id == null) {
    return <div className="movie-card">{content}</div>;
  }

  return (
    <a
      className="movie-card"
      href={tmdbUrl(movie.movie_id)}
      target="_blank"
      rel="noopener noreferrer"
    >
      {content}
    </a>
  );
}

const DEFAULT_TOP_K = 5;

function SearchPage() {
  const [query, setQuery] = useState("");
  const [topK, setTopK] = useState(DEFAULT_TOP_K);
  const [includeAdult, setIncludeAdult] = useState(false);
  const [popularOnly, setPopularOnly] = useState(true);
  const [highlyRatedOnly, setHighlyRatedOnly] = useState(false);
  const [results, setResults] = useState<Source[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [searched, setSearched] = useState(false);

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    const question = query.trim();
    if (!question || loading) return;

    setLoading(true);
    setError(null);
    try {
      const response = await search(question, topK, {
        includeAdult,
        popularOnly,
        highlyRatedOnly,
      });
      setResults(response.results);
      setSearched(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not reach the API.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="search-page">
      <p className="search-heading">Keyword search — no chat, just results</p>
      <form className="search-input" onSubmit={handleSubmit}>
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search for movies…"
          disabled={loading}
        />
        <button type="submit" disabled={loading || !query.trim()}>
          Search
        </button>
      </form>

      <div className="search-options">
        <label htmlFor="top-k">
          Number of movies: <strong>{topK}</strong>
        </label>
        <input
          id="top-k"
          type="range"
          min={1}
          max={42}
          value={topK}
          onChange={(e) => setTopK(Number(e.target.value))}
          disabled={loading}
        />

        <label className="toggle-control" htmlFor="include-adult">
          <input
            id="include-adult"
            type="checkbox"
            checked={includeAdult}
            onChange={(e) => setIncludeAdult(e.target.checked)}
            disabled={loading}
          />
          Show mature content
        </label>

        <label className="toggle-control" htmlFor="popular-only">
          <input
            id="popular-only"
            type="checkbox"
            checked={popularOnly}
            onChange={(e) => setPopularOnly(e.target.checked)}
            disabled={loading}
          />
          Popular movies only
        </label>

        <label className="toggle-control" htmlFor="highly-rated-only">
          <input
            id="highly-rated-only"
            type="checkbox"
            checked={highlyRatedOnly}
            onChange={(e) => setHighlyRatedOnly(e.target.checked)}
            disabled={loading}
          />
          Highly rated only
        </label>
      </div>

      <div className="search-results">
        {loading && <div className="search-status">Searching…</div>}
        {error && <div className="search-status error">{error}</div>}
        {!loading && !error && searched && results.length === 0 && (
          <div className="search-status">No movies found.</div>
        )}

        {!loading &&
          !error &&
          results.map((movie) => (
            <MovieCard key={movie.movie_id ?? movie.title} movie={movie} />
          ))}
      </div>
    </div>
  );
}

export default SearchPage;
