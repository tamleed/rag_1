import pandas as pd
from sentence_transformers import SentenceTransformer
import chromadb
from app.config import DB_PATH, COLLECTION_NAME, MODEL_NAME

def load_data(file_path="data.csv"):
    """Loads data from a CSV file."""
    df = pd.read_csv(file_path)
    print(f"Loaded {len(df)} records from {file_path}")
    return df

def create_embeddings(df, model_name=MODEL_NAME):
    """Creates embeddings for the 'title' column."""
    model = SentenceTransformer(model_name)
    df["embedding"] = df["title"].apply(lambda x: model.encode(x).tolist())
    print("Embeddings created successfully.")
    return df

def store_in_chroma(df):
    """Stores data and embeddings in ChromaDB."""
    client = chromadb.PersistentClient(path=DB_PATH)
    collection = client.get_or_create_collection(COLLECTION_NAME)

    collection.add(
        ids=[str(i) for i in df.index],
        embeddings=df["embedding"].tolist(),
        documents=df["title"].tolist(),
        metadatas=[{"url": url, "category": cat} for url, cat in zip(df["url"], df["category"])],
    )
    print(f"Stored {len(df)} records in ChromaDB collection '{COLLECTION_NAME}'.")

    # Verify the count
    count = collection.count()
    print(f"Verification: Collection '{COLLECTION_NAME}' now contains {count} items.")

if __name__ == "__main__":
    data_df = load_data()
    data_df = create_embeddings(data_df)
    store_in_chroma(data_df)
