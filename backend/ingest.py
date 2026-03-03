import os
import sys
import time
import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
from sentence_transformers import SentenceTransformer

# ----------------------------
# Configuration
# ----------------------------
DB_NAME = "semantic_db"
DB_USER = "postgres"
DB_PASSWORD = "yourpassword"
DB_HOST = "localhost"
DB_PORT = "5433"

CSV_PATH = "../data/documents.csv"
BATCH_SIZE = 10  # insert in small batches

# ----------------------------
# Initialize Model
# ----------------------------
print("Loading embedding model...")
model = SentenceTransformer("all-MiniLM-L6-v2")
print("Model loaded successfully.")

# ----------------------------
# Database Connection
# ----------------------------
def get_connection():
    try:
        conn = psycopg2.connect(
            dbname="DB_NAME",
            user="DB_USER",
            password="DB_PASSWORD",
            host="DB_HOST",
            port="DB_PORT"
        )
        print("Connected to PostgreSQL.")
        return conn
    except Exception as e:
        print("Database connection failed:", e)
        sys.exit(1)

# ----------------------------
# Read CSV
# ----------------------------
def load_csv(path):
    if not os.path.exists(path):
        print("CSV file not found:", path)
        sys.exit(1)

    df = pd.read_csv(path)
    
    if "title" not in df.columns or "content" not in df.columns:
        print("CSV must contain 'title' and 'content' columns.")
        sys.exit(1)

    print(f"Loaded {len(df)} documents from CSV.")
    return df

# ----------------------------
# Generate Embeddings
# ----------------------------
def generate_embeddings(texts):
    return model.encode(texts, show_progress_bar=True).tolist()

# ----------------------------
# Insert into DB
# ----------------------------
def insert_documents(conn, records):
    with conn.cursor() as cursor:
        insert_query = """
            INSERT INTO documents (title, content, embedding)
            VALUES %s
            ON CONFLICT DO NOTHING
        """
        execute_values(cursor, insert_query, records)
    conn.commit()

# ----------------------------
# Main Ingestion Logic
# ----------------------------
def ingest():
    start_time = time.time()

    conn = get_connection()
    df = load_csv(CSV_PATH)

    titles = df["title"].tolist()
    contents = df["content"].tolist()

    print("Generating embeddings...")
    embeddings = generate_embeddings(contents)

    print("Preparing records for insertion...")
    records = []
    for i in range(len(df)):
        records.append((
            titles[i],
            contents[i],
            embeddings[i]
        ))

    print("Inserting into database in batches...")
    for i in range(0, len(records), BATCH_SIZE):
        batch = records[i:i + BATCH_SIZE]
        insert_documents(conn, batch)
        print(f"Inserted {i + len(batch)} / {len(records)} documents")

    conn.close()

    print("Ingestion completed.")
    print("Total time:", round(time.time() - start_time, 2), "seconds")

# ----------------------------
# Run Script
# ----------------------------
if __name__ == "__main__":
    ingest()