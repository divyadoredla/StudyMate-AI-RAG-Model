"""
text_splitter.py  —  Stage 3 of the RAG pipeline
──────────────────────────────────────────────────
WHAT THIS FILE DOES:
  Takes the giant string produced by pdf_loader.py and splits it into
  smaller overlapping chunks that can be embedded and stored in FAISS.

WHY CHUNKING IS THE MOST IMPORTANT STAGE:
  Bad chunking = bad answers. Period.

  Too large chunks (chunk_size=5000):
    → Each chunk covers too many topics → embeddings become vague
    → Retrieval matches the wrong sections
    → LLM gets irrelevant context → hallucinates

  Too small chunks (chunk_size=100):
    → Each chunk has too little context
    → "B+ Tree" might appear in a chunk that doesn't explain it
    → Answers are incomplete and confusing

  No overlap (chunk_overlap=0):
    → If the answer spans the boundary between two chunks, it gets cut in half
    → The retriever picks only one half → incomplete answer

  chunk_size=1000, chunk_overlap=200 is the sweet spot for academic notes.

IMPORTS EXPLAINED:
  langchain.text_splitter.RecursiveCharacterTextSplitter
    — This is BETTER than CharacterTextSplitter.
      It tries to split on paragraphs first, then sentences, then words,
      then characters — in that priority order.
      CharacterTextSplitter only splits on one separator (\n) and
      can produce awkward mid-sentence chunks.
"""

try:
    from langchain_text_splitters import RecursiveCharacterTextSplitter
except ImportError:
    from langchain.text_splitter import RecursiveCharacterTextSplitter
# WHY RecursiveCharacterTextSplitter over CharacterTextSplitter?
# RecursiveCharacterTextSplitter tries these separators in order:
#   ["\n\n", "\n", " ", ""]
# This means it prefers to split at paragraph breaks, then line breaks,
# then spaces. CharacterTextSplitter only uses ONE separator ("\n").
# Result: RecursiveCharacterTextSplitter produces more natural chunks.


def get_text_chunks(text: str) -> list[str]:
    """
    Splits a large string into overlapping text chunks suitable for
    embedding and vector storage.

    HOW THE PARAMETERS WORK:
        chunk_size=1000:
            Each chunk will be AT MOST 1000 characters.
            Why 1000? It's small enough to produce precise embeddings
            but large enough to contain a complete concept (e.g., the
            full explanation of a B+ Tree insertion algorithm).

        chunk_overlap=200:
            The last 200 characters of chunk N are repeated as the
            first 200 characters of chunk N+1.
            WHY? Academic text often defines a term on one line and
            explains it on the next. Without overlap, a chunk could
            end right after "B+ Tree is defined as:" and the next
            chunk would start mid-explanation with no context.

        length_function=len:
            We measure chunk size in characters (not tokens).
            Token-based splitting is more accurate for LLM context
            limits, but character-based is simpler and works fine
            for our use case.

        separators=["\n\n", "\n", " ", ""]:
            Tries to split at double newlines (paragraph breaks) first,
            then single newlines, then spaces, then characters.
            This is the default for RecursiveCharacterTextSplitter.

    Args:
        text: The full extracted text from all PDFs combined.

    Returns:
        list[str]: List of text chunks, each ~1000 characters.
                   Returns empty list if input is empty.

    COMMON ERRORS:
        • "chunks is empty list" → text extraction failed upstream.
          Fix: Print len(text) before calling this function to verify
          that pdf_loader actually returned something.
        • Very long PDFs produce thousands of chunks → slow embedding.
          Fix: Increase chunk_size to 1500 or reduce overlap to 100
          for large textbooks.
    """
    if not text or not text.strip():
        return []

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
        # add_start_index=True adds character position metadata to each chunk.
        # Useful for Phase 4 (Source Citation) — we can say "found at char 4200".
        add_start_index=True,
    )

    chunks = text_splitter.split_text(text)
    return chunks


def get_text_chunks_with_metadata(text: str, source_name: str = "document") -> list:
    """
    PHASE 4 VARIANT — produces LangChain Document objects instead of
    plain strings. Each Document carries metadata (source filename,
    chunk index) that we later display as source citations.

    Use this instead of get_text_chunks() once you implement Phase 4.

    Args:
        text: Extracted PDF text.
        source_name: The PDF filename, stored as metadata.

    Returns:
        list[Document]: LangChain Document objects with .page_content
                        and .metadata = {"source": source_name, "chunk": N}
    """
    from langchain.schema import Document

    if not text or not text.strip():
        return []

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
        add_start_index=True,
    )

    raw_chunks = text_splitter.split_text(text)

    # Wrap each chunk in a Document object so the vector store
    # can store and return the metadata alongside the text.
    documents = [
        Document(
            page_content=chunk,
            metadata={"source": source_name, "chunk_index": i}
        )
        for i, chunk in enumerate(raw_chunks)
    ]
    return documents
