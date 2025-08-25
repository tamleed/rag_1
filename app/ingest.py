import pandas as pd
from sentence_transformers import SentenceTransformer
import chromadb
from app.config import COLLECTION_NAME, MODEL_NAME, CHROMA_HOST, CHROMA_PORT

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
    """Stores data and embeddings in a remote ChromaDB server."""
    client = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)
    print(f"Connecting to ChromaDB at {CHROMA_HOST}:{CHROMA_PORT}...")

    collection = client.get_or_create_collection(COLLECTION_NAME)
    print(f"Ingesting {len(df)} records into collection '{COLLECTION_NAME}'...")

    collection.add(
        ids=[str(i) for i in df.index],
        embeddings=df["embedding"].tolist(),
        documents=df["title"].tolist(),
        metadatas=[{"url": url, "category": cat} for url, cat in zip(df["url"], df["category"])],
    )
    print(f"Successfully stored {collection.count()} records.")

if __name__ == "__main__":
    data_df = load_data()
    data_df = create_embeddings(data_df)
    store_in_chroma(data_df)
