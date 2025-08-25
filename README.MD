# RAG Search API with FastAPI and Standalone ChromaDB

This project provides a simple Retrieval-Augmented Generation (RAG) search API using FastAPI. It uses `sentence-transformers` to create vector embeddings and stores them in a **standalone ChromaDB server**, making the database accessible to other applications on the network.

This entire application stack is designed to be run with Docker Compose.

## Project Structure

- `app/`: Contains the main FastAPI application source code.
- `Dockerfile`: Defines the container for the FastAPI application.
- `docker-compose.yml`: Orchestrates the API and ChromaDB services.
- `data.csv`: Sample data for the project.
- `requirements.txt`: Python dependencies.

## How to Run with Docker

This is the recommended way to run the project.

**Prerequisites:**
- Docker and Docker Compose installed.

**Steps:**

1.  **Build and Start the Services:**
    From the root directory of the project, run:
    ```bash
    docker-compose up --build
    ```
    This will:
    - Build the Docker image for the FastAPI `api` service.
    - Pull the official Docker image for the `chroma` service.
    - Start both containers and connect them on a shared network.

    The API will be available at `http://localhost:8000`.
    The ChromaDB server will be available at `http://localhost:8001`.

2.  **Ingest the Data:**
    Once the services are running, open a **new terminal window** and run the ingestion script. This only needs to be done once.
    ```bash
    python -m app.ingest
    ```
    This script will connect to the ChromaDB server running in Docker and populate it with the data from `data.csv`.

3.  **Use the API:**
    The search endpoint is now active. You can use `curl` or any HTTP client to send requests:
    ```bash
    curl "http://localhost:8000/search/?q=healthy%20living"
    ```

## Connecting from an External Application (e.g., Jupyter Notebook)

Because ChromaDB is running as a standalone service, you can connect to it from any other application that can reach it (e.g., from your host machine).

**Connection Details:**
- **Host:** `localhost`
- **Port:** `8001`

**Example Python Code:**
```python
import chromadb

# Connect to the running ChromaDB server
client = chromadb.HttpClient(host="localhost", port=8001)

# Get the collection
collection = client.get_collection("news_1")

# Query the collection
results = collection.query(
    query_texts=["space exploration"],
    n_results=2
)

print(results)
```
This demonstrates how you can now interact with the same database used by the API from a completely separate process.
