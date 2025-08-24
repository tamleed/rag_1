from fastapi import APIRouter, Depends
from .schemas import QueryRequest, QueryResult
from .deps import get_chroma

router = APIRouter()

@router.get("/health")
def health_check():
    return {"status": "ok"}

@router.post("/query", response_model=QueryResult)
def query_rag(req: QueryRequest, collection=Depends(get_chroma)):
    try:
        results = collection.query(
            query_texts=[req.query],
            n_results=req.n_results
        )
        return QueryResult(
            documents=results["documents"][0],
            metadatas=results["metadatas"][0]
        )
    except Exception as e:
        return {"error": str(e)}
