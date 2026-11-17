import json
from pathlib import Path
import pyodbc
import os
from dotenv import load_dotenv
from openai import AzureOpenAI

# Carga las variables ocultas del archivo .env
load_dotenv()

# --- Configuración de Azure SQL ---
AZURE_SERVER = os.getenv('AZURE_SERVER')
AZURE_DATABASE = os.getenv('AZURE_DATABASE')
AZURE_USER = os.getenv('AZURE_USER')
AZURE_PASSWORD = os.getenv('AZURE_PASSWORD')

# --- Configuración de Azure OpenAI (Reemplaza a Ollama) ---
AZURE_OPENAI_ENDPOINT = os.getenv('AZURE_OPENAI_ENDPOINT')
AZURE_OPENAI_API_KEY = os.getenv('AZURE_OPENAI_API_KEY')
DEPLOYMENT_NAME = "text-embedding-3-small"

CONN_STR = (
    f'DRIVER={{ODBC Driver 18 for SQL Server}};'
    f'SERVER={AZURE_SERVER};'
    f'DATABASE={AZURE_DATABASE};'
    f'UID={AZURE_USER};'
    f'PWD={AZURE_PASSWORD};'
    f'Encrypt=yes;TrustServerCertificate=no;'
)

# Inicializamos el cliente de IA de Microsoft
ai_client = AzureOpenAI(
    api_key=AZURE_OPENAI_API_KEY,
    api_version="2024-02-15-preview",
    azure_endpoint=AZURE_OPENAI_ENDPOINT
)

# Ruta relativa al archivo JSON
BASE_DIR = Path(__file__).resolve().parent.parent
JSON_PATH = BASE_DIR / 'data' / 'shows.json'

def get_embedding(text):
    """Obtiene el vector embedding (1536D) desde Azure OpenAI."""
    try:
        response = ai_client.embeddings.create(
            input=text,
            model=DEPLOYMENT_NAME
        )
        return response.data[0].embedding
    except Exception as e:
        raise Exception(f'Error al conectar con Azure OpenAI: {e}')

def main():
    if not JSON_PATH.exists():
        raise FileNotFoundError(f"No se encontró el archivo JSON en: {JSON_PATH}")

    print(f"📂 Cargando dataset desde: {JSON_PATH}")
    with open(JSON_PATH, 'r', encoding='utf-8') as f:
        shows_data = json.load(f)

    print('🔌 Conectando a Azure SQL Database...')
    
    try:
        with pyodbc.connect(CONN_STR) as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT Title FROM dbo.Shows")
            existing_titles = {row[0] for row in cursor.fetchall()}

            records_to_insert = []

            for show in shows_data:
                title = show['title']
                
                if title in existing_titles:
                    print(f"⏭️ La serie '{title}' ya existe. Saltando...")
                    continue

                print(f"🧠 Generando embedding Azure AI enriquecido para: '{title}'...")
                
                # --- DATA ENRICHMENT ---
                # Unimos todos los metadatos para darle un contexto perfecto a OpenAI
                texto_enriquecido = f"Título: {title}. Género: {show['genre']}. Año: {show['year']}. Sinopsis: {show['synopsis']}"
                
                # Generamos el vector basándonos en el texto enriquecido, no solo en la sinopsis
                vector = get_embedding(texto_enriquecido)
                vector_json = json.dumps(vector)

                # La inserción en base de datos no cambia, guardamos la sinopsis limpia para Angular
                records_to_insert.append((title, show['genre'], show['year'], show['synopsis'], vector_json))

            if records_to_insert:
                print(f"💾 Insertando {len(records_to_insert)} nuevas series en Azure SQL...")
                cursor.executemany("""
                    INSERT INTO dbo.Shows (Title, Genre, ReleaseYear, Synopsis, EmbeddingJson)
                    VALUES (?, ?, ?, ?, ?)
                """, records_to_insert)
                
                conn.commit()
                print('✅ ¡Proceso de sincronización completado con éxito!')
            else:
                print('✅ No hay series nuevas que insertar. Todo está al día.')

    except pyodbc.Error as e:
        print(f"❌ Error en la base de datos: {e}")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

if __name__ == '__main__':
    main()