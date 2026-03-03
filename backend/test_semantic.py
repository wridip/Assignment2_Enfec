import psycopg2
from sentence_transformers import SentenceTransformer

# DB config
DB_NAME = "semantic_db"
DB_USER = "postgres"
DB_PASSWORD = "bittu12345"
DB_HOST = "localhost"
DB_PORT = "5433"

# Load model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Connect DB
conn = psycopg2.connect(
    dbname="semantic_db",
    user="postgres",
    password="bittu12345",
    host="localhost",
    port="5433"
)

query = input("Enter search query: ")

# Generate embedding
query_embedding = model.encode(query).tolist()

with conn.cursor() as cursor:
    cursor.execute("""
        SELECT title, content,
               (embedding <=> %s::vector) AS distance
        FROM documents
        ORDER BY distance
        LIMIT 5;
    """, (query_embedding,))
    
    results = cursor.fetchall()

print("\nTop 5 Semantic Results:\n")

for r in results:
    similarity = 1 - r[2]
    print(f"Title: {r[0]}")
    print(f"Similarity: {round(similarity, 4)}")
    print(f"Content: {r[1]}")
    print("-" * 50)

conn.close()