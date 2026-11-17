import json
import pyodbc
from fastapi import HTTPException
from openai import AzureOpenAI
from backend.schemas import ShowItem

# Fíjate que hemos cambiado las variables importadas desde config
from backend.config import CONN_STR, AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_KEY

# Inicializamos el cliente de IA de Microsoft para el backend
ai_client = AzureOpenAI(
    api_key=AZURE_OPENAI_API_KEY,
    api_version="2024-02-15-preview",
    azure_endpoint=AZURE_OPENAI_ENDPOINT
)

def generate_query_embedding(query_text: str) -> list[float]:
    """Genera el vector en Azure OpenAI (1536D) eliminando el motor local."""
    try:
        # OpenAI no necesita prefijos como 'search_query:'
        response = ai_client.embeddings.create(
            input=query_text.strip(),
            model="text-embedding-3-small"
        )
        return response.data[0].embedding
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"El servicio de Azure OpenAI no responde: {str(e)}"
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