from src.models.movieDocument import MovieDocument


def movieToDocument(movie) -> MovieDocument:
    text = f"""
Title: {movie["title"]}

Language: {movie["original_language"]}

Genres: {movie["genres"]}

Tagline:
{movie["tagline"]}

Keywords:
{movie["keywords"]}

Overview:
{movie["overview"]}
""".strip()

    payload = {
        "movie_id": int(movie["id"]),
        "imdb_id": movie["imdb_id"],
        "title": movie["title"],
        "genres": movie["genres"],
        "popularity": float(movie["popularity"]),
        "vote_average": float(movie["vote_average"]),
        "vote_count": int(movie["vote_count"]),
        "runtime": int(movie["runtime"]),
        "adult": bool(movie["adult"]),
        "release_date": movie["release_date"],
    }

    return MovieDocument(
        id=int(movie["id"]),
        text=text,
        payload=payload,
    )
