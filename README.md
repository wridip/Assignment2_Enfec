# Semantic vs Keyword Search Application

This project demonstrates the difference between Keyword Search (Exact match) and Semantic Search (Vector-based similarity) using Django, PostgreSQL with `pgvector`, and Streamlit.

---

## ✅ STEP 1 – Setup PostgreSQL with pgvector

### 1. Install PostgreSQL
If Windows:
Install via official PostgreSQL installer.

### 2. Install pgvector
To install the extension, you can build it from source or use Docker.

Option A: Install on Windows (Native x64)
1. Open "x64 Native Tools Command Prompt for VS 2022" as Administrator.
2. Run:
   ```cmd
   set "PGROOT=C:\Program Files\PostgreSQL\16"
   cd %TEMP%
   git clone --branch v0.8.0 https://github.com/pgvector/pgvector.git
   cd pgvector
   nmake /F Makefile.win
   nmake /F Makefile.win install
   ```

Option B: Use Docker (Recommended)
```bash
docker run --name semantic-db -e POSTGRES_PASSWORD=YOUR_DB_PASSWORD -p 5433:6379 -d pgvector/pgvector:pg16
```

After Container Starts
Connect: 
```
docker exec -it YOUR_DB_NAME psql -U postgres
```

Then create databse:
```
CREATE DATABASE semantic_search;
\c semantic_search
```

Connect to your database and run:
```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

### 3. Create table using either PSQL tool or Query tool
IMPORTANT: `all-MiniLM-L6-v2` produces 384-dimensional vectors (NOT 1536).

Correct schema:
```sql
CREATE TABLE documents (
  id SERIAL PRIMARY KEY,
  title VARCHAR(500),
  content TEXT,
  embedding VECTOR(384)
);
```

### 4. Create vector index
```sql
CREATE INDEX ON documents
USING ivfflat (embedding vector_cosine_ops);
```

---

## 2. Setup Virtual Environment

It is recommended to use a virtual environment to manage project dependencies.

1.  Create a virtual environment:
    ```bash
    python -m venv venv
    ```
2.  Activate the virtual environment:
    - Windows: `venv\Scripts\activate`
    - Mac/Linux: `source venv/bin/activate`
3.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

---

## 3. How to load sample documents

1.  Ensure your database is configured in `backend/core/settings.py` and `backend/ingest.py`.
2.  Navigate to the backend directory:
    ```bash
    cd backend
    ```
3.  Run the ingestion script:
    ```bash
    python ingest.py
    ```

---

## 4. How to run the app

### Start the Backend (Django)
1.  Apply migrations:
    ```bash
    python manage.py migrate
    ```
2.  Start the server:
    ```bash
    python manage.py runserver
    ```

### Start the Frontend (Streamlit)
1.  Open a new terminal (with the virtual environment activated).
2.  Run the Streamlit app:
    ```bash
    streamlit run ui/app.py
    ```

---

## 5. Comparison Notes

### Semantic Search vs. Keyword Search
Keyword search relies on exact character matching (using `ILIKE` in this project). It is fast but fails when the user uses synonyms or conceptually related terms that don't share exact words. Semantic search, powered by vector embeddings, understands the context and "meaning" behind words. It maps text into a high-dimensional space where similar concepts are physically closer together, allowing it to retrieve relevant results even when there is no keyword overlap.

Example:
If a user searches for "How do computers learn from data?", keyword search might only return "What is Machine Learning?" because it contains the phrase "learn from data". However, semantic search will also return "Deep Learning Overview", "Neural Networks Explained", and "Reinforcement Learning Concepts" because it understands these topics are subsets or related concepts of computers learning from data, even if those specific words are missing from their descriptions.
