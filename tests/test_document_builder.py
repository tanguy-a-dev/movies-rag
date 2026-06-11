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
    }

    doc = movie_to_document(movie)

    assert doc.id == 1
    assert "Inception" in doc.text
    assert "dreams" in doc.text
    assert doc.payload["title"] == "Inception"
    assert doc.payload["overview"] == movie["overview"]
