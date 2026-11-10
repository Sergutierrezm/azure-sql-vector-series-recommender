import json
import math
import pyodbc
import requests
import os

from dotenv import load_dotenv

# Carga las variables ocultas del archivo .env
load_dotenv()

# --- Configuración de Azure SQL y Ollama ---
AZURE_SERVER = os.getenv('AZURE_SERVER')
AZURE_DATABASE = os.getenv('AZURE_DATABASE')
AZURE_USER = os.getenv('AZURE_USER')
AZURE_PASSWORD = os.getenv('AZURE_PASSWORD')

OLLAMA_URL = 'http://localhost:11434/api/embeddings'
OLLAMA_MODEL = 'nomic-embed-text' 

CONN_STR = (
    f'DRIVER={{ODBC Driver 18 for SQL Server}};'
    f'SERVER={AZURE_SERVER};'
    f'DATABASE={AZURE_DATABASE};'
    f'UID={AZURE_USER};'
    f'PWD={AZURE_PASSWORD};'
    f'Encrypt=yes;TrustServerCertificate=no;'
)

def get_embedding(text):
    """Genera el vector de la frase que escriba el usuario"""
    payload = {'model': OLLAMA_MODEL, 'prompt': text}
    response = requests.post(OLLAMA_URL, json=payload)
    if response.status_code == 200:
        return response.json().get('embedding')
    else:
        raise Exception(f'Error en Ollama: {response.text}')

def cosine_similarity(v1, v2):
    """Fórmula matemática para calcular la cercanía entre dos vectores"""
    dot_product = sum(a * b for a, b in zip(v1, v2))
    magnitude = math.sqrt(sum(a * a for a in v1)) * math.sqrt(sum(b * b for b in v2))
    return dot_product / magnitude if magnitude != 0 else 0

def main():
    # 1. Input del usuario
    print("\n🎬 --- BUSCADOR SEMÁNTICO DE SERIES ---")
    query_text = input("¿De qué tipo de serie tienes ganas hoy? (Ej: algo de viajes en el tiempo, humor absurdo en el trabajo, etc.):\n> ")
    
    print("\n🧠 Analizando tu petición con IA...")
    query_vector = get_embedding(query_text)

    # 2. Extraer vectores de Azure SQL
    print("🔌 Conectando a Azure SQL Database para buscar coincidencias...")
    conn = pyodbc.connect(CONN_STR)
    cursor = conn.cursor()
    
    cursor.execute("SELECT Title, Genre, Synopsis, EmbeddingJson FROM dbo.Shows")
    shows = cursor.fetchall()
    conn.close()

    # 3. Calcular la similitud matemática
    results = []
    for show in shows:
        title, genre, synopsis, embedding_json = show
        if embedding_json:
            show_vector = json.loads(embedding_json)
            similarity = cosine_similarity(query_vector, show_vector)
            results.append((title, genre, synopsis, similarity))
    
    # 4. Ordenar resultados de mayor a menor porcentaje de similitud
    results.sort(key=lambda x: x[3], reverse=True)

    # 5. Mostrar el Top 3
    print("\n🏆 TOP 3 SERIES RECOMENDADAS PARA TI:")
    print("-" * 60)
    for i, (title, genre, synopsis, sim) in enumerate(results[:3], 1):
        # Convertimos la similitud a un formato de porcentaje más legible
        match_pct = round(sim * 100, 2)
        print(f"{i}. {title} ({genre}) | Afinadad: {match_pct}%")
        print(f"   Sinopsis: {synopsis}\n")

if __name__ == '__main__':
    main()