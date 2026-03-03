from django.shortcuts import render

# Create your views here.
from django.http import JsonResponse
from django.db import connection
from sentence_transformers import SentenceTransformer
from django.views.decorators.csrf import csrf_exempt
import time

# Load model once (VERY IMPORTANT)
model = SentenceTransformer("all-MiniLM-L6-v2")


# ----------------------------
# Keyword Search
# ----------------------------
def keyword_search(request):
    query = request.GET.get("q")

    if not query:
        return JsonResponse({"error": "Query parameter 'q' is required"}, status=400)

    start = time.time()

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT id, title, content
            FROM documents
            WHERE content ILIKE %s
            LIMIT 5;
        """, [f"%{query}%"])

        rows = cursor.fetchall()

    results = [
        {
            "id": r[0],
            "title": r[1],
            "content": r[2]
        }
        for r in rows
    ]

    return JsonResponse({
        "type": "keyword",
        "response_time": round(time.time() - start, 4),
        "results": results
    })


# ----------------------------
# Semantic Search
# ----------------------------
import json

@csrf_exempt
def semantic_search(request):

    if request.method != "POST":
        return JsonResponse({"error": "POST method required"}, status=405)

    try:
        body = json.loads(request.body)
        query = body.get("query")
    except Exception:
        return JsonResponse({"error": "Invalid JSON body"}, status=400)

    if not query:
        return JsonResponse({"error": "Query is required"}, status=400)

    start = time.time()

    query_embedding = model.encode(query).tolist()

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT id, title, content,
                   (embedding <=> %s::vector) AS distance
            FROM documents
            ORDER BY distance
            LIMIT 5;
        """, [query_embedding])

        rows = cursor.fetchall()

    results = [
        {
            "id": r[0],
            "title": r[1],
            "content": r[2],
            "similarity": round(1 - r[3], 4)
        }
        for r in rows
    ]

    return JsonResponse({
        "type": "semantic",
        "response_time": round(time.time() - start, 4),
        "results": results
    })