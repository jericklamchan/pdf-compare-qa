import logging
import sys
from pathlib import Path

import fitz  # PyMuPDF

log = logging.getLogger(__name__)

MIN_CHARS = 20  # below this, the page probably has no text layer (scanned)


def extract_pages(path: str | Path) -> list[dict]:
    """Return [{page, text, needs_ocr}] with 1-based page numbers."""
    pages = []
    with fitz.open(path) as doc:
        for i, page in enumerate(doc, start=1):
            text = page.get_text("text").strip()
            needs_ocr = len(text) < MIN_CHARS
            if needs_ocr:
                log.warning("%s page %d has little or no text; OCR needed", path, i)
            pages.append({"page": i, "text": text, "needs_ocr": needs_ocr})
    return pages


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    for p in extract_pages(sys.argv[1]):
        print(f"--- page {p['page']} (needs_ocr={p['needs_ocr']}) ---")
        print(p["text"])