#!/usr/bin/env python3
"""
07_manual_add.py - Batch Processor for Watch Folders

One-time processing of all pending files in watch_folders/.
Useful for initial setup or bulk document additions.

Features:
- Processes all files in static, dynamic, and miscellaneous folders
- Progress reporting with file counts
- Same logic as 06_watch.py but without monitoring
- Validates files before processing
- Detailed summary report

Usage:
    python scripts/07_manual_add.py
    
    # Process specific folder only
    python scripts/07_manual_add.py --folder static
"""

import os
import sys
import argparse
from pathlib import Path
from typing import List, Dict

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import from 06_watch.py (reuse logic)
from watch_06 import (
    WATCH_FOLDERS,
    SUPPORTED_EXTENSIONS,
    extract_text_from_file,
    classify_for_miscellaneous,
    process_and_insert,
    move_to_processed,
    init_classifier,
    init_weaviate,
)


# ==================== BATCH PROCESSING ====================

def scan_folder(folder_path: str) -> List[str]:
    """
    Scan folder for supported files.
    
    Returns:
        List of file paths to process
    """
    files = []
    
    if not os.path.exists(folder_path):
        return files
    
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        
        # Skip directories and special files
        if not os.path.isfile(file_path):
            continue
        
        if filename.startswith('.') or filename.upper() == 'README.TXT':
            continue
        
        # Check extension
        if Path(file_path).suffix.lower() in SUPPORTED_EXTENSIONS:
            files.append(file_path)
    
    return files


def process_file(file_path: str, folder_type: str) -> Dict:
    """
    Process a single file and return result.
    
    Returns:
        Dict with processing status
    """
    filename = Path(file_path).name
    result = {
        "filename": filename,
        "folder": folder_type,
        "status": "pending",
        "collections": [],
        "error": None,
    }
    
    try:
        # Determine target collection(s)
        if folder_type == "static":
            target_collections = ["static"]
        elif folder_type == "dynamic":
            target_collections = ["dynamic"]
        elif folder_type == "miscellaneous":
            # Extract and classify
            text = extract_text_from_file(file_path)
            if not text:
                result["status"] = "failed"
                result["error"] = "Text extraction failed"
                return result
            target_collections = classify_for_miscellaneous(text)
        else:
            result["status"] = "failed"
            result["error"] = "Unknown folder type"
            return result
        
        result["collections"] = target_collections
        
        # Process and insert
        success = process_and_insert(file_path, target_collections)
        
        if success:
            move_to_processed(file_path)
            result["status"] = "success"
        else:
            result["status"] = "failed"
            result["error"] = "Database insertion failed"
    
    except Exception as e:
        result["status"] = "failed"
        result["error"] = str(e)
    
    return result


def batch_process(folders: List[str] = None) -> Dict:
    """
    Batch process all files in specified folders.
    
    Args:
        folders: List of folder names to process (None = all)
    
    Returns:
        Dict with processing statistics
    """
    # Initialize services
    print("🔧 Initializing services...")
    init_classifier()
    init_weaviate()
    print("✅ Services ready\n")
    
    # Determine which folders to process
    if folders is None:
        folders_to_process = list(WATCH_FOLDERS.keys())
    else:
        folders_to_process = folders
    
    # Scan for files
    print("📂 Scanning for files...")
    all_files = {}
    total_files = 0
    
    for folder_name in folders_to_process:
        if folder_name not in WATCH_FOLDERS:
            print(f"⚠️  Unknown folder: {folder_name}")
            continue
        
        folder_path = WATCH_FOLDERS[folder_name]
        files = scan_folder(folder_path)
        all_files[folder_name] = files
        total_files += len(files)
        
        print(f"   📁 {folder_name}: {len(files)} file(s)")
    
    if total_files == 0:
        print("\n✨ No files to process!")
        return {
            "total": 0,
            "success": 0,
            "failed": 0,
            "results": []
        }
    
    print(f"\n📊 Total files to process: {total_files}")
    print("=" * 70)
    
    # Process files
    results = []
    success_count = 0
    failed_count = 0
    current = 0
    
    for folder_name, files in all_files.items():
        if not files:
            continue
        
        print(f"\n📁 Processing {folder_name.upper()} folder...")
        print("-" * 70)
        
        for file_path in files:
            current += 1
            filename = Path(file_path).name
            
            print(f"\n[{current}/{total_files}] {filename}")
            
            result = process_file(file_path, folder_name)
            results.append(result)
            
            if result["status"] == "success":
                success_count += 1
                collections_str = " & ".join(result["collections"])
                print(f"✅ Success → Added to: {collections_str}")
            else:
                failed_count += 1
                print(f"❌ Failed: {result['error']}")
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 PROCESSING SUMMARY")
    print("=" * 70)
    print(f"✅ Successful: {success_count}")
    print(f"❌ Failed: {failed_count}")
    print(f"📝 Total: {total_files}")
    
    if success_count > 0:
        print(f"\n💾 Documents added to vector database")
    
    if failed_count > 0:
        print(f"\n⚠️  {failed_count} file(s) failed - check errors above")
    
    print("=" * 70)
    
    return {
        "total": total_files,
        "success": success_count,
        "failed": failed_count,
        "results": results,
    }


# ==================== CLI ====================

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Batch process documents from watch folders"
    )
    parser.add_argument(
        "--folder",
        choices=["static", "dynamic", "miscellaneous"],
        help="Process specific folder only (default: all folders)"
    )
    
    args = parser.parse_args()
    
    print("=" * 70)
    print("📦 BATCH DOCUMENT PROCESSOR")
    print("=" * 70)
    print()
    
    folders = [args.folder] if args.folder else None
    
    try:
        stats = batch_process(folders)
        
        # Exit code based on results
        if stats["failed"] > 0:
            sys.exit(1)  # Partial failure
        elif stats["success"] == 0:
            sys.exit(0)  # Nothing to process
        else:
            sys.exit(0)  # All successful
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Processing interrupted by user")
        sys.exit(130)
    
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
