# Ingestion piece — scanned document → searchable chunks

Uses pytesseract (lightweight OCR wrapper) instead of PaddleOCR — far fewer
dependency/version issues, and works great on clean/printed documents like
the sample docs and most real inspection reports/standards.

## Setup

### 1. Install Tesseract itself (the OCR engine, not just the Python package)
Download and run the Windows installer:
https://github.com/UB-Mannheim/tesseract/wiki

Default install path is `C:\Program Files\Tesseract-OCR\tesseract.exe` —
the script already checks this path automatically on Windows, so you
usually don't need to configure anything extra.

### 2. Install the Python packages
```bash
uv pip install -r requirements.txt
```
(or `pip install -r requirements.txt` if you don't have uv — but uv is faster)

## Your demo plan (follow in order)

### Step 1 — Check OCR quality first
```bash
python ingestion.py --ocr-only sample_internal_standard.png
```
Read the printed text carefully. Is it accurate? If it's garbled or missing
words, the image quality is the problem — try a clearer scan/photo before
moving on.

### Step 2 — Run the full pipeline
```bash
python ingestion.py sample_internal_standard.png "what is the max pressure allowed?"
```
This does all 4 steps: extract text -> chunk it -> embed it -> find the
best-matching chunk for your question.

### Step 3 — Try a few different questions
Run it a few times with different questions across the 3 sample documents.
Note which ones give clearly correct, relevant answers.

### Step 4 — Pick your 2 best questions
These become your fixed demo script. Don't improvise questions live —
use the ones you've already proven give a clean answer.

## If something's off
- **"tesseract is not installed or not in PATH" error** → confirm Tesseract
  installed to the default path above, or set the path manually near the
  top of `extract_text()` in `ingestion.py`
- **Garbled OCR text** → clearer scan/photo, not a code fix
- **Wrong chunk returned** → try a smaller chunk size (edit `chunk_size=200`
  in `chunk_text()`, try 100) or rephrase the question closer to the
  document's own wording
- **First run is slow** → sentence-transformers downloads a small model
  the first time only, that's normal

## Handoff (once your demo works)
The `chunks` list built in `chunk_text()` is what gets handed to the agent —
nothing else in this file needs to change for integration.
