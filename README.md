# 🎬 azureSQLSeries — Búsqueda Semántica de Series

**Un motor de recomendación en lenguaje natural que conecta Azure SQL Database con Inteligencia Artificial local (Ollama) para buscar series por su "vibra" o contexto.**

![Arquitectura v2.0.0](docs/architecture-v2.jpeg)

---

## 🛑 El problema
Los buscadores tradicionales en bases de datos relacionales (con cláusulas `LIKE` o `Freetext`) son rígidos: si el usuario busca *"comedia ligera sobre la vida en la oficina"*, pero la base de datos dice *"Sitcom de trabajo"*, no hay resultados. Integrar motores de búsqueda semántica externos suele ser costoso y añade complejidad a la arquitectura. Necesitábamos una forma de buscar por "conceptos abstractos" aprovechando la seguridad y potencia de nuestra base de datos relacional existente.

## ✨ Qué hace
1. **Generación de Vectores:** Convierte catálogos de texto (sinopsis de series) en representaciones matemáticas (vectores de 768 dimensiones) usando IA local.
2. **Búsqueda Semántica:** Permite buscar series usando lenguaje natural y devuelve las más afines.
3. **Cálculo Optimizado (Pushdown Compute):** Realiza toda la carga matemática (Similitud del Coseno) directamente dentro de Azure SQL, evitando saturar la memoria de la aplicación cliente.
4. **Auditoría Continua:** Mantiene un registro inmutable de todos los cambios en el catálogo mediante *System-Versioning* (Temporal Tables).

## 🏗️ Cómo lo construí
El proyecto sigue un enfoque "Backend-first".
- **Modelo de IA:** Ollama con `nomic-embed-text` ejecutándose localmente.
- **Base de Datos:** Azure SQL Database (Serverless) alojando los vectores en formato JSON (`EmbeddingJson`).
- **Procesamiento:** Lógica delegada a T-SQL mediante *Stored Procedures*, uso de `OPENJSON` y variables tipo Tabla para optimizar el rendimiento.
- **Cliente:** Python (`pyodbc`, `requests`) para orquestar la comunicación ETL y las búsquedas.

## 🚀 Cómo probarlo

### 1. Variables de Entorno (`.env`)
Crea un archivo `.env` en la raíz del proyecto:
```env
AZURE_SERVER=sql-server-sergio-dp800.database.windows.net
AZURE_DATABASE=TVShowDB
AZURE_USER=admiuser
AZURE_PASSWORD=TuContraseñaSegura
```

### 2. Instalación y Ejecución
```bash
# Instalar dependencias
pip install pyodbc requests python-dotenv

# 1. Ingestar el catálogo y vectorizar (ETL)
python scripts/01_populate_embeddings.py

# 2. Iniciar el buscador semántico (CLI)
python scripts/02_semantic_search.py
```

## 🧠 Aprendizajes
- **De Python a T-SQL:** Al principio (v1), extraía los vectores de Azure a Python para calcular la similitud. Aprendí que delegar el cálculo a la base de datos (*Stored Procedures* en T-SQL) es infinitamente más eficiente.
- **Optimización Matemática:** Calcular la Similitud del Coseno en SQL Server nativo requirió aprender a manejar `OPENJSON` y extraer pre-cálculos a variables (como la magnitud del vector) para reducir el tiempo de respuesta.
- **Preparación DP-800:** Configurar *Temporal Tables* me enseñó cómo mantener trazabilidad y cumplir con normativas de auditoría de datos en la nube sin esfuerzo adicional de código.

## 🗺️ Próximos pasos (Roadmap)
- [x] **v1.0.0 (MVP):** Pipeline ETL y cálculo de similitud vectorial client-side (Python).
- [x] **v2.0.0 (Optimización):** Delegación del cálculo de Similitud del Coseno a Azure SQL.
- [ ] **v3.0.0 (Full-Stack):** Evolución a aplicación web completa con Backend modular en **FastAPI** y Frontend minimalista en **Angular**.