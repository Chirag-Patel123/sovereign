# Ingestion piece — scanned document → searchable chunks

Your job: prove that a scanned document can be turned into text, and that
a question can find the right piece of that text. This is a standalone demo
that doesn't depend on anyone else's work.

## Setup
```bash
pip install -r requirements.txt
```
Let PaddleOCR download its models on first run — do this well before rehearsal,
not the night of.

## Your demo plan (follow in order)

### Step 1 — Check OCR quality first
```bash
python ingestion.py --ocr-only your_document.png
```
Read the printed text carefully. Is it accurate? If it's garbled or missing
words, the image quality is the problem — try a clearer scan/photo before
moving on. Don't skip this step; bad OCR poisons everything after it.

### Step 2 — Run the full pipeline
```bash
python ingestion.py your_document.png "a real question about the document"
```
This does all 4 steps: extract text -> chunk it -> embed it -> find the
best-matching chunk for your question.

### Step 3 — Try a few different questions
Run it 3 times with 3 different questions about the same document. Note
which ones give clearly correct, relevant answers.

### Step 4 — Pick your 2 best questions
These become your fixed demo script. Don't improvise questions live —
use the ones you've already proven give a clean answer.

## If something's off
- **Garbled OCR text** → clearer scan/photo, not a code fix
- **Wrong chunk returned** → try a smaller chunk size (edit `chunk_size=200`
  in `chunk_text()`, try 100) or rephrase the question closer to the
  document's own wording
- **First run is slow** → sentence-transformers downloads a small model
  the first time only, that's normal

## Handoff (once your demo works)
The `chunks` list built in `chunk_text()` is what gets handed to the agent —
nothing else in this file needs to change for integration.
