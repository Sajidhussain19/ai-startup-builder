import json
import os

# ============================================
# PRODUCTION-SAFE MEMORY STORE
# ✅ Works without sentence-transformers/faiss
# ✅ Falls back to simple JSON search in production
# ============================================

try:
    import faiss
    import numpy as np
    from sentence_transformers import SentenceTransformer
    MEMORY_ENABLED = True
    model = SentenceTransformer('all-MiniLM-L6-v2')
    print("✅ Memory enabled — FAISS + sentence-transformers loaded")
except ImportError:
    MEMORY_ENABLED = False
    print("⚠️ Memory disabled — running in production mode without FAISS")

# Storage paths
INDEX_PATH = "../generated_startups/memory.index"
DATA_PATH = "../generated_startups/memory_data.json"


def get_embedding(text: str):
    """Convert text to vector embedding (only when FAISS enabled)"""
    embedding = model.encode([text])
    return np.array(embedding, dtype='float32')


def save_to_memory(idea: str, summary: str):
    """Save a startup idea and its summary to memory"""

    os.makedirs("../generated_startups", exist_ok=True)

    # ✅ Always save to JSON regardless of FAISS
    if os.path.exists(DATA_PATH):
        with open(DATA_PATH, "r") as f:
            data = json.load(f)
    else:
        data = []

    data.append({"idea": idea, "summary": summary})

    with open(DATA_PATH, "w") as f:
        json.dump(data, f, indent=2)

    # ✅ Only use FAISS if available
    if MEMORY_ENABLED:
        if os.path.exists(INDEX_PATH):
            index = faiss.read_index(INDEX_PATH)
        else:
            index = faiss.IndexFlatL2(384)

        embedding = get_embedding(idea)
        index.add(embedding)
        faiss.write_index(index, INDEX_PATH)

    print(f"💾 Saved to memory: {idea[:50]}")
    return {"status": "saved", "memory_enabled": MEMORY_ENABLED}


def search_memory(query: str, top_k: int = 3) -> list:
    """Search memory for similar past startup ideas"""

    if not os.path.exists(DATA_PATH):
        return []

    with open(DATA_PATH, "r") as f:
        data = json.load(f)

    # ✅ FAISS vector search if available
    if MEMORY_ENABLED and os.path.exists(INDEX_PATH):
        index = faiss.read_index(INDEX_PATH)
        query_embedding = get_embedding(query)
        distances, indices = index.search(query_embedding, top_k)

        results = []
        for i, idx in enumerate(indices[0]):
            if idx < len(data):
                results.append({
                    "idea": data[idx]["idea"],
                    "summary": data[idx]["summary"],
                    "similarity_score": float(distances[0][i])
                })
        return results

    # ✅ Fallback: simple keyword search in production
    query_lower = query.lower()
    results = []
    for item in data:
        if any(word in item["idea"].lower() for word in query_lower.split()):
            results.append({
                "idea": item["idea"],
                "summary": item["summary"],
                "similarity_score": 0.0
            })

    return results[:top_k]