import os
os.environ['ENV'] = 'TEST'

import pytest
from fastapi.testclient import TestClient
import shutil
import pandas as pd
from sentence_transformers import SentenceTransformer
import chromadb

from app.main import app, get_collection
from app.config import COLLECTION_NAME, MODEL_NAME

TEST_DB_PATH = "chroma_db_test"

@pytest.fixture(scope="module", autouse=True)
def setup_teardown_test_database():
    """
    Fixture to create a dedicated test database before tests run
    and clean it up afterwards.
    """
    if_exists_delete_test_db()

    client = chromadb.PersistentClient(path=TEST_DB_PATH)
    collection = client.get_or_create_collection(COLLECTION_NAME)
    model = SentenceTransformer(MODEL_NAME)

    df = pd.read_csv("data.csv")
    embeddings = df["title"].apply(lambda x: model.encode(x).tolist()).tolist()
    collection.add(
        ids=[str(i) for i in df.index],
        embeddings=embeddings,
        documents=df["title"].tolist(),
        metadatas=[{"url": url, "category": cat} for url, cat in zip(df["url"], df["category"])],
    )
    print(f"Test database created at {TEST_DB_PATH} with {collection.count()} items.")

    yield

    print(f"Cleaning up test database at {TEST_DB_PATH}...")
    if_exists_delete_test_db()
    print("Cleanup complete.")

def if_exists_delete_test_db():
    shutil.rmtree(TEST_DB_PATH, ignore_errors=True)

def override_get_collection():
    """Dependency override to point to the test database."""
    client = chromadb.PersistentClient(path=TEST_DB_PATH)
    collection = client.get_or_create_collection(name=COLLECTION_NAME)
    return collection

app.dependency_overrides[get_collection] = override_get_collection

def test_root_endpoint():
    """Test the root endpoint."""
    with TestClient(app) as client:
        response = client.get("/")
        assert response.status_code == 200
        assert response.json() == {"message": "RAG Service is running 🚀"}

def test_search_endpoint_success():
    """Test a successful search query."""
    with TestClient(app) as client:
        response = client.get("/search/?q=health")
        assert response.status_code == 200
        data = response.json()
        assert data["query"] == "health"
        assert len(data["results"]) > 0
        first_result = data["results"][0]
        assert first_result["doc"] == "Tips for a healthy lifestyle"

def test_search_endpoint_with_specific_n():
    """Test the 'n' parameter to limit results."""
    with TestClient(app) as client:
        response = client.get("/search/?q=space&n=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data["results"]) == 2

def test_search_endpoint_no_query():
    """Test hitting the endpoint with no query."""
    with TestClient(app) as client:
        response = client.get("/search/?q=")
        assert response.status_code == 400
        assert response.json() == {"detail": "Query parameter 'q' cannot be empty."}
