from src.embeddings.httpEmbedding import embedText


def main():
    vec = embedText("test movie")
    print("vector size:", len(vec))
    print("first values:", vec[:5])


if __name__ == "__main__":
    main()
