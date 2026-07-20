import re
from collections.abc import Sequence
from typing import Protocol

CITED_ID_PATTERN = re.compile(r"[\[\(](?:id:\s*)?(\d+)(?:[:\s][^\]\)]*)?[\]\)]")


class PointWithPayload(Protocol):
    payload: dict | None


def extract_cited_ids(answer: str) -> set[int]:
    return {int(match) for match in CITED_ID_PATTERN.findall(answer)}


def validate_answer(answer: str, matches: Sequence[PointWithPayload]) -> dict:
    context_ids = {
        (point.payload or {}).get("movie_id")
        for point in matches
        if (point.payload or {}).get("movie_id") is not None
    }
    cited_ids = extract_cited_ids(answer)
    hallucinated_ids = cited_ids - context_ids

    return {
        "valid": not hallucinated_ids,
        "cited_ids": sorted(cited_ids),
        "hallucinated_ids": sorted(hallucinated_ids),
    }
