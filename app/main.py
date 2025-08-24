from fastapi import FastAPI
from . import api

app = FastAPI(title="RAG Service")

app.include_router(api.router, prefix="/api")
