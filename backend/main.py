import json
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.schemas import SearchRequest, ShowItem
from backend.services import (
    generate_query_embedding,
    get_all_catalog_shows,
    search_semantic_shows_db
)

app = FastAPI(
    title="Azure SQL Series Semantic Search API",
    description="Backend v3.0.0: Catálogo y recomendador semántico con Ollama y Azure SQL",
    version="3.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {"status": "ok", "version": "3.0.0"}

@app.get("/api/shows", response_model=list[ShowItem])
def list_shows():
    """Obtiene todas las series añadidas en la base de datos."""
    return get_all_catalog_shows()

@app.post("/api/search", response_model=list[ShowItem])
def semantic_search(request: SearchRequest):
    """Recomienda series calculando el embedding en Ollama y la similitud en Azure SQL."""
    vector = generate_query_embedding(request.query)
    vector_json = json.dumps(vector)
    return search_semantic_shows_db(vector_json, request.top_k)