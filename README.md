# Semantic vs Keyword Search Application

This project demonstrates the difference between Keyword Search (Exact match) and Semantic Search (Vector-based similarity) using Django, PostgreSQL with `pgvector`, and Streamlit.

---

## STEP 1 – Setup PostgreSQL with pgvector

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

Option B: ## Setup Instructions

### 3. Configure Environment Variables
Copy the example environment file and update it with your credentials:
```bash
cp .env.example .env
```
Edit `.env` and set your `DB_PASSWORD` and other configurations.

### 4. Start Infrastructure (Docker)
The easiest way to run the database and cache is using Docker:

**PostgreSQL with pgvector:**
```bash
docker run --name semantic-db -e POSTGRES_PASSWORD=your_secure_password -p 5433:5432 -d pgvector/pgvector:pg16
```
*(Ensure the password matches what you put in `.env`)*

**Redis:**
```bash
docker run --name semantic-redis -p 6379:6379 -d redis
```

### 5. Initialize Database
Connect to the PostgreSQL instance and create the database and extension:
```bash
docker exec -it semantic-db psql -U postgres -c "CREATE DATABASE semantic_db;"
docker exec -it semantic-db psql -U postgres -d semantic_db -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

### 6. Setup Python Environment
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

pip install -r requirements.txt
```
---

## Data Ingestion

Load the sample documents into the database:
```bash
cd backend
python ingest.py
cd ..
```
---

## Running the Application

### 1. Start Django Backend
```bash
cd backend
python manage.py migrate
python manage.py runserver
```

### 2. Start Streamlit Frontend
Open a new terminal, activate the virtual environment, and run:
```bash
streamlit run ui/app.py
```
---

## 5. Comparison Notes

### Semantic Search vs. Keyword Search
Keyword search relies on exact character matching (using `ILIKE` in this project). It is fast but fails when the user uses synonyms or conceptually related terms that don't share exact words. Semantic search, powered by vector embeddings, understands the context and "meaning" behind words. It maps text into a high-dimensional space where similar concepts are physically closer together, allowing it to retrieve relevant results even when there is no keyword overlap.

Example:
If a user searches for "How do computers learn from data?", keyword search might only return "What is Machine Learning?" because it contains the phrase "learn from data". However, semantic search will also return "Deep Learning Overview", "Neural Networks Explained", and "Reinforcement Learning Concepts" because it understands these topics are subsets or related concepts of computers learning from data, even if those specific words are missing from their descriptions.

ARCHITECTURE:

```

User  
    ↓   
Streamlit
    ↓
Django API
    ↓
Redis (check) → If Hit → Return 
    ↓
If miss → LLM embedding → PostgreSQL vector
    ↓
search
    ↓
Store in Redis
    ↓
Return

```
