from src.dataset.loader import load_movies
from src.embeddings.httpEmbedding import embedText
from src.vectordb.qdrantClient import client


def ingest(n=200):
    df = load_movies().fillna("")
    df = df.head(n)

    for i, row in df.iterrows():
        text = f"{row['title']} {row['overview']} {row['tagline']}"
        vector = embedText(text)

        client.upsert(
            collection_name="movies",
            points=[
                {
                    "id": int(row["id"]),
                    "vector": vector,
                    "payload": {
                        "title": row["title"],
                        "overview": row["overview"],
                        "genres": row["genres"],
                    },
                }
            ],
        )

        if i % 50 == 0:
            print("ingested:", i)


if __name__ == "__main__":
    ingest()