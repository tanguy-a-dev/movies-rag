from src.clients.qdrant import ensure_collection
from src.settings import settings


def main() -> None:
    ensure_collection(vector_size=settings.vector_size)


if __name__ == "__main__":
    main()
