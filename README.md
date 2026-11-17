# 🎬 azureSQLSeries — Búsqueda Semántica de Series

**Un motor de recomendación Full-Stack Cloud Native que conecta Azure SQL Database con Azure AI Foundry para buscar series por su "vibra" o contexto mediante IA de grado empresarial.**

![Arquitectura v4.0.0](docs/architecture-v4.jpeg)

---

## 🛑 El problema
Los buscadores tradicionales en bases de datos relacionales (con cláusulas `LIKE` o `Freetext`) son rígidos: si el usuario busca *"comedia ligera sobre la vida en la oficina"*, pero la base de datos dice *"Sitcom de trabajo"*, no hay resultados. Las primeras iteraciones de motores semánticos resolvían parte del problema, pero dependían de hardware local (Ollama) y sufrían de "miopía de contexto" (ej. no asociar *Game of Thrones* con "castillos" si la sinopsis no incluía la palabra explícita). Necesitábamos una arquitectura 100% en la nube, escalable, con una interfaz web real y enriquecimiento de datos para lograr una precisión absoluta.

## ✨ Qué hace
1. **Data Enrichment & Ingesta (1536D):** Concatena metadatos clave (Título, Género, Año y Sinopsis) antes de vectorizarlos con **Azure OpenAI (`text-embedding-3-small`)**, generando representaciones matemáticas ultraprecisas de 1536 dimensiones.
2. **Búsqueda Semántica Full-Stack:** Permite buscar series en lenguaje natural desde una interfaz web moderna y reactiva, devolviendo resultados ordenados por porcentaje de afinidad.
3. **Cálculo Optimizado (Pushdown Compute):** Realiza toda la carga matemática (Similitud del Coseno) directamente dentro de Azure SQL mediante *Stored Procedures*, recibiendo vectores desde la API sin saturar la memoria del servidor backend.
4. **Desacoplamiento Total:** El Frontend (Angular) consume un contrato de datos estricto (`ShowItem`), siendo completamente agnóstico al motor de IA o base de datos que opera en el Backend (FastAPI).

## 🏗️ Cómo lo construí
El proyecto sigue una arquitectura Full-Stack Cloud Native:
- **Frontend:** Angular v21 (Standalone Components) para un renderizado reactivo y tipado estricto.
- **Backend (API):** Python con **FastAPI**, orquestando la comunicación asíncrona y gestionando políticas de CORS.
- **Modelo de IA:** Azure AI Foundry (OpenAI `text-embedding-3-small`) a través del SDK oficial de Python.
- **Base de Datos:** Azure SQL Database (Serverless) alojando los vectores y delegando la lógica matemática a T-SQL mediante `OPENJSON` y *Stored Procedures*.
- **Seguridad y Auditoría:** Autenticación local mediante `.env` y control de cambios en la base de datos con *System-Versioning* (Temporal Tables).

## 🚀 Cómo probarlo

### 1. Variables de Entorno (`.env`)
Crea un archivo `.env` en la raíz del backend:
```env
AZURE_SERVER=sql-server-sergio-dp800.database.windows.net
AZURE_DATABASE=TVShowDB
AZURE_USER=admiuser
AZURE_PASSWORD=TuContraseñaSegura

AZURE_OPENAI_ENDPOINT=https://tu-recurso-openai.openai.azure.com/
AZURE_OPENAI_API_KEY=TuClaveDeAPI
```

### 2. Instalación y Ejecución

**Paso 1: Backend y ETL (Python/FastAPI)**
```bash
# Navegar al backend, crear entorno virtual e instalar dependencias
cd backend
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install fastapi uvicorn pyodbc openai python-dotenv

# Opcional: Re-ingestar catálogo con Data Enrichment (borrar BD primero)
python scripts/01_populate_embeddings.py

# Iniciar la API REST
uvicorn main:app --reload
```

**Paso 2: Frontend (Angular)**
```bash
# En una nueva terminal, navegar al frontend
cd frontend

# Instalar dependencias e iniciar el servidor de desarrollo
npm install
ng serve
```
Abre `http://localhost:4200` en tu navegador para interactuar con la aplicación.

## 🧠 Aprendizajes
- **El Poltergeist de los Vectores (Dimension Mismatch):** Al migrar de Ollama (768D) a OpenAI (1536D), aprendí que mezclar dimensionalidades en la base de datos genera resultados ruidosos e incoherentes. La limpieza de la BD y la idempotencia del pipeline ETL son vitales.
- **El poder del Data Enrichment:** Los modelos LLM son rehenes del texto proporcionado. Inyectar el género y el título explícitamente en el texto base de la vectorización elevó drásticamente la precisión para búsquedas conceptuales (ej. resolver el puente semántico entre "magia/castillos" y la serie *The Witcher*).
- **Contratos de API Desacoplados:** Migrar todo el motor de IA subyacente de local a Cloud sin tener que alterar una sola línea de código en Angular demostró el inmenso valor de las arquitecturas orientadas a servicios (SOA).
- **Preparación DP-800:** Diseñar flujos de trabajo con Azure OpenAI y delegar procesamiento analítico-matemático a Azure SQL han sido prácticas directas para dominar el diseño de soluciones de IA en bases de datos relacionales Microsoft.

## 🗺️ Próximos pasos (Roadmap)
- [x] **v1.0.0 (MVP):** Pipeline ETL y cálculo de similitud vectorial client-side (Python/Ollama local).
- [x] **v2.0.0 (Optimización):** Delegación del cálculo de Similitud del Coseno a Azure SQL (Pushdown Compute).
- [x] **v3.0.0 (Full-Stack):** Evolución a aplicación web completa con Backend modular en **FastAPI** y Frontend reactivo en **Angular**.
- [x] **v4.0.0 (Cloud Native):** Migración a **Azure OpenAI (`text-embedding-3-small`)**, adopción de 1536 dimensiones e implementación de *Data Enrichment* en el ETL.