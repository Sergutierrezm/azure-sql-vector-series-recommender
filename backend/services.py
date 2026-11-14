import json
import pyodbc
import requests
from fastapi import HTTPException
from backend.config import CONN_STR, OLLAMA_URL, OLLAMA_MODEL
from backend.schemas import ShowItem

def generate_query_embedding(query_text: str) -> list[float]:
    """Genera el vector en Ollama usando el prefijo search_query de nomic-embed-text."""
    formatted_prompt = f"search_query: {query_text.strip()}"
    try:
        response = requests.post(
            OLLAMA_URL,
            json={"model": OLLAMA_MODEL, "prompt": formatted_prompt},
            timeout=10
        )
        response.raise_for_status()
        return response.json().get("embedding")
    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=503,
            detail=f"El motor de IA local (Ollama) no responde: {str(e)}"
        )

def get_all_catalog_shows() -> list[ShowItem]:
    """Devuelve las 50 series almacenadas en Azure SQL para la pestaña de catálogo."""
    try:
        with pyodbc.connect(CONN_STR, timeout=30) as conn:
            cursor = conn.cursor()
            sql = """
                SELECT ShowID, Title, Genre, ReleaseYear, Synopsis 
                FROM dbo.Shows 
                ORDER BY Title ASC
            """
            cursor.execute(sql)
            rows = cursor.fetchall()
            return [
                ShowItem(
                    id=row[0],
                    title=row[1],
                    genre=row[2],
                    release_year=row[3],
                    synopsis=row[4]
                )
                for row in rows
            ]
    except pyodbc.Error as e:
        raise HTTPException(status_code=500, detail=f"Error al leer el catálogo en Azure SQL: {str(e)}")

def search_semantic_shows_db(vector_json: str, top_k: int) -> list[ShowItem]:
    """Ejecuta el Stored Procedure en Azure SQL y devuelve el Top K con su afinidad."""
    try:
        with pyodbc.connect(CONN_STR, timeout=30) as conn:
            cursor = conn.cursor()
            sql = "EXEC dbo.SearchSemanticShows @queryVector=?, @topK=?"
            cursor.execute(sql, (vector_json, top_k))
            rows = cursor.fetchall()
            return [
                ShowItem(
                    id=row[0],
                    title=row[1],
                    genre=row[2],
                    release_year=row[3],
                    synopsis=row[4],
                    affinity_pct=round(float(row[5]) * 100, 2)
                )
                for row in rows
            ]
    except pyodbc.Error as e:
        raise HTTPException(status_code=500, detail=f"Error en el cálculo vectorial de Azure SQL: {str(e)}")