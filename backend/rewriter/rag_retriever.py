"""
rag_retriever.py
Retrieval Augmented Generation - indexes rewrite_dataset.csv
and retrieves similar email pairs at query time.

No training required. Just indexing for fast similarity search.
Database is built ONCE and persisted on disk.
"""

import os
import pandas as pd

os.environ["CHROMA_TELEMETRY_DISABLED"] = "1"
import chromadb  # type: ignore
from sentence_transformers import SentenceTransformer  # type: ignore
HAS_DEPS = True

BASE_DIR    = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
RAG_DB_PATH = os.path.join(BASE_DIR, 'data', 'rag_db')
REWRITE_CSV = os.path.join(BASE_DIR, 'data', 'raw', 'combined', 'rewrite_dataset.csv')
MAX_PAIRS   = 20000  

_sbert_model   = None
_chroma_client = None
_collection    = None
_rag_available = False  

def get_sbert():
    global _sbert_model
    if _sbert_model is None and HAS_DEPS:
        print("  [RAG] Loading SBERT embedding model...")
        _sbert_model = SentenceTransformer('all-MiniLM-L6-v2')

    return _sbert_model

def get_collection():
    global _chroma_client, _collection
    if _collection is not None:
        return _collection
    if not HAS_DEPS: return None
    try:
        _chroma_client = chromadb.PersistentClient(path=RAG_DB_PATH)
        _collection = _chroma_client.get_collection("email_rewrites")

        print(f"  [RAG] Loaded existing DB ({_collection.count()} pairs)")
        return _collection
    except Exception:
        return None

def database_exists() -> bool:
    col = get_collection()
    return col is not None and col.count() > 0

def build_rag_database() -> bool:
    global _chroma_client, _collection, _rag_available

    if not HAS_DEPS:
        print("  [RAG] Missing dependencies (chromadb or sentence-transformers). RAG disabled.")
        return False

    if not os.path.exists(REWRITE_CSV):
        print(f"  [RAG] rewrite_dataset.csv not found at {REWRITE_CSV}")
        print("  [RAG] RAG disabled. Rewriting will work without examples.")
        return False

    try:
        print(f"  [RAG] Loading rewrite_dataset.csv...")
        df = pd.read_csv(REWRITE_CSV, nrows=MAX_PAIRS)

        # Detect column names
        cols = [c.lower().strip() for c in df.columns]
        df.columns = cols

        if 'source' in cols and 'target' in cols:
            src_col, tgt_col = 'source', 'target'
        elif len(cols) >= 2:
            src_col, tgt_col = cols[0], cols[1]
        else:
            print("  [RAG] Cannot detect source/target columns. RAG disabled.")
            return False

        df = df[[src_col, tgt_col]].dropna()
        df[src_col] = df[src_col].astype(str).str[:300]
        df[tgt_col] = df[tgt_col].astype(str).str[:300]
        df = df[df[src_col].str.len() > 30]
        df = df[df[tgt_col].str.len() > 30]
        df = df.reset_index(drop=True)

        print(f"  [RAG] Encoding {len(df)} email pairs with SBERT...")
        print("  [RAG] This takes 3-5 minutes on first run only...")
        model = get_sbert()
        embeddings = model.encode(
            df[src_col].tolist(),
            batch_size=256,
            show_progress_bar=True
        )

        os.makedirs(RAG_DB_PATH, exist_ok=True)
        _chroma_client = chromadb.PersistentClient(path=RAG_DB_PATH)

        try:
            _chroma_client.delete_collection("email_rewrites")
        except Exception:
            pass

        _collection = _chroma_client.create_collection(
            "email_rewrites",
            metadata={"hnsw:space": "cosine"}
        )

        batch = 500
        for start in range(0, len(df), batch):
            end     = min(start + batch, len(df))
            b_df    = df.iloc[start:end]
            b_embs  = embeddings[start:end]
            _collection.add(
                embeddings = b_embs.tolist(),
                documents  = b_df[src_col].tolist(),
                metadatas  = [{"rewritten": r} for r in b_df[tgt_col].tolist()],
                ids        = [str(i) for i in range(start, end)]
            )
            print(f"  [RAG] Indexed {end}/{len(df)} pairs", end='\r')

        print(f"\n  [RAG] Database built: {_collection.count()} pairs indexed")
        _rag_available = True
        return True

    except Exception as e:
        print(f"  [RAG] Build failed: {e}")
        print("  [RAG] Rewriting will work without RAG examples.")
        return False

def retrieve_similar_examples(query_email: str, n: int = 3) -> list:
    """
    Returns list of similar email pairs:
    [{"original": "...", "rewritten": "..."}, ...]
    Returns empty list if RAG is unavailable.
    """
    try:
        collection = get_collection()
        if collection is None or collection.count() == 0:
            return []

        model = get_sbert()
        query_emb = model.encode([query_email[:300]]).tolist()

        results = collection.query(
            query_embeddings=query_emb,
            n_results=min(n, collection.count()),
        )

        examples = []
        for i in range(len(results['documents'][0])):
            orig = results['documents'][0][i]
            rew  = results['metadatas'][0][i].get('rewritten', '')
            if orig and rew and orig.strip() != rew.strip():
                examples.append({
                    "original":  orig[:250],
                    "rewritten": rew[:250],
                })
        return examples

    except Exception as e:
        print(f"  [RAG] Retrieval error (non-fatal): {e}")
        return []

def setup_rag():
    """
    Called once at backend startup.
    Loads existing database or builds it from rewrite_dataset.csv.
    Safe to call even if CSV is missing — RAG simply stays disabled.
    """
    global _rag_available
    print("  [RAG] Initialising...")

    if database_exists():
        _rag_available = True
        return True

    result = build_rag_database()
    _rag_available = result
    return result

def is_rag_available() -> bool:
    return _rag_available