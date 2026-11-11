import json
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

def main():
    # 1. Input del usuario
    print("\n🎬 --- BUSCADOR SEMÁNTICO DE SERIES (v2.0.0) ---")
    query_text = input("¿De qué tipo de serie tienes ganas hoy? (Ej: algo de viajes en el tiempo, humor absurdo en el trabajo, etc.):\n> ")
    
    print("\n🧠 Analizando tu petición con IA...")
    query_vector = get_embedding(query_text)
    
    # Preparamos el vector convirtiéndolo a texto JSON para que SQL lo entienda
    query_vector_json = json.dumps(query_vector)

    # 2. Delegar el cálculo a Azure SQL Database
    print("☁️ Delegando cálculo matemático y ordenación a Azure SQL Database...")
    conn = pyodbc.connect(CONN_STR)
    cursor = conn.cursor()
    
    # Llamamos al procedimiento almacenado enviando el vector y pidiendo el TOP 3
    sql_query = "EXEC dbo.SearchSemanticShows @queryVector=?, @topK=?"
    cursor.execute(sql_query, (query_vector_json, 3))
    
    # Recibimos ÚNICAMENTE los 3 resultados ya calculados y ordenados por la base de datos
    results = cursor.fetchall()
    conn.close()

    # 3. Mostrar los resultados
    print("\n🏆 TOP 3 SERIES RECOMENDADAS PARA TI:")
    print("-" * 60)
    for i, row in enumerate(results, 1):
        # El SP devuelve: ShowID (0), Title (1), Genre (2), ReleaseYear (3), SimilarityScore (4)
        show_id = row[0]
        title = row[1]
        genre = row[2]
        release_year = row[3]
        sim = row[4]
        
        match_pct = round(sim * 100, 2)
        print(f"{i}. {title} ({release_year}) - {genre} | Afinidad: {match_pct}%")
        print(f"   [ID Sistema: {show_id}]\n")

if __name__ == '__main__':
    main()