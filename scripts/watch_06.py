#!/usr/bin/env python3
"""
06_watch.py - Watch Folder Background Service

Monitors watch_folders/ for document changes and automatically processes them.
Supports static, dynamic, and miscellaneous folders with hybrid classification.

Features:
- Real-time file monitoring using watchfiles (Rust-based)
- Automatic text extraction from PDF, DOCX, XLSX, PPTX, HTML, TXT
- AI-powered hybrid classification for miscellaneous folder (60% threshold)
- Weaviate vector database integration
- Processed files archived with timestamps
- Graceful shutdown handling

Usage:
    python scripts/06_watch.py

    # Run in background (Windows)
    Start-Process python -ArgumentList "scripts/06_watch.py" -WindowStyle Hidden

    # Stop: Ctrl+C or close terminal
"""

import os
import sys
import shutil
import signal
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple, List

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Third-party imports
from watchfiles import watch, Change
import weaviate
from dotenv import load_dotenv

# Local imports - reusing existing pipeline functions
from extract_02 import (
    extract_pdf as _extract_pdf_to_file,
    extract_docx,
    extract_xlsx,
    extract_pptx,
    extract_html,
    extract_txt,
    clean_text,
    is_digital,
)
from classifier_03 import load_model, classify_text
from curation_04 import embed_and_insert, create_collection

# Load environment
load_dotenv()

# ==================== CONFIGURATION ====================

WATCH_BASE_DIR = "./watch_folders"
WATCH_FOLDERS = {
    "static": os.path.join(WATCH_BASE_DIR, "static"),
    "dynamic": os.path.join(WATCH_BASE_DIR, "dynamic"),
    "miscellaneous": os.path.join(WATCH_BASE_DIR, "miscellaneous"),
}
PROCESSED_DIR = os.path.join(WATCH_BASE_DIR, "processed")

# Hybrid classification threshold
CONFIDENCE_THRESHOLD = 0.60

# Supported file extensions
SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".xlsx", ".pptx", ".html", ".htm", ".txt"}

# Weaviate configuration
WEAVIATE_URL = os.getenv("WEAVIATE_URL", "http://localhost:8080")
WEAVIATE_API_KEY = os.getenv("WEAVIATE_API_KEY")

# Global state
classifier_model = None
classifier_tokenizer = None
classifier_device = None
weaviate_client = None
running = True


# ==================== HELPER FUNCTIONS ====================


def init_classifier():
    """Initialize classification model (lazy loading)"""
    global classifier_model, classifier_tokenizer, classifier_device

    if classifier_model is None:
        print("🔧 Initializing classification model...")
        classifier_model, classifier_tokenizer, classifier_device = load_model()
        print("✅ Classification model ready")


def init_weaviate():
    """Initialize Weaviate client"""
    global weaviate_client

    if weaviate_client is None:
        print("🔧 Connecting to Weaviate...")

        if WEAVIATE_API_KEY:
            weaviate_client = weaviate.connect_to_weaviate_cloud(
                cluster_url=WEAVIATE_URL,
                auth_credentials=weaviate.auth.AuthApiKey(WEAVIATE_API_KEY),
            )
        else:
            weaviate_client = weaviate.connect_to_local(host=WEAVIATE_URL.replace("http://", ""))

        # Ensure collections exist
        for collection_name in ["static", "dynamic"]:
            if not weaviate_client.collections.exists(collection_name):
                print(f"📦 Creating collection: {collection_name}")
                create_collection(weaviate_client, collection_name)

        print("✅ Weaviate connected")


def extract_text_from_file(file_path: str) -> Optional[str]:
    """
    Extract text from any supported file format.
    Returns cleaned text or None on error.
    """
    ext = Path(file_path).suffix.lower()

    try:
        if ext == ".pdf":
            # PDF needs special handling - extract_pdf returns text directly
            import fitz

            if is_digital(file_path):
                # Digital PDF
                with fitz.open(file_path) as doc:
                    text_parts = []
                    for page_num, page in enumerate(doc, 1):
                        text = page.get_text()
                        if text.strip():
                            text_parts.append(text)
                    text = "\n".join(text_parts)
            else:
                # Scanned PDF - use OCR
                try:
                    import easyocr

                    reader = easyocr.Reader(["hi", "en"], gpu=False)

                    with fitz.open(file_path) as doc:
                        text_parts = []
                        for page_num in range(doc.page_count):
                            page = doc.load_page(page_num)
                            pix = page.get_pixmap(dpi=200)
                            ocr_result = reader.readtext(pix.tobytes(), detail=0, paragraph=True)
                            text_parts.append(" ".join(ocr_result))
                    text = "\n".join(text_parts)
                except ImportError:
                    print("⚠️  EasyOCR not available, skipping scanned PDF")
                    return None

        elif ext == ".docx":
            text = extract_docx(file_path)
        elif ext == ".xlsx":
            text = extract_xlsx(file_path)
        elif ext == ".pptx":
            text = extract_pptx(file_path)
        elif ext in [".html", ".htm"]:
            text = extract_html(file_path)
        elif ext == ".txt":
            text = extract_txt(file_path)
        else:
            print(f"❌ Unsupported file type: {ext}")
            return None

        return clean_text(text) if text else None

    except Exception as e:
        print(f"❌ Error extracting text from {Path(file_path).name}: {e}")
        return None


