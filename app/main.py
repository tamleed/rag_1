import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException
import chromadb
from sentence_transformers import SentenceTransformer
from typing import Dict, Any

from app.config import COLLECTION_NAME, MODEL_NAME, CHROMA_HOST, CHROMA_PORT

# A dictionary to hold the state of the application
state: Dict[str, Any] = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    A context manager to handle the startup and shutdown of the application.
    """
    print("RAG service starting up...")

    # Load the model, which is needed in all environments
    state["model"] = SentenceTransformer(MODEL_NAME)

    # Connect to ChromaDB only if not in a test environment
    if os.getenv("ENV") != "TEST":
        print(f"Connecting to ChromaDB at {CHROMA_HOST}:{CHROMA_PORT}...")
        state["client"] = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)
        print("DB client connected.")
    else:
        print("Running in TEST mode. Skipping remote DB connection in lifespan.")
        state["client"] = None # In tests, this will be handled by dependency overrides

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
    """
    Dependency to get the ChromaDB collection.
    In production, this uses the client from the app state.
    In tests, this function is overridden to point to a local test DB.
    """
    client = state.get("client")
    if client is None:
        # This will happen in tests, where the override will take over.
        # If it happens in production, it's a server error.
        raise HTTPException(status_code=503, detail="Database client not initialized.")

    try:
        collection = client.get_or_create_collection(COLLECTION_NAME)
        return collection
    except Exception as e:
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

    query_embedding = model.encode(q).tolist()
    results = collection.query(query_embeddings=[query_embedding], n_results=n)

    return {
        "query": q,
        "results": [
            {"doc": doc, "meta": meta, "dist": dist}
            for doc, meta, dist in zip(results["documents"][0], results["metadatas"][0], results["distances"][0])
        ]
    }
