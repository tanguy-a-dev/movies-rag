from dataclasses import dataclass


@dataclass
class MovieDocument:
    id: int
    text: str
    payload: dict