"""
pdf_loader.py  —  Stage 1 & 2 of the RAG pipeline
──────────────────────────────────────────────────
WHAT THIS FILE DOES:
  Takes a list of uploaded PDF files (Streamlit UploadedFile objects)
  and returns a single string of all the text inside them.

WHY IT EXISTS:
  We need raw text before we can chunk, embed, or search anything.
  Separating this into its own module means app.py stays clean,
  and you can swap PyPDF for another loader (PDFPlumber, Unstructured)
  without touching any other file.

IMPORTS EXPLAINED:
  pypdf.PdfReader  — modern, actively maintained PDF parser.
                     PyPDF2 is deprecated; pypdf is its official successor.
  streamlit        — only imported here for type hinting in the docstring;
                     the actual UploadedFile type lives in Streamlit's internals.

COMMON ERRORS & FIXES:
  • "No text extracted" → The PDF is image-based (scanned). You need OCR.
    Fix: Use pytesseract + pdf2image instead of pypdf.
  • "PdfReadError: EOF marker not found" → Corrupted PDF.
    Fix: The try/except below skips broken files and logs a warning.
  • "UnicodeDecodeError" → Some PDFs have weird encodings.
    Fix: pypdf handles this better than PyPDF2 — another reason to upgrade.
"""

import streamlit as st
from pypdf import PdfReader   # pip install pypdf  (NOT PyPDF2)


def get_pdf_text(pdf_docs: list) -> str:
    """
    Accepts a list of Streamlit UploadedFile objects (the PDFs the user
    dragged into the sidebar uploader) and returns all their text
    concatenated into one big string.

    WHY ONE BIG STRING?
    The next stage (chunking) will intelligently split this string.
    We don't need to track which page came from which file at this point —
    the vector store will handle relevance ranking.

    Args:
        pdf_docs: list of streamlit.runtime.uploaded_file_manager.UploadedFile

    Returns:
        str: All text from all pages of all PDFs, concatenated.
             Returns empty string if no text could be extracted.
    """
    full_text = ""

    for pdf_file in pdf_docs:
        try:
            # PdfReader accepts a file-like object — Streamlit UploadedFile
            # IS a file-like object, so this works directly.
            reader = PdfReader(pdf_file)

            for page_number, page in enumerate(reader.pages):
                # extract_text() returns a string or None if the page
                # contains only images (scanned text).
                page_text = page.extract_text()

                if page_text:
                    # We add a newline between pages so chunks don't
                    # accidentally merge the last sentence of page N
                    # with the first sentence of page N+1.
                    full_text += page_text + "\n"
                else:
                    # Silently skip blank/image-only pages.
                    # You could log this with st.warning() if you want
                    # to tell the user which pages were skipped.
                    pass

        except Exception as e:
            # Don't crash the whole app if one PDF is corrupt.
            # Show a small warning and continue with the other files.
            st.warning(f"⚠️ Could not read '{pdf_file.name}': {e}")
            continue

    return full_text


def get_pdf_metadata(pdf_docs: list) -> list[dict]:
    """
    BONUS UTILITY (used in Phase 4 — Source Citation).
    Returns metadata about each PDF: filename, page count, file size.

    This is how we later say "Answer found on page 3 of DBMS_Notes.pdf"

    Args:
        pdf_docs: list of UploadedFile objects

    Returns:
        list of dicts: [{"name": "DBMS.pdf", "pages": 42, "size_kb": 320}, ...]
    """
    metadata = []
    for pdf_file in pdf_docs:
        try:
            reader = PdfReader(pdf_file)
            metadata.append({
                "name": pdf_file.name,
                "pages": len(reader.pages),
                "size_kb": round(pdf_file.size / 1024, 1)
            })
            # IMPORTANT: Reset the file pointer after reading metadata.
            # Once PdfReader reads a file-like object, the cursor is at the end.
            # If get_pdf_text() runs after this, it would read 0 bytes.
            pdf_file.seek(0)
        except Exception:
            continue
    return metadata
