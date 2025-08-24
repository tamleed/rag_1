# Simple RAG Search API with FastAPI and ChromaDB

This project is a simple Retrieval-Augmented Generation (RAG) search API built using FastAPI. It uses `sentence-transformers` to create vector embeddings from a data source and stores them in ChromaDB for efficient similarity searching.

## Project Structure

- `app/main.py`: The main FastAPI application containing the `/search` endpoint.
- `app/ingest.py`: A script to process a data source (`data.csv`), create embeddings, and store them in ChromaDB.
- `data.csv`: Sample data for the project.
- `requirements.txt`: Python dependencies.

## Setup

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd <repository-name>
   ```

2. **Install dependencies:**
   Make sure you have Python 3.8+ installed. Then, install the required packages.
   ```bash
   pip install -r requirements.txt
   ```

## How to Run

There are two main steps: first ingest the data, then run the API server.

**1. Ingest Data**

Run the ingestion script from the root directory of the project. This script will read `data.csv`, generate embeddings for the titles, and store them in a local ChromaDB database located at `./chroma_db`.

```bash
python -m app.ingest
```

You should see output confirming that records have been loaded and stored. You only need to do this once.

**2. Run the API Server**

Run the FastAPI application using `uvicorn`.

```bash
uvicorn app.main:app --reload
```

The server will be available at `http://127.0.0.1:8000`.

## How to Use

Once the server is running, you can send `GET` requests to the `/search` endpoint with a query `q`.

Here is an example using `curl`:

```bash
curl "http://127.0.0.1:8000/search/?q=healthy%20living"
```

This will return a JSON object with the most relevant search results from the data, including the document, its metadata, and the search distance.
