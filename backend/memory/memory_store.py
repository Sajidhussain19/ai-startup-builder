import faiss
import numpy as np
import json
import os
from sentence_transformers import SentenceTransformer

# Load embedding model
model = SentenceTransformer('all-MiniLM-L6-v2')

# FAISS index storage path
INDEX_PATH = "../generated_startups/memory.index"
DATA_PATH = "../generated_startups/memory_data.json"

def get_embedding(text: str) -> np.ndarray:
    """Convert text to vector embedding"""
    embedding = model.encode([text])
    return np.array(embedding, dtype='float32')

def save_to_memory(idea: str, summary: str):
    """Save a startup idea and its summary to memory"""

    # Load or create index
    if os.path.exists(INDEX_PATH):
        index = faiss.read_index(INDEX_PATH)
        with open(DATA_PATH, "r") as f:
            data = json.load(f)
    else:
        index = faiss.IndexFlatL2(384)  # 384 = embedding size
        data = []

    # Get embedding for the idea
    embedding = get_embedding(idea)

    # Add to index
    index.add(embedding)
    data.append({"idea": idea, "summary": summary})

    # Save index and data
    os.makedirs("../generated_startups", exist_ok=True)
    faiss.write_index(index, INDEX_PATH)
    with open(DATA_PATH, "w") as f:
        json.dump(data, f, indent=2)

    print(f"💾 Saved to memory: {idea[:50]}")

def search_memory(query: str, top_k: int = 3) -> list:
    """Search memory for similar past startup ideas"""

    if not os.path.exists(INDEX_PATH):
        return []

    index = faiss.read_index(INDEX_PATH)
    with open(DATA_PATH, "r") as f:
        data = json.load(f)

    # Get embedding for query
    query_embedding = get_embedding(query)

    # Search
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