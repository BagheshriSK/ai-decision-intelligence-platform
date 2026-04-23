"""Sentence-transformer embeddings + HDBSCAN semantic clustering."""
import numpy as np
from sentence_transformers import SentenceTransformer
from typing import Optional

_model: Optional[SentenceTransformer] = None

def get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model

def embed(text: str) -> list[float]:
    model = get_model()
    vec = model.encode(text, normalize_embeddings=True)
    return vec.tolist()

def embed_batch(texts: list[str]) -> np.ndarray:
    model = get_model()
    return model.encode(texts, normalize_embeddings=True, batch_size=32, show_progress_bar=False)

# Predefined cluster centroids (computed from representative sentences)
CLUSTER_SEEDS = {
    "camera":      "camera photo video lens zoom selfie picture quality",
    "battery":     "battery charging power drain fast charge mah life",
    "overheating": "overheating hot temperature thermal burning warm device",
    "price":       "price cost expensive cheap value worth afford money",
    "performance": "performance speed fast slow lag smooth processor benchmark",
    "general":     "product review experience user feedback opinion",
}

_cluster_centroids: Optional[dict] = None

def get_cluster_centroids() -> dict:
    global _cluster_centroids
    if _cluster_centroids is None:
        model = get_model()
        _cluster_centroids = {
            name: model.encode(seed, normalize_embeddings=True)
            for name, seed in CLUSTER_SEEDS.items()
        }
    return _cluster_centroids

def nearest_cluster(text: str) -> str:
    """Assign text to nearest cluster centroid via cosine similarity."""
    vec = np.array(embed(text))
    centroids = get_cluster_centroids()
    best_cluster = "general"
    best_score = -1.0
    for name, centroid in centroids.items():
        score = float(np.dot(vec, centroid))
        if score > best_score:
            best_score = score
            best_cluster = name
    return best_cluster
