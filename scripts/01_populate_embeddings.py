import json
from pathlib import Path
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

# Ruta relativa al archivo JSON desde la carpeta scripts/
BASE_DIR = Path(__file__).resolve().parent.parent
JSON_PATH = BASE_DIR / 'data' / 'shows.json'

def get_embedding(text):
    """Obtiene el vector embedding desde Ollama."""
    try:
        response = requests.post(OLLAMA_URL, json={'model': OLLAMA_MODEL, 'prompt': text}, timeout=10)
        response.raise_for_status()
        return response.json().get('embedding')
    except requests.exceptions.RequestException as e:
        raise Exception(f'Error al conectar con Ollama: {e}')

def main():
    if not JSON_PATH.exists():
        raise FileNotFoundError(f"No se encontró el archivo JSON en: {JSON_PATH}")

    print(f"📂 Cargando dataset desde: {JSON_PATH}")
    with open(JSON_PATH, 'r', encoding='utf-8') as f:
        shows_data = json.load(f)

    print('🔌 Conectando a Azure SQL Database...')
    
    # Uso de 'with' para garantizar que la conexión se cierra aunque haya errores
    try:
        with pyodbc.connect(CONN_STR) as conn:
            cursor = conn.cursor()

            # 1. OPTIMIZACIÓN N+1: Traer todos los títulos existentes en una sola consulta
            cursor.execute("SELECT Title FROM dbo.Shows")
            # Usamos un Set (conjunto) de Python porque las búsquedas en él son ultra rápidas (O(1))
            existing_titles = {row[0] for row in cursor.fetchall()}

            # Lista para guardar los registros nuevos y hacer la inserción en bloque
            records_to_insert = []

            for show in shows_data:
                title = show['title']
                
                # Búsqueda instantánea en la memoria de Python, sin llamar a Azure
                if title in existing_titles:
                    print(f"⏭️ La serie '{title}' ya existe. Saltando...")
                    continue

                # 2. Generar el embedding
                print(f"🧠 Generando embedding para nueva serie: '{title}'...")
                vector = get_embedding(show['synopsis'])
                vector_json = json.dumps(vector)

                # Preparamos el registro
                records_to_insert.append((title, show['genre'], show['year'], show['synopsis'], vector_json))

            # 3. OPTIMIZACIÓN DE TRANSACCIONES: Insertar todo de golpe si hay datos nuevos
            if records_to_insert:
                print(f"💾 Insertando {len(records_to_insert)} nuevas series en Azure SQL...")
                cursor.executemany("""
                    INSERT INTO dbo.Shows (Title, Genre, ReleaseYear, Synopsis, EmbeddingJson)
                    VALUES (?, ?, ?, ?, ?)
                """, records_to_insert)
                
                # Un solo commit al final ahorra muchísimos recursos en la base de datos
                conn.commit()
                print('✅ ¡Proceso de sincronización y guardado completado!')
            else:
                print('✅ No hay series nuevas que insertar. Todo está al día.')

    except pyodbc.Error as e:
        print(f"❌ Error en la base de datos: {e}")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

if __name__ == '__main__':
    main()
    