import os

# --- Shared Configuration ---
COLLECTION_NAME = "news_1"
MODEL_NAME = "all-MiniLM-L6-v2"

# --- Database Configuration ---
# When running with Docker, these will be set by docker-compose.
# When running locally, it will fall back to localhost and a default port.
CHROMA_HOST = os.getenv("CHROMA_HOST", "localhost")
CHROMA_PORT = int(os.getenv("CHROMA_PORT", "8001")) # Defaulting to 8001 for local Chroma server

# --- DEPRECATED ---
# The DB_PATH is no longer used for the server-based client,
# but we keep it here for reference or for potential local-only modes.
DB_PATH = "chroma_db"
