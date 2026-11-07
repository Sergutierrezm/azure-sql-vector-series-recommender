import json
import pyodbc
import requests

# ---------------------------------------------------------
# 1. Configuración de Conexión a Azure SQL y Ollama
# ---------------------------------------------------------
AZURE_SERVER = 'sql-server-sergio-dp800.database.windows.net'
AZURE_DATABASE = 'TVShowDB'
AZURE_USER = 'admiuser'
AZURE_PASSWORD = 'TuPasswordSegura123!'  # <--- Reemplaza con tu contraseña real de Azure SQL

OLLAMA_URL = 'http://localhost:11434/api/embeddings'
OLLAMA_MODEL = 'nomic-embed-text'  # El modelo de embeddings que tengas en Ollama

CONN_STR = (
    f'DRIVER={{ODBC Driver 18 for SQL Server}};'
    f'SERVER={AZURE_SERVER};'
    f'DATABASE={AZURE_DATABASE};'
    f'UID={AZURE_USER};'
    f'PWD={AZURE_PASSWORD};'
    f'Encrypt=yes;TrustServerCertificate=no;'
)

# ---------------------------------------------------------
# 2. Dataset de prueba (Series y Sinopsis)
# ---------------------------------------------------------
SHOWS_DATA = [
    {
        'title': 'Breaking Bad',
        'genre': 'Drama',
        'year': 2008,
        'synopsis': (
            'A high school chemistry teacher diagnosed with inoperable lung'
            ' cancer turns to manufacturing and selling methamphetamine with a'
            ' former student.'
        ),
    },
    {
        'title': 'Stranger Things',
        'genre': 'Sci-Fi',
        'year': 2016,
        'synopsis': (
            'When a young boy vanishes, a small town uncovers a mystery'
            ' involving secret experiments, terrifying supernatural forces and'
            ' one strange little girl.'
        ),
    },
    {
        'title': 'The Office',
        'genre': 'Comedy',
        'year': 2005,
        'synopsis': (
            'A mockumentary on a group of typical office workers, where the'
            ' workday consists of ego clashes, inappropriate behavior, and'
            ' tedium.'
        ),
    },
    {
        'title': 'Game of Thrones',
        'genre': 'Fantasy',
        'year': 2011,
        'synopsis': (
            'Nine noble families fight for control over the lands of Westeros,'
            ' while an ancient enemy returns after being dormant for thousands'
            ' of years.'
        ),
    },
    {
        'title': 'Black Mirror',
        'genre': 'Sci-Fi',
        'year': 2011,
        'synopsis': (
            'An anthology series exploring a twisted, high-tech multiverse'
            ' where humanity\'s greatest innovations and darkest instincts'
            ' collide.'
        ),
    },
]


def get_embedding(text):
  """Llama a la API local de Ollama para convertir la sinopsis en un vector."""
  payload = {'model': OLLAMA_MODEL, 'prompt': text}
  response = requests.post(OLLAMA_URL, json=payload)
  if response.status_code == 200:
    return response.json().get('embedding')
  else:
    raise Exception(f'Error en Ollama: {response.text}')


def main():
  print('🔌 Conectando a Azure SQL Database...')
  conn = pyodbc.connect(CONN_STR)
  cursor = conn.cursor()

  for show in SHOWS_DATA:
    print(f"🧠 Generando embedding para: '{show['title']}'...")
    vector = get_embedding(show['synopsis'])
    vector_json = json.dumps(vector)

    print(f"💾 Insertando '{show['title']}' en Azure SQL...")
    cursor.execute(
        """
        INSERT INTO dbo.Shows (Title, Genre, ReleaseYear, Synopsis, EmbeddingJson)
        VALUES (?, ?, ?, ?, ?)
    """,
        show['title'],
        show['genre'],
        show['year'],
        show['synopsis'],
        vector_json,
    )

  conn.commit()
  cursor.close()
  conn.close()
  print('✅ ¡Proceso completado! Todas las series y sus vectores están en Azure.')


if __name__ == '__main__':
  main()