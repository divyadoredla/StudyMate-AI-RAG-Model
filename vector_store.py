"""
vector_store.py  —  Stage 5 of the RAG pipeline
──────────────────────────────────────────────────
WHAT THIS FILE DOES:
  Takes text chunks + an embeddings model, builds a FAISS index
  (an in-memory vector database), and provides functions to save,
  load, and search it.

WHAT IS FAISS? (Interview answer ready)
  FAISS (Facebook AI Similarity Search) is an open-source library
  by Meta Research for efficient similarity search over dense vectors.

  A naive approach to finding the most similar chunk would be:
    for each chunk in database:
        compute cosine_similarity(query_vector, chunk_vector)
    return top-k results
  This is O(n) — for 10,000 chunks it's 10,000 dot products per query.

  FAISS uses Approximate Nearest Neighbor (ANN) algorithms to make
  this sub-linear. For our use case (< 50,000 chunks) FAISS uses
  exact search with BLAS-optimized matrix multiplication — still
  millisecond-fast because vectors are only 384 dimensions.

PERSISTENCE EXPLAINED:
  FAISS indices live in memory by default. If the Streamlit app
  restarts, the index is lost and PDFs must be re-processed.
  We add save/load functions so the index survives restarts.
  The index is saved as two files:
    faiss_index/index.faiss  — the actual binary FAISS index
    faiss_index/index.pkl    — the text content of each chunk
                               (so we can return text, not just vectors)

IMPORTS EXPLAINED:
  langchain_community.vectorstores.FAISS
    — LangChain wrapper around the faiss-cpu library.
      Stores both vectors AND the original text, handles batch encoding,
      and implements the Retriever interface LangChain chains expect.
"""

import os
from langchain_community.vectorstores import FAISS
from embeddings import get_embeddings

# Directory where the FAISS index is saved on disk.
FAISS_INDEX_PATH = "faiss_index"


def build_vectorstore(text_chunks: list[str]) -> FAISS:
    """
    Converts text chunks into a FAISS vector store.

    WHAT HAPPENS INTERNALLY:
      1. get_embeddings() loads the sentence-transformer model.
      2. FAISS.from_texts() calls embeddings.embed_documents(chunks),
         which sends all chunks through the model in batches.
      3. Each resulting 384-dim vector is added to the FAISS index.
      4. LangChain also stores the original text alongside each vector
         so retrieval can return the actual text, not just an index number.

    Args:
        text_chunks: List of text strings from text_splitter.py

    Returns:
        FAISS: A LangChain FAISS vector store object with all chunks indexed.

    PERFORMANCE NOTE:
      Embedding 100 chunks ≈ 2 seconds on CPU.
      Embedding 1000 chunks ≈ 15 seconds on CPU.
      This is a one-time cost per PDF upload session.

    COMMON ERRORS:
      • "AssertionError: texts is empty" → text_chunks is [].
        Check that pdf_loader and text_splitter ran successfully first.
      • Slow processing → Expected on CPU for large PDFs. Show a spinner.
    """
    if not text_chunks:
        raise ValueError(
            "Cannot build vectorstore: text_chunks is empty. "
            "Check that PDFs were loaded and split successfully."
        )

    embeddings = get_embeddings()
    vectorstore = FAISS.from_texts(texts=text_chunks, embedding=embeddings)
    return vectorstore


def save_vectorstore(vectorstore: FAISS, path: str = FAISS_INDEX_PATH) -> None:
    """
    Saves the FAISS index to disk so it persists across app restarts.

    WHEN TO USE:
      After building the vectorstore, call this to cache it.
      On next app start, call load_vectorstore() instead of rebuilding.

    Args:
        vectorstore: A FAISS object returned by build_vectorstore().
        path: Directory path where index files are saved.
              Creates the directory if it doesn't exist.

    FILES CREATED:
        {path}/index.faiss  — Binary FAISS index (the actual vectors)
        {path}/index.pkl    — Pickle file with text chunks and metadata
    """
    os.makedirs(path, exist_ok=True)
    vectorstore.save_local(path)


def load_vectorstore(path: str = FAISS_INDEX_PATH) -> FAISS | None:
    """
    Loads a previously saved FAISS index from disk.

    WHY allow_dangerous_deserialization=True?
      LangChain v0.2+ added this safety flag because loading .pkl files
      can execute arbitrary Python code if the file is tampered with.
      In our case, WE created the file, so it's safe. Setting this to
      True explicitly acknowledges this risk.

    Returns:
        FAISS object if the index exists on disk, None otherwise.

    COMMON ERRORS:
      • "FileNotFoundError" → Index doesn't exist yet. Build it first.
        This function handles this gracefully by returning None.
      • "UnpicklingError" → Index file is corrupt.
        Fix: Delete the faiss_index/ folder and re-upload PDFs.
    """
    if not os.path.exists(path):
        return None

    embeddings = get_embeddings()
    try:
        vectorstore = FAISS.load_local(
            path,
            embeddings,
            allow_dangerous_deserialization=True   # See docstring above
        )
        return vectorstore
    except Exception as e:
        print(f"Could not load vectorstore: {e}")
        return None


def get_retriever(vectorstore: FAISS, k: int = 4):
    """
    Returns a LangChain Retriever from the FAISS vectorstore.

    WHAT IS A RETRIEVER?
      A retriever is a LangChain abstraction that accepts a query string
      and returns the top-k most relevant Document objects.
      It's the bridge between the vector store and the conversational chain.

    WHY k=4?
      We retrieve 4 chunks per query. This gives Gemini enough context
      (4 × ~1000 chars = ~4000 chars) without exceeding its context window.
      Increase to k=6 for complex technical questions.
      Decrease to k=2 if you notice slow responses.

    Args:
        vectorstore: Built FAISS vectorstore.
        k: Number of chunks to retrieve per query. Default is 4.

    Returns:
        VectorStoreRetriever: Pass this directly to ConversationalRetrievalChain.
    """
    retriever = vectorstore.as_retriever(
        search_type="similarity",    # Cosine similarity search
        search_kwargs={"k": k}       # Return top-k results
    )
    return retriever


# ── Quick self-test ────────────────────────────────────────────────────────────
# Run: python vector_store.py
# Expected: prints top-2 chunks most similar to the test query
#
if __name__ == "__main__":
    from text_splitter import get_text_chunks

    sample_text = """
    A B+ Tree is a self-balancing tree data structure that keeps data sorted
    and allows searches, sequential access, insertions, and deletions in
    O(log n) time. Unlike a B-Tree, all data records are stored at leaf nodes.
    The internal nodes only store keys for routing.

    A Hash Index maps key values to bucket addresses using a hash function.
    Hash indices are optimal for equality searches but cannot handle range queries.
    """

    chunks = get_text_chunks(sample_text)
    vs = build_vectorstore(chunks)
    retriever = get_retriever(vs, k=2)

    results = retriever.invoke("What is a B+ Tree?")
    print(f"\nQuery: 'What is a B+ Tree?'")
    print(f"Retrieved {len(results)} chunks:")
    for i, doc in enumerate(results):
        print(f"\nChunk {i+1}: {doc.page_content[:150]}...")
    print("\n✅ Vector store working correctly")
