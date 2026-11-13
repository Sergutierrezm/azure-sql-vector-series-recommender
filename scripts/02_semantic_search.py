import json
import pyodbc
import requests
import os
import sys
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
    try:
        response = requests.post(OLLAMA_URL, json={'model': OLLAMA_MODEL, 'prompt': f"search_query: {text}"}, timeout=10)
        response.raise_for_status()
        return response.json().get('embedding')
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Error al conectar con Ollama: Verifica que el servicio esté levantado.\nDetalle: {e}")
        sys.exit(1)

def main():
    # 1. Input del usuario
    print("\n🎬 --- BUSCADOR SEMÁNTICO DE SERIES (v2.0.0) ---")
    query_text = input("¿De qué tipo de serie tienes ganas hoy? (Ej: algo de viajes en el tiempo, humor absurdo en el trabajo, etc.):\n> ")
    
    if not query_text.strip():
        print("⚠️ No has escrito nada. Saliendo...")
        return

    print("\n🧠 Analizando tu petición con IA...")
    query_vector = get_embedding(query_text)
    
    # Preparamos el vector convirtiéndolo a texto JSON para que SQL lo entienda
    query_vector_json = json.dumps(query_vector)

    # 2. Delegar el cálculo a Azure SQL Database
    print("☁️ Delegando cálculo matemático y ordenación a Azure SQL Database...")
    
    try:
        # Usamos 'with' para asegurar el cierre automático de la conexión
        with pyodbc.connect(CONN_STR) as conn:
            cursor = conn.cursor()
            
            # Llamamos al procedimiento almacenado enviando el vector y pidiendo el TOP 3
            sql_query = "EXEC dbo.SearchSemanticShows @queryVector=?, @topK=?"
            cursor.execute(sql_query, (query_vector_json, 3))
            
            # Recibimos ÚNICAMENTE los resultados ya calculados y ordenados
            results = cursor.fetchall()

            # 3. Mostrar los resultados
            if not results:
                print("\n⚠️ No se encontraron resultados compatibles.")
                return

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

    except pyodbc.Error as e:
        print(f"\n❌ Error en la base de datos Azure SQL: {e}")
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")

if __name__ == '__main__':
    main()

    