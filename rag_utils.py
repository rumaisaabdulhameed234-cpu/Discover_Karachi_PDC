import csv
import os
import numpy as np
from sentence_transformers import SentenceTransformer

# Load the embedding model once (cached across calls within the same process)
_model = SentenceTransformer("all-MiniLM-L6-v2")

_PLACES_PATH = os.path.join(os.path.dirname(__file__), "karachi_places.csv")

with open(_PLACES_PATH, "r", encoding="utf-8", newline="") as f:
    _places = list(csv.DictReader(f))

def _place_to_text(place: dict) -> str:
    """Combine a place's fields into a single text blob for embedding."""
    return (
        f"{place['name']} in {place['area']}. "
        f"Category: {place['category']}. "
        f"Price range: {place['price']}. "
        f"Vibe: {place['vibe']}. "
        f"{place['description']}"
    )

# Pre-compute embeddings for every place once at import time
_place_texts = [_place_to_text(p) for p in _places]
_place_embeddings = _model.encode(_place_texts, normalize_embeddings=True)


def search_places(query: str, top_k: int = 4):
    """
    Given a user query, return the top_k most relevant places
    as a list of dicts with keys: name, area, description, price, vibe.
    """
    query_embedding = _model.encode([query], normalize_embeddings=True)[0]

    # Cosine similarity (embeddings are already normalized, so this is just a dot product)
    scores = np.dot(_place_embeddings, query_embedding)

    # Get indices of the top_k highest scores
    top_indices = np.argsort(scores)[::-1][:top_k]

    results = []
    for idx in top_indices:
        place = _places[idx]
        results.append({
            "name": place["name"],
            "area": place["area"],
            "description": place["description"],
            "price": place["price"],
            "vibe": place["vibe"],
        })
    return results