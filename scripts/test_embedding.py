from src.clients.ollama import ollama_client


def main() -> None:
    vec = ollama_client.embed_text("test movie")
    print("vector size:", len(vec))
    print("first values:", vec[:5])


if __name__ == "__main__":
    main()
