// TMDB's own movie page -- id comes straight from our Qdrant payload's movie_id,
// so no extra lookup is needed to build this.
export function tmdbUrl(id: number | string): string {
  return `https://www.themoviedb.org/movie/${id}`;
}
