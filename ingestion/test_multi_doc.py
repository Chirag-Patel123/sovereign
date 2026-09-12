"""
Real test of retrieval: load MULTIPLE documents into one knowledge base,
then check that a question about doc A returns a chunk from doc A, and a
question about doc B returns a chunk from doc B. This is what actually
proves discrimination -- the single-document tests couldn't.

Usage:
    python test_multi_doc.py doc1.png doc2.png [doc3.png ...]
"""

import sys
from ingestion import extract_text, chunk_text, embed_chunks, search


def main():
    doc_paths = sys.argv[1:]
    if len(doc_paths) < 2:
        print("Usage: python test_multi_doc.py doc1.png doc2.png [doc3.png ...]")
        sys.exit(1)

    all_chunks = []
    chunk_sources = []   # tracks which document each chunk came from

    for path in doc_paths:
        print(f"Reading {path} ...")
        text = extract_text(path)
        chunks = chunk_text(text)
        all_chunks.extend(chunks)
        chunk_sources.extend([path] * len(chunks))

    print(f"\nTotal chunks across all documents: {len(all_chunks)}")

    print("Embedding all chunks together ...")
    model, chunk_vectors = embed_chunks(all_chunks)

    # A few test questions -- one clearly about each doc, plus an edge case
    test_questions = [
        "what is the maximum pressure allowed?",
        "what did the inspector find on line PW-114?",
        "what is the flow velocity measured?",
    ]

    for q in test_questions:
        answer = search(q, model, all_chunks, chunk_vectors)
        source = chunk_sources[all_chunks.index(answer)]
        print(f"\nQ: {q}")
        print(f"   -> matched chunk from: {source}")
        print(f"   -> answer: {answer[:150]}...")


if __name__ == "__main__":
    main()
