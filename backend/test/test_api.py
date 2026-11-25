from fastapi import HTTPException
from fastapi.testclient import TestClient
from unittest.mock import patch
from backend.main import app
from backend.schemas import ShowItem

client = TestClient(app)


def test_health_check():
    """Verifica que la API responde y reporta la v4.0.0 con Azure OpenAI."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "version": "4.0.0",
        "ai_engine": "Azure OpenAI",
    }


@patch("backend.main.get_all_catalog_shows")
def test_list_shows_mocked(mock_get_shows):
    """Prueba GET /api/shows sin conectarse a Azure SQL."""
    mock_get_shows.return_value = [
        ShowItem(
            id=1,
            title="The Office",
            genre="Comedy",
            release_year=2005,
            synopsis="Falso documental sobre empleados de oficina.",
        )
    ]

    response = client.get("/api/shows")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "The Office"
    assert data[0]["affinity_pct"] is None


@patch("backend.main.search_semantic_shows_db")
@patch("backend.main.generate_query_embedding")
def test_semantic_search_mocked(mock_embedding, mock_db_search):
    """
    Prueba POST /api/search simulando Azure OpenAI (1536D) y Azure SQL.
    Valida el flujo completo y el contrato JSON con Angular sin gastar tokens.
    """
    mock_embedding.return_value = [0.01] * 1536
    mock_db_search.return_value = [
        ShowItem(
            id=1,
            title="The Office",
            genre="Comedy",
            release_year=2005,
            synopsis="Falso documental sobre empleados de oficina.",
            affinity_pct=48.77,
        )
    ]

    response = client.post(
        "/api/search",
        json={"query": "series graciosas de oficina", "top_k": 3},
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "The Office"
    assert data[0]["affinity_pct"] == 48.77
    mock_embedding.assert_called_once_with("series graciosas de oficina")


def test_semantic_search_validation_errors():
    """Verifica que Pydantic rechaza queries muy cortas o top_k fuera de rango (1-10)."""
    # Query con menos de 2 caracteres (min_length=2)
    res_short = client.post("/api/search", json={"query": "a", "top_k": 3})
    assert res_short.status_code == 422

    # top_k mayor que 10 (le=10)
    res_topk = client.post("/api/search", json={"query": "comedia", "top_k": 25})
    assert res_topk.status_code == 422


@patch("backend.main.generate_query_embedding")
def test_semantic_search_openai_unavailable(mock_embedding):
    """Verifica que si Azure OpenAI falla, la API devuelve 503 controlado."""
    mock_embedding.side_effect = HTTPException(
        status_code=503,
        detail="El servicio de Azure OpenAI no responde",
    )

    response = client.post("/api/search", json={"query": "series de crimenes"})
    assert response.status_code == 503
    assert "Azure OpenAI" in response.json()["detail"]