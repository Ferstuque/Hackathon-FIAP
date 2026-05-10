"""
RAG Pipeline — Debug Knowledge Base (support/rag_pipeline.py)
Template used by the `debugger` agent for persisting and searching debug knowledge.
"""

import os
import json
import uuid
from datetime import datetime
from typing import Optional

import psycopg2
from psycopg2.extras import RealDictCursor
# Optional local embedder
try:
    from sentence_transformers import SentenceTransformer
except Exception:
    SentenceTransformer = None

# --- Config ---
DB_URL = os.getenv("DATABASE_URL", "postgresql://user:pass@localhost:5432/debug_db")
EMBED_MODEL_NAME = os.getenv("EMBED_MODEL", "all-MiniLM-L6-v2")
TOP_K_RESULTS = int(os.getenv("RAG_TOP_K", "5"))


def get_connection():
    return psycopg2.connect(DB_URL, cursor_factory=RealDictCursor)


def get_embedder():
    if SentenceTransformer is None:
        raise RuntimeError("sentence-transformers não disponível. Instale 'sentence-transformers' ou configure outra estratégia de embeddings.")
    return SentenceTransformer(EMBED_MODEL_NAME)


def generate_embedding(text: str) -> list[float]:
    model = get_embedder()
    emb = model.encode(text, normalize_embeddings=True)
    return emb.tolist()


def save_debug_entry(project_name: str, error_slug: str, debug_data: dict) -> str:
    combined_text = " ".join([
        debug_data.get("title", ""),
        debug_data.get("root_cause", ""),
        debug_data.get("solution", ""),
        " ".join(debug_data.get("tags", [])),
    ])

    embedding = None
    try:
        embedding = generate_embedding(combined_text)
    except Exception:
        embedding = None

    sql = """
        INSERT INTO debug_knowledge_base
            (project_name, project_language, error_slug, debug_data, embedding)
        VALUES (%s, 'python', %s, %s, %s)
        ON CONFLICT (error_slug) DO UPDATE
            SET debug_data  = EXCLUDED.debug_data,
                embedding   = EXCLUDED.embedding,
                updated_at  = NOW()
        RETURNING id;
    """

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (project_name, error_slug, json.dumps(debug_data), embedding))
            result = cur.fetchone()
            conn.commit()

    return str(result["id"])


def search_similar_debugs(query: str, project_name: Optional[str] = None, top_k: int = TOP_K_RESULTS) -> list[dict]:
    embedding = None
    try:
        embedding = generate_embedding(query)
    except Exception:
        embedding = None

    sql = """
        SELECT 
            id,
            project_name,
            error_slug,
            debug_data,
            created_at
        FROM debug_knowledge_base
        WHERE (%s IS NULL OR project_name = %s)
        ORDER BY created_at DESC
        LIMIT %s;
    """

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (project_name, project_name, top_k))
            return [dict(row) for row in cur.fetchall()]