def classify_for_miscellaneous(text: str) -> List[str]:
    """
    Classify text for miscellaneous folder using hybrid approach.

    Returns:
        List of collection names: ["static"], ["dynamic"], or ["static", "dynamic"]
    """
    init_classifier()

    label, confidence, scores = classify_text(text, classifier_model, classifier_tokenizer, classifier_device)

    print(f"   📊 Classification: {label} (confidence: {confidence:.2%})")
    print(f"      Scores: static={scores['static']:.2%}, dynamic={scores['dynamic']:.2%}")

    # Hybrid logic: if confidence >= 60%, use that label; else add to both
    if confidence >= CONFIDENCE_THRESHOLD:
        return [label]
    else:
        print(f"   ⚠️  Low confidence ({confidence:.2%} < {CONFIDENCE_THRESHOLD:.0%}), adding to BOTH collections")
        return ["static", "dynamic"]


def process_and_insert(file_path: str, target_collections: List[str]) -> bool:
    """
    Process file and insert into specified Weaviate collection(s).

    Args:
        file_path: Path to the file to process
        target_collections: List of collection names to insert into

    Returns:
        True if successful, False otherwise
    """
    init_weaviate()

    # Extract text
    text = extract_text_from_file(file_path)
    if not text:
        return False

    # Prepare metadata
    filename = Path(file_path).name
    metadata = {
        "file_name": filename,
        "source": "watch_folder",
        "processed_date": datetime.now().isoformat(),
    }

    # Insert into each target collection
    for collection_name in target_collections:
        try:
            print(f"   💾 Inserting into '{collection_name}' collection...")

            # Use embed_and_insert from curation_04.py
            from llama_index.core import Document

            doc = Document(text=text, metadata=metadata)

            embed_and_insert(
                documents=[doc],
                client=weaviate_client,
                collection_name=collection_name,
            )

            print(f"   ✅ Successfully added to '{collection_name}'")

        except Exception as e:
            print(f"   ❌ Error inserting into '{collection_name}': {e}")
            return False

    return True


def move_to_processed(file_path: str) -> None:
    """Move processed file to archive with timestamp"""
    try:
        # Create date-based subfolder
        date_folder = datetime.now().strftime("%Y-%m-%d")
        archive_dir = os.path.join(PROCESSED_DIR, date_folder)
        os.makedirs(archive_dir, exist_ok=True)

        # Move file with timestamp
        filename = Path(file_path).name
        timestamp = datetime.now().strftime("%H%M%S")
        base, ext = os.path.splitext(filename)
        archived_name = f"{base}_{timestamp}{ext}"

        dest_path = os.path.join(archive_dir, archived_name)
        shutil.move(file_path, dest_path)

        print(f"   📁 Archived to: {os.path.relpath(dest_path)}")

    except Exception as e:
        print(f"   ⚠️  Could not archive file: {e}")


def delete_from_database(filename: str, collection_names: List[str]) -> None:
    """
    Delete document from Weaviate collection(s) by filename.

    Args:
        filename: Name of the file to delete
        collection_names: List of collections to delete from
    """
    init_weaviate()

    for collection_name in collection_names:
        try:
            collection = weaviate_client.collections.get(collection_name)

            # Delete all objects with matching filename
            result = collection.data.delete_many(
                where={"path": ["file_name"], "operator": "Equal", "valueText": filename}
            )

            if result.successful > 0:
                print(f"   🗑️  Deleted {result.successful} object(s) from '{collection_name}'")
            else:
                print(f"   ℹ️  No matching documents found in '{collection_name}'")

        except Exception as e:
            print(f"   ❌ Error deleting from '{collection_name}': {e}")


