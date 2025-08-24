from pydantic import BaseModel
from typing import List, Dict, Any

class QueryRequest(BaseModel):
    query: str
    n_results: int = 5

class QueryResult(BaseModel):
    documents: List[str]
    metadatas: List[Dict[str, Any]]
