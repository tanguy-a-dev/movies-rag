from src.dataset.document_builder import movie_to_document


def test_movie_to_document_builds_text_and_payload():
    movie = {
        "id": 1,
        "imdb_id": "tt123",
        "title": "Inception",
        "original_language": "en",
        "genres": "Action, Sci-Fi",
        "tagline": "Your mind is the scene of the crime",
        "keywords": "dream, heist",
        "overview": "A thief who steals secrets through dreams.",
        "popularity": 100.0,
        "vote_average": 8.8,
        "vote_count": 30000,
        "runtime": 148,
        "adult": False,
        "release_date": "2010-07-16",
        "poster_path": "/inception.jpg",
    }

    doc = movie_to_document(movie)

    assert doc.id == 1
    assert "Inception" in doc.text
    assert "dreams" in doc.text
    assert doc.payload["title"] == "Inception"
    assert doc.payload["overview"] == movie["overview"]
    assert doc.payload["poster_path"] == "/inception.jpg"


def test_movie_to_document_normalizes_missing_poster_to_none():
    movie = {
        "id": 2,
        "imdb_id": "tt456",
        "title": "No Poster Movie",
        "original_language": "en",
        "genres": "Drama",
        "tagline": "",
        "keywords": "",
        "overview": "A movie with no poster.",
        "popularity": 1.0,
        "vote_average": 5.0,
        "vote_count": 10,
        "runtime": 90,
        "adult": False,
        "release_date": "2020-01-01",
        "poster_path": "",
    }

    doc = movie_to_document(movie)

    assert doc.payload["poster_path"] is None
