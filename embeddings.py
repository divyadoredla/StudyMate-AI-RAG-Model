"""
embeddings.py  —  Stage 4 of the RAG pipeline
───────────────────────────────────────────────
WHAT THIS FILE DOES:
  Provides a function that returns a pre-loaded HuggingFace embedding
  model. The model converts any text string into a 384-dimensional
  vector (a list of 384 decimal numbers).

WHAT IS AN EMBEDDING? (Interview answer ready)
  An embedding is a numerical representation of text that captures
  its *meaning*. Two sentences that mean similar things will produce
  vectors that are mathematically close to each other.

  Example:
    "How does a B+ Tree index work?"  → [0.23, -0.41, 0.87, ...]
    "Explain B+ Tree indexing"        → [0.24, -0.39, 0.85, ...]  ← very similar
    "What is photosynthesis?"         → [-0.72, 0.11, -0.33, ...] ← very different

  FAISS measures how "close" two vectors are using cosine similarity.
  Vectors that point in nearly the same direction have high similarity.

WHY all-MiniLM-L6-v2?
  • 384 dimensions (vs 768 for larger models) → faster, less RAM
  • Trained on 1B+ sentence pairs → excellent semantic understanding
  • Free, runs locally → no API cost for embedding
  • 22MB model size → downloads once, cached automatically
  • Benchmark: 58.8 on STSB (sentence similarity task) — best in class
    for its speed/accuracy tradeoff

WHY NOT OpenAI embeddings?
  • They cost money per token
  • They require internet access at embedding time
  • all-MiniLM-L6-v2 is 95% as good for academic text at 0% the cost

IMPORTS EXPLAINED:
  langchain_community.embeddings.HuggingFaceEmbeddings
    — LangChain wrapper around sentence-transformers.
      Handles model downloading, caching, and batch encoding.
      The underlying library is sentence-transformers by UKP Lab.

COMMON ERRORS & FIXES:
  • "OSError: [model] not found" → No internet on first run.
    Fix: Run once with internet. Model caches at ~/.cache/huggingface/
  • Slow first run (30–60 seconds) → Model is downloading (22MB).
    Fix: Normal behaviour. Subsequent runs load from cache in ~2 seconds.
  • "RuntimeError: CUDA not available" → You asked for GPU but have none.
    Fix: Set model_kwargs={"device": "cpu"} (already done below).
  • Import error "langchain_community not found":
    Fix: pip install langchain-community
"""

try:
    from langchain_huggingface import HuggingFaceEmbeddings
except ImportError:
    from langchain_community.embeddings import HuggingFaceEmbeddings
# LangChain 0.3+: HuggingFaceEmbeddings moved to langchain_huggingface package
# LangChain 0.2.x: still in langchain_community.embeddings
# The try/except above handles both versions automatically.


# We define the model name as a constant so it's easy to change in one place.
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


def get_embeddings():
    """
    Returns a LangChain-compatible HuggingFaceEmbeddings instance.

    WHY RETURN AN OBJECT INSTEAD OF COMPUTING EMBEDDINGS DIRECTLY?
    LangChain's FAISS.from_texts() and FAISS.from_documents() expect
    an embeddings *object* (not pre-computed vectors). The object
    has an .embed_documents() method that FAISS calls internally.
    This design lets LangChain batch-process chunks efficiently.

    MODEL KWARGS EXPLAINED:
        device: "cpu"
            Forces CPU inference. If you have a GPU and want to use it,
            change this to "cuda". For students, CPU is fine — embedding
            1000 chunks takes ~10 seconds on CPU.

    ENCODE KWARGS EXPLAINED:
        normalize_embeddings: True
            Normalizes vectors to unit length before storing.
            This makes cosine similarity equivalent to dot product,
            which is faster to compute. ALWAYS set this to True
            when using FAISS with cosine similarity.

    Returns:
        HuggingFaceEmbeddings: An embeddings model instance ready to use
                               with FAISS.from_texts() or FAISS.from_documents()

    USAGE EXAMPLE:
        embeddings = get_embeddings()
        # Now pass it to FAISS:
        vectorstore = FAISS.from_texts(chunks, embeddings)
    """
    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL_NAME,
        model_kwargs={"device": "cpu"},    # Use "cuda" if you have a GPU
        encode_kwargs={"normalize_embeddings": True},
        # cache_folder: Optional. Specify a path to cache downloaded models.
        # Useful on shared servers where ~/.cache might not be writable.
        # cache_folder="./models"
    )
    return embeddings


# ── Quick self-test ───────────────────────────────────────────────────────────
# Run this file directly to verify embeddings work before moving on:
#   python embeddings.py
#
# Expected output:
#   Vector shape: 384
#   ✅ Embeddings working correctly
#
if __name__ == "__main__":
    print("Testing embeddings... (first run downloads ~22MB model)")
    emb = get_embeddings()
    test_text = "What is a B+ Tree?"
    # embed_query() converts one string to a vector.
    # embed_documents() converts a list of strings (used by FAISS internally).
    vector = emb.embed_query(test_text)
    print(f"Vector shape: {len(vector)}")       # Should print: 384
    assert len(vector) == 384, "Unexpected vector dimension!"
    print("✅ Embeddings working correctly")
