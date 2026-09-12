"""
Your piece: scanned document -> searchable chunks.
Now using pytesseract instead of PaddleOCR (much lighter, fewer dependency
issues, works great on clean/printed documents like your demo samples).

SETUP (one-time):
1. Install Tesseract itself (the OCR engine):
   https://github.com/UB-Mannheim/tesseract/wiki  (Windows installer)
   Default install path: C:\\Program Files\\Tesseract-OCR\\tesseract.exe

2. Install the Python wrapper:
   uv pip install pytesseract pillow

TWO WAYS TO RUN THIS:

1. Check OCR quality only (do this first, on your real demo document):
    python ingestion.py --ocr-only path/to/your/document.png

2. Full pipeline - extract, chunk, embed, and search:
    python ingestion.py path/to/your/document.png "your test question"

Example:
    python ingestion.py sample_internal_standard.png "what is the max pressure allowed?"
"""

import sys
import os
import numpy as np


# ---------------------------------------------------------------------------
# STEP 1: Get text out of the scanned document (using pytesseract)
# ---------------------------------------------------------------------------

# If Tesseract isn't on your PATH, uncomment and set the path below:
# import pytesseract
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def extract_text(file_path: str) -> str:
    import pytesseract
    from PIL import Image

    # Point pytesseract at the default Windows install location if it's
    # there and not already on PATH -- avoids a common "tesseract not found" error.
    default_win_path = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    if os.name == "nt" and os.path.exists(default_win_path):
        pytesseract.pytesseract.tesseract_cmd = default_win_path

    img = Image.open(file_path)
    text = pytesseract.image_to_string(img)
    return text


# ---------------------------------------------------------------------------
# STEP 2: Split the text into small chunks (~200 words each)
# ---------------------------------------------------------------------------
def chunk_text(text: str, chunk_size: int = 50) -> list[str]:
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size):
        chunk = " ".join(words[i:i + chunk_size])
        if chunk.strip():
            chunks.append(chunk)
    return chunks


# ---------------------------------------------------------------------------
# STEP 3: Turn chunks into vectors (numbers that represent meaning)
# ---------------------------------------------------------------------------
def embed_chunks(chunks: list[str]):
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer("all-MiniLM-L6-v2")
    vectors = model.encode(chunks)
    return model, vectors


# ---------------------------------------------------------------------------
# STEP 4: Given a question, find the closest-matching chunk
# ---------------------------------------------------------------------------
def search(query: str, model, chunks: list[str], chunk_vectors) -> str:
    query_vector = model.encode([query])[0]
    similarities = chunk_vectors @ query_vector
    best_index = int(np.argmax(similarities))
    return chunks[best_index]


# ---------------------------------------------------------------------------
# Run everything end to end
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    args = sys.argv[1:]

    # Mode 1: OCR-only check -- run this first on your real demo document
    if args and args[0] == "--ocr-only":
        if len(args) < 2:
            print("Usage: python ingestion.py --ocr-only <document_path>")
            sys.exit(1)

        file_path = args[1]
        print(f"[OCR-ONLY] Reading text from {file_path} ...")
        text = extract_text(file_path)
        print(f"           Extracted {len(text.split())} words.\n")
        print("=== RAW EXTRACTED TEXT ===")
        print(text)
        print("\n(Check this text is accurate before running the full pipeline.)")
        sys.exit(0)

    # Mode 2: Full pipeline
    if len(args) < 2:
        print('Usage:')
        print('  python ingestion.py --ocr-only <document_path>')
        print('  python ingestion.py <document_path> "<your question>"')
        sys.exit(1)

    file_path = args[0]
    question = args[1]

    print(f"[1/4] Reading text from {file_path} ...")
    text = extract_text(file_path)
    print(f"      Extracted {len(text.split())} words.")

    print("[2/4] Splitting into chunks ...")
    chunks = chunk_text(text)
    print(f"      Got {len(chunks)} chunks.")

    print("[3/4] Turning chunks into searchable vectors ...")
    model, chunk_vectors = embed_chunks(chunks)

    print(f"[4/4] Searching for: \"{question}\"")
    answer_chunk = search(question, model, chunks, chunk_vectors)

    print("\n=== BEST MATCHING CHUNK ===")
    print(answer_chunk)