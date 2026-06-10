"""
validator.py - Validates intent preservation using Sentence-BERT cosine similarity.
"""
from sentence_transformers import SentenceTransformer, util

_sbert_model = None
SIMILARITY_THRESHOLD = 0.75

def get_sbert():
    global _sbert_model
    if _sbert_model is None:
        _sbert_model = SentenceTransformer("all-MiniLM-L6-v2")
    return _sbert_model

def validate_intent_preservation(original: str, rewritten: str) -> dict:
    model = get_sbert()
    emb_orig = model.encode(original,   convert_to_tensor=True)
    emb_rew  = model.encode(rewritten,  convert_to_tensor=True)
    similarity = float(util.cos_sim(emb_orig, emb_rew).item())

    preserved = similarity >= SIMILARITY_THRESHOLD
    return {
        "similarity":  round(similarity, 4),
        "preserved":   preserved,
        "threshold":   SIMILARITY_THRESHOLD,
        "warning":     None if preserved else "Intent may have drifted. Similarity below threshold.",
    }
