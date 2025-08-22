from fastapi import FastAPI
import chromadb

app = FastAPI()

DB_PATH = "./chroma_db"
COLLECTION_NAME = "news_1"

@app.get("/")
def root():
    return {"message": "RAG Service is running 🚀"}

@app.get("/search/")
def search(q: str, n: int = 5):
    client = chromadb.PersistentClient(path=DB_PATH)
    collection = client.get_collection(COLLECTION_NAME)

    results = collection.query(query_texts=[q], n_results=n)

    return {
        "query": q,
        "results": [
            {"doc": doc, "meta": meta}
            for doc, meta in zip(results["documents"][0], results["metadatas"][0])
        ]
    }
