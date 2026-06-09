from src.vectordb.qdrantClient import createCollection

if __name__ == "__main__":
    createCollection(vector_size=768)