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
    payload = {'model': OLLAMA_MODEL, 'prompt': text}
    response = requests.post(OLLAMA_URL, json=payload)
    if response.status_code == 200:
        return response.json().get('embedding')
    else:
        raise Exception(f'Error en Ollama: {response.text}')

def main():
    if not JSON_PATH.exists():
        raise FileNotFoundError(f"No se encontró el archivo JSON en: {JSON_PATH}")

    print(f"📂 Cargando dataset desde: {JSON_PATH}")
    with open(JSON_PATH, 'r', encoding='utf-8') as f:
        shows_data = json.load(f)

    print('🔌 Conectando a Azure SQL Database...')
    conn = pyodbc.connect(CONN_STR)
    cursor = conn.cursor()

    for show in shows_data:
        title = show['title']
        
        # 1. Comprobamos si la serie ya existe en la base de datos
        cursor.execute("SELECT COUNT(1) FROM dbo.Shows WHERE Title = ?", title)
        exists = cursor.fetchone()[0]

        if exists > 0:
            print(f"⏭️ La serie '{title}' ya existe en la base de datos. Saltando...")
            continue

        # 2. Si no existe, generamos el embedding y la insertamos
        print(f"🧠 Generando embedding para nueva serie: '{title}'...")
        vector = get_embedding(show['synopsis'])
        vector_json = json.dumps(vector)

        print(f"💾 Insertando '{title}' en Azure SQL...")
        cursor.execute("""
            INSERT INTO dbo.Shows (Title, Genre, ReleaseYear, Synopsis, EmbeddingJson)
            VALUES (?, ?, ?, ?, ?)
        """, title, show['genre'], show['year'], show['synopsis'], vector_json)
        
        conn.commit()

    cursor.close()
    conn.close()
    print('✅ ¡Proceso de sincronización completado sin duplicados!')

if __name__ == '__main__':
    main()