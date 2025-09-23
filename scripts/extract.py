import os
import shutil
import subprocess
import re
from typing import Optional, List

import fitz  # PyMuPDF

# ==============================================================================
# ### NEW - CONFIGURATION FOR CLEANING ###
# ==============================================================================
# IMPORTANT: You MUST customize this list with common, repetitive text
# found in the headers or footers of YOUR documents.
COMMON_HEADERS_FOOTERS: List[str] = [
    "9th ANNUAL REPORT 2017-2018",
    "CENTRAL UNIVERSITY OF RAJASthan",
    # Add more common phrases you find here...
]

# ==============================================================================
# ### NEW - The Cleaning Function ###
# ==============================================================================
def clean_page_text(text: str, headers_footers: List[str]) -> str:
    """
    Cleans the raw OCR text for a single page.
    """
    # 1. Remove non-ASCII characters and other OCR noise
    text = re.sub(r'[^\x00-\x7F]+', '', text)

    # 2. Remove user-defined common headers and footers
    for item in headers_footers:
        # Case-insensitive replacement
        text = re.sub(re.escape(item), '', text, flags=re.IGNORECASE)

    # 3. Normalize whitespace: replace multiple spaces/newlines with a single space
    text = re.sub(r'\s+', ' ', text).strip()

    return text


def is_digital(pdf_path: str) -> bool:
    try:
        with fitz.open(pdf_path) as doc:
            text_pages = sum(1 for page in doc if page.get_text().strip())
            if doc.page_count != text_pages:
                return False
            return True
    except Exception:
        return False


def ghostscript_repair(pdf_path: str, repaired_dir: str) -> str:
    os.makedirs(repaired_dir, exist_ok=True)
    out_path = os.path.join(repaired_dir, os.path.basename(pdf_path))

    # Try common Ghostscript executables on Windows, then generic 'gs'
    gs_candidates = ["gswin64c", "gswin32c", "gs"]
    gs = None
    for cand in gs_candidates:
        try:
            subprocess.run([cand, "-v"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            gs = cand
            break
        except Exception:
            continue

    if gs is None:
        raise RuntimeError("Ghostscript not found. Install it and ensure 'gswin64c' is on PATH.")

    subprocess.run(
        [gs, "-o", out_path, "-sDEVICE=pdfwrite", "-dPDFSETTINGS=/prepress", pdf_path],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return out_path


def ocr_extract(pdf_path: str, ocr_dir: str, reader, dpi: int = 200) -> str:
    os.makedirs(ocr_dir, exist_ok=True)
    base = os.path.splitext(os.path.basename(pdf_path))[0]
    txt_path = os.path.join(ocr_dir, f"{base}_ocr.txt")

    with fitz.open(pdf_path) as doc, open(txt_path, "w", encoding="utf-8") as txt_file:
        for page_num in range(doc.page_count):
            page = doc.load_page(page_num)
            pix = page.get_pixmap(dpi=dpi)
            # Following the existing pattern in your repo: feed bytes to EasyOCR
            ocr_result = reader.readtext(pix.tobytes(), detail=0, paragraph=True)
            txt_file.write(f"Page {page_num + 1}:\n")
            txt_file.write(" ".join(ocr_result))
            txt_file.write("\n" + "-" * 80 + "\n")

    return txt_path


def process_pdf(pdf_path: str, repaired_dir: str, ocr_dir: str, error_dir: Optional[str] = None, reader=None) -> None:
    try:
        if is_digital(pdf_path):
            ghostscript_repair(pdf_path, repaired_dir)
            print(f"Digital (repaired): {os.path.basename(pdf_path)}")
        else:
            # Lazy import to avoid requiring EasyOCR if only repairing
            global easyocr
            if reader is None:
                import easyocr  # type: ignore

                reader = easyocr.Reader(["hi", "en"])  # initialize once if needed
            ocr_extract(pdf_path, ocr_dir, reader)
            print(f"Scanned (OCRed): {os.path.basename(pdf_path)}")
    except Exception as e:
        print(f"Error processing {os.path.basename(pdf_path)}: {e}")
        if error_dir:
            os.makedirs(error_dir, exist_ok=True)
            try:
                shutil.copy(pdf_path, os.path.join(error_dir, os.path.basename(pdf_path)))
            except Exception:
                pass


def main(
    input_dir: str = "../pdfs",
    repaired_dir: str = "../sorted_data/repaired",
    ocr_dir: str = "../ocr_texts",
    error_dir: Optional[str] = "../sorted_data/error",
    limit: Optional[int] = 50,
):
    if not os.path.isdir(input_dir):
        print(f"Input directory '{input_dir}' does not exist.")
        return

    os.makedirs(repaired_dir, exist_ok=True)
    os.makedirs(ocr_dir, exist_ok=True)
    if error_dir:
        os.makedirs(error_dir, exist_ok=True)

    # Initialize EasyOCR reader once for scanned PDFs
    reader = None
    try:
        import easyocr  # type: ignore

        reader = easyocr.Reader(["hi", "en"], gpu=True)  # heavy init; do once
    except Exception:
        # Defer to lazy init in process_pdf for cases that actually need OCR
        reader = None

    count = 0
    for filename in sorted(os.listdir(input_dir)):
        if not filename.lower().endswith(".pdf"):
            continue
        if limit is not None and count >= limit:
            break
        pdf_path = os.path.join(input_dir, filename)
        process_pdf(pdf_path, repaired_dir, ocr_dir, error_dir=error_dir, reader=reader)
        count += 1

    print("Processing completed.")


if __name__ == "__main__":
    main()
