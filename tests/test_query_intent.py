from src.services.query_intent import parse_intent


def test_no_intent_for_plain_question():
    intent = parse_intent("Suggest a movie about heists")

    assert intent.sort_by == []
    assert intent.min_year is None
    assert intent.max_year is None


def test_detects_best_rated():
    intent = parse_intent("Give me best rated superhero movies")

    assert intent.sort_by == ["rating"]


def test_detects_most_popular():
    intent = parse_intent("Give me most popular superhero movies")

    assert intent.sort_by == ["popularity"]


def test_detects_both_rating_and_popularity():
    intent = parse_intent("Give me best rated and most popular superhero movies")

    assert intent.sort_by == ["rating", "popularity"]


def test_detects_four_digit_decade():
    intent = parse_intent("Suggest a dark comedy from the 1990s")

    assert (intent.min_year, intent.max_year) == (1990, 1999)


def test_detects_two_digit_decade_recent():
    intent = parse_intent("Suggest a dark comedy from the 90s")

    assert (intent.min_year, intent.max_year) == (1990, 1999)


def test_two_digit_decade_low_number_reads_as_2000s():
    intent = parse_intent("Suggest a movie from the 10s")

    assert (intent.min_year, intent.max_year) == (2010, 2019)


def test_detects_before_year():
    intent = parse_intent("Recommend a horror movie before 2000")

    assert (intent.min_year, intent.max_year) == (None, 1999)


def test_detects_after_year():
    intent = parse_intent("Recommend a horror movie after 2010")

    assert (intent.min_year, intent.max_year) == (2010, None)


def test_detects_exact_year():
    intent = parse_intent("What came out in 2015?")

    assert (intent.min_year, intent.max_year) == (2015, 2015)