# ==================== EVENT HANDLERS ====================


def handle_file_added(file_path: str, folder_type: str) -> None:
    """Handle new file addition"""
    filename = Path(file_path).name

    # Skip README files and hidden files
    if filename.startswith(".") or filename.upper() == "README.TXT":
        return

    # Check extension
    if Path(file_path).suffix.lower() not in SUPPORTED_EXTENSIONS:
        print(f"⚠️  Skipping unsupported file: {filename}")
        return

    print(f"\n➕ NEW FILE: {filename} [{folder_type}]")

    # Determine target collection(s)
    if folder_type == "static":
        target_collections = ["static"]
    elif folder_type == "dynamic":
        target_collections = ["dynamic"]
    elif folder_type == "miscellaneous":
        # Extract and classify
        text = extract_text_from_file(file_path)
        if not text:
            return
        target_collections = classify_for_miscellaneous(text)
    else:
        return

    # Process and insert
    success = process_and_insert(file_path, target_collections)

    if success:
        move_to_processed(file_path)
        print(f"✅ {filename} processed successfully!\n")
    else:
        print(f"❌ {filename} processing failed\n")


def handle_file_modified(file_path: str, folder_type: str) -> None:
    """Handle file modification (treat as re-add)"""
    filename = Path(file_path).name

    if filename.startswith(".") or filename.upper() == "README.TXT":
        return

    print(f"\n🔄 MODIFIED FILE: {filename} [{folder_type}]")

    # Delete old version(s) from database
    if folder_type == "miscellaneous":
        # Could be in either collection
        delete_from_database(filename, ["static", "dynamic"])
    else:
        delete_from_database(filename, [folder_type])

    # Re-process as new file
    handle_file_added(file_path, folder_type)


def handle_file_deleted(file_path: str, folder_type: str) -> None:
    """Handle file deletion"""
    filename = Path(file_path).name

    if filename.startswith(".") or filename.upper() == "README.TXT":
        return

    print(f"\n🗑️  DELETED FILE: {filename} [{folder_type}]")

    # Remove from database
    if folder_type == "miscellaneous":
        delete_from_database(filename, ["static", "dynamic"])
    else:
        delete_from_database(filename, [folder_type])

    print(f"✅ {filename} removed from database\n")


# ==================== MAIN WATCH LOOP ====================


def process_event(change: Change, file_path: str) -> None:
    """Process a single file system event"""
    # Determine which watch folder this belongs to
    file_path_obj = Path(file_path)

    for folder_type, folder_path in WATCH_FOLDERS.items():
        if str(file_path_obj.parent).startswith(os.path.abspath(folder_path)):
            if change == Change.added:
                handle_file_added(file_path, folder_type)
            elif change == Change.modified:
                handle_file_modified(file_path, folder_type)
            elif change == Change.deleted:
                handle_file_deleted(file_path, folder_type)
            break


def signal_handler(sig, frame):
    """Handle graceful shutdown"""
    global running
    print("\n\n🛑 Shutting down watch service...")
    running = False

    # Close Weaviate connection
    if weaviate_client:
        weaviate_client.close()

    print("👋 Goodbye!")
    sys.exit(0)


def main():
    """Main watch loop"""
    global running

    # Setup signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Ensure watch folders exist
    for folder_path in WATCH_FOLDERS.values():
        os.makedirs(folder_path, exist_ok=True)
    os.makedirs(PROCESSED_DIR, exist_ok=True)

    print("=" * 70)
    print("👀 WATCH FOLDER SERVICE STARTED")
    print("=" * 70)
    print(f"📁 Monitoring folders:")
    for name, path in WATCH_FOLDERS.items():
        print(f"   - {name}: {os.path.abspath(path)}")
    print(f"\n💡 Supported formats: {', '.join(SUPPORTED_EXTENSIONS)}")
    print(f"🤖 Hybrid classification threshold: {CONFIDENCE_THRESHOLD:.0%}")
    print(f"\n⚠️  Press Ctrl+C to stop\n")
    print("=" * 70)

    try:
        # Watch all folders
        watch_paths = list(WATCH_FOLDERS.values())

        for changes in watch(watch_paths):
            if not running:
                break

            for change, file_path in changes:
                process_event(change, file_path)

    except KeyboardInterrupt:
        signal_handler(None, None)

    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        if weaviate_client:
            weaviate_client.close()
        sys.exit(1)


if __name__ == "__main__":
    main()
