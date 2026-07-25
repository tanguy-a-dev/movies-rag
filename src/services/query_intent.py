import re
from dataclasses import dataclass, field

RATING_PATTERN = re.compile(
    r"\b(?:best|top|highest|highly)[\s-]rated\b", re.IGNORECASE
)
POPULARITY_PATTERN = re.compile(
    r"\b(?:most|highly|very)\s+popular\b|\btrending\b", re.IGNORECASE
)

DECADE_4_DIGIT = re.compile(r"\b(19|20)(\d)0s\b", re.IGNORECASE)
DECADE_2_DIGIT = re.compile(r"\b'?(\d0)s\b", re.IGNORECASE)
YEAR_BEFORE = re.compile(r"\bbefore\s+(\d{4})\b", re.IGNORECASE)
YEAR_AFTER = re.compile(r"\b(?:after|since)\s+(\d{4})\b", re.IGNORECASE)
YEAR_EXACT = re.compile(r"\b(?:released\s+in|from|in)\s+(\d{4})\b", re.IGNORECASE)


@dataclass
class QueryIntent:
    sort_by: list[str] = field(default_factory=list)
    min_year: int | None = None
    max_year: int | None = None


def parse_intent(question: str) -> QueryIntent:
    sort_by = []
    if RATING_PATTERN.search(question):
        sort_by.append("rating")
    if POPULARITY_PATTERN.search(question):
        sort_by.append("popularity")

    min_year: int | None = None
    max_year: int | None = None

    if match := DECADE_4_DIGIT.search(question):
        decade_start = int(match.group(1) + match.group(2) + "0")
        min_year, max_year = decade_start, decade_start + 9
    elif match := DECADE_2_DIGIT.search(question):
        two_digit = int(match.group(1))
        # "20s" reads as 2020s, not 1920s, in casual movie-search phrasing today
        decade_start = (2000 if two_digit < 30 else 1900) + two_digit
        min_year, max_year = decade_start, decade_start + 9

    if match := YEAR_BEFORE.search(question):
        max_year = int(match.group(1)) - 1
    if match := YEAR_AFTER.search(question):
        min_year = int(match.group(1))
    if min_year is None and max_year is None and (match := YEAR_EXACT.search(question)):
        min_year = max_year = int(match.group(1))

    return QueryIntent(sort_by=sort_by, min_year=min_year, max_year=max_year)
