import chromadb

DB_PATH = "./chroma_db"
COLLECTION_NAME = "news_1"

def get_chroma():
    client = chromadb.PersistentClient(path=DB_PATH)
    return client.get_collection(COLLECTION_NAME)
