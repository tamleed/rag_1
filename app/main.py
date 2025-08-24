from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException
import chromadb
from sentence_transformers import SentenceTransformer
from typing import Dict, Any

from app.config import DB_PATH, COLLECTION_NAME, MODEL_NAME

# A dictionary to hold the state of the application
# This is a simple way to share objects like models or db connections
# across the application's lifespan.
state: Dict[str, Any] = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    A context manager to handle the startup and shutdown of the application.
    This is where we will load our model and database client.
    """
    print("RAG service starting up...")
    state["model"] = SentenceTransformer(MODEL_NAME)
    state["client"] = chromadb.PersistentClient(path=DB_PATH)
    print("Model and DB client loaded.")
    yield
    # Code to run on shutdown
    print("RAG service shutting down...")
    state.clear()
    print("Shutdown complete.")

app = FastAPI(lifespan=lifespan)

def get_model() -> SentenceTransformer:
    """Dependency to get the SentenceTransformer model."""
    return state.get("model")

def get_collection() -> chromadb.Collection:
    """Dependency to get the ChromaDB collection."""
    try:
        collection = state["client"].get_or_create_collection(COLLECTION_NAME)
        return collection
    except Exception as e:
        # This could happen if the client isn't initialized, etc.
        raise HTTPException(status_code=503, detail=f"Database not available: {e}")

@app.get("/")
def root():
    return {"message": "RAG Service is running 🚀"}

@app.get("/search/")
def search(
    q: str,
    n: int = 5,
    model: SentenceTransformer = Depends(get_model),
    collection: chromadb.Collection = Depends(get_collection)
):
    """
    Search endpoint that finds the most relevant documents for a given query.
    """
    if not q:
        raise HTTPException(status_code=400, detail="Query parameter 'q' cannot be empty.")

    # Create the embedding for the query
    query_embedding = model.encode(q).tolist()

    # Query the collection
    results = collection.query(query_embeddings=[query_embedding], n_results=n)

    return {
        "query": q,
        "results": [
            {"doc": doc, "meta": meta, "dist": dist}
            for doc, meta, dist in zip(results["documents"][0], results["metadatas"][0], results["distances"][0])
        ]
    }
