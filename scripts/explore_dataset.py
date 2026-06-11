from src.dataset.document_builder import movie_to_document
from src.dataset.loader import load_movies


def main() -> None:
    df = load_movies().fillna("")

    print(df.columns)
    print(df.head())
    movie = df.iloc[0]

    for column in df.columns:
        print(f"{column}: {movie[column]}")

    doc = movie_to_document(df.iloc[0])
    print(doc.text)
    print(doc.payload)


if __name__ == "__main__":
    main()
