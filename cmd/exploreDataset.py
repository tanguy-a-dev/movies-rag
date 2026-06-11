from src.dataset.loader import load_movies
from src.dataset.documentBuilder import movieToDocument


if __name__ == "__main__":
    try:
        df = load_movies().fillna("")

        print(df.columns)
        print(df.head())
        movie = df.iloc[0]

        for column in df.columns:
            print(f"{column}: {movie[column]}")

        doc = movieToDocument(df.iloc[0])

        print(doc.text)
        print(doc.payload)
    except Exception as err:
        print(f"err {err}")
