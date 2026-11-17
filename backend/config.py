import os
from dotenv import load_dotenv

load_dotenv()

AZURE_SERVER = os.getenv('AZURE_SERVER')
AZURE_DATABASE = os.getenv('AZURE_DATABASE')
AZURE_USER = os.getenv('AZURE_USER')
AZURE_PASSWORD = os.getenv('AZURE_PASSWORD')

AZURE_OPENAI_ENDPOINT = os.getenv('AZURE_OPENAI_ENDPOINT')
AZURE_OPENAI_API_KEY = os.getenv('AZURE_OPENAI_API_KEY')

CONN_STR = (
    f'DRIVER={{ODBC Driver 18 for SQL Server}};'
    f'SERVER={AZURE_SERVER};'
    f'DATABASE={AZURE_DATABASE};'
    f'UID={AZURE_USER};'
    f'PWD={AZURE_PASSWORD};'
    f'Encrypt=yes;TrustServerCertificate=no;'
)