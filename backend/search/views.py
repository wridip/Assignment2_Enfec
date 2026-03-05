from django.shortcuts import render

# Create your views here.
from django.http import JsonResponse
from django.db import connection
from sentence_transformers import SentenceTransformer
from django.views.decorators.csrf import csrf_exempt
import time
import json
import redis

# Load model once (VERY IMPORTANT)
model = SentenceTransformer("all-MiniLM-L6-v2")

redis_client = redis.Redis(
    host='localhost',
    port=6379,
    db=0,
    decode_responses=True
)

# Keyword Search
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


# Semantic Search
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

    # Create cache key
    cache_key = f"semantic:{query}"

    # Check Redis first
    cached_result = redis_client.get(cache_key)

    if cached_result:
        cached_data = json.loads(cached_result)
        cached_data["cached"] = True
        return JsonResponse(cached_data)

    # If not cached → compute normally
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

    response_data = {
        "type": "semantic",
        "response_time": round(time.time() - start, 4),
        "cached": False,
        "results": results
    }

    # Store in Redis (TTL 1 hour)
    redis_client.setex(cache_key, 3600, json.dumps(response_data))

    return JsonResponse(response_data)
"""
    return JsonResponse({
        "type": "semantic",
        "response_time": round(time.time() - start, 4),
        "results": results
    })
"""

