#!/usr/bin/env python3
"""
llama_local.py - Create Weaviate Collections for Agent

Creates three local Weaviate collections:
1. 'static' - From classified_data/static/ (permanent info)
2. 'dynamic' - From classified_data/dynamic/ (time-sensitive info)
3. 'sitemap' - From pages.jl (page summaries)

Uses Ollama BGE-M3 embeddings to match agent.py configuration.
"""

import os
import json
import time
from pathlib import Path
from typing import List, Dict

import weaviate
from dotenv import load_dotenv

# LlamaIndex imports
from llama_index.core import Document, Settings
from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.ollama import OllamaEmbedding

# Weaviate v4 typed helpers
from weaviate.classes.config import Configure, Property, DataType

load_dotenv()

# ---------------- Config ----------------
COLLECTIONS = ["static", "dynamic", "sitemap"]
TEXT_KEY = "text"
BATCH_SIZE = 50

# Data directories
CLASSIFIED_DATA_DIR = "./classified_data"
SITEMAP_FILE = "./pages.jl"

# Ollama settings (must match agent.py)
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
WEAVIATE_API_KEY = os.getenv("WEAVIATE_API_KEY")

# Configure embeddings to match agent.py
Settings.embed_model = OllamaEmbedding(model_name="bge-m3", base_url=OLLAMA_URL)

print(f"[INFO] Using Ollama BGE-M3 embeddings from: {OLLAMA_URL}")


# ---------------- Helper Functions ----------------
def load_classified_documents(category: str) -> List[Document]:
    """Load documents from classified_data/{category}/{pdf,docs,html}/"""
    documents = []
    category_path = Path(CLASSIFIED_DATA_DIR) / category

    if not category_path.exists():
        print(f"[WARN] Directory not found: {category_path}")
        return documents

    # Process each source type (pdf, docs, html)
    for source_type in ["pdf", "docs", "html"]:
        source_dir = category_path / source_type
        if not source_dir.exists():
            continue

        for txt_file in source_dir.glob("*.txt"):
            try:
                with open(txt_file, "r", encoding="utf-8") as f:
                    text = f.read()

                if not text.strip():
                    continue

                # Create document with metadata
                # NOTE: Metadata structure prepared for future customization
                doc = Document(
                    text=text,
                    metadata={
                        "file_name": txt_file.name,
                        "category": category,
                        "source_type": source_type,
                        # Placeholder for additional metadata:
                        # Add custom fields here later (e.g., date, department, etc.)
                    },
                )
                documents.append(doc)

            except Exception as e:
                print(f"[ERROR] Failed to load {txt_file.name}: {e}")

    return documents


def load_sitemap_documents() -> List[Document]:
    """Load documents from pages.jl (sitemap summaries)"""
    documents = []

    if not os.path.exists(SITEMAP_FILE):
        print(f"[WARN] Sitemap file not found: {SITEMAP_FILE}")
        return documents

    try:
        with open(SITEMAP_FILE, "r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, 1):
                try:
                    record = json.loads(line)

                    # Combine title and summary for better context
                    title = record.get("title", "").strip()
                    summary = record.get("summary", "").strip()
                    url = record.get("url", "")
                    fetched_at = record.get("fetched_at", "")

                    if not summary:
                        continue

                    # Create text content
                    text = f"Title: {title}\n\n{summary}" if title else summary

                    # Create document with metadata
                    # NOTE: Metadata structure prepared for future customization
                    doc = Document(
                        text=text,
                        metadata={
                            "file_name": f"page_{line_num}",
                            "url": url,
                            "title": title,
                            "fetched_at": fetched_at,
                            "category": "sitemap",
                            "source_type": "webpage",
                            # Placeholder for additional metadata:
                            # Add custom fields here later
                        },
                    )
                    documents.append(doc)

                except json.JSONDecodeError as e:
                    print(f"[ERROR] Invalid JSON at line {line_num}: {e}")
                except Exception as e:
                    print(f"[ERROR] Failed to process line {line_num}: {e}")

    except Exception as e:
        print(f"[ERROR] Failed to read sitemap file: {e}")

    return documents


def create_collection(client, collection_name: str):
    """Create a Weaviate collection with proper schema"""
    if client.collections.exists(collection_name):
        print(f"[INFO] Collection '{collection_name}' already exists, deleting...")
        client.collections.delete(collection_name)

    # Define properties
    props = [
        Property(name=TEXT_KEY, data_type=DataType.TEXT),
        Property(name="file_name", data_type=DataType.TEXT),
        Property(name="category", data_type=DataType.TEXT),
        Property(name="source_type", data_type=DataType.TEXT),
        # Additional properties for sitemap
        Property(name="url", data_type=DataType.TEXT),
        Property(name="title", data_type=DataType.TEXT),
        Property(name="fetched_at", data_type=DataType.TEXT),
        # Placeholder for future custom properties
        # Add more properties here as needed
    ]

    # Self-provided vectors (we'll compute embeddings)
    vc = Configure.Vectors.named(name="default", vector_config=Configure.Vectors.HnswVector())

    client.collections.create(
        name=collection_name,
        properties=props,
        vectorizer_config=Configure.Vectorizer.none(),  # We provide our own vectors
    )

    print(f"[INFO] Created collection '{collection_name}'")


def chunk_documents(documents: List[Document]) -> List[Document]:
    """Chunk documents into smaller nodes"""
    splitter = SentenceSplitter(chunk_size=512, chunk_overlap=50)

    nodes = splitter.get_nodes_from_documents(documents)

    # Convert nodes back to documents (preserve metadata)
    chunked_docs = []
    for node in nodes:
        doc = Document(text=node.get_content(), metadata=node.metadata)
        chunked_docs.append(doc)

    return chunked_docs


def embed_and_insert(client, collection_name: str, documents: List[Document]):
    """Generate embeddings and insert documents into Weaviate collection"""
    if not documents:
        print(f"[WARN] No documents to insert for '{collection_name}'")
        return

    print(f"[INFO] Processing {len(documents)} documents for '{collection_name}'...")

    # Chunk documents
    chunked_docs = chunk_documents(documents)
    print(f"[INFO] Chunked into {len(chunked_docs)} nodes")

    # Get collection
    coll = client.collections.get(collection_name)

    # Process in batches
    print(f"[INFO] Computing embeddings and inserting...")

    with coll.batch.dynamic() as batch:
        for idx, doc in enumerate(chunked_docs):
            try:
                # Get embedding
                text = doc.get_content()
                embedding = Settings.embed_model.get_text_embedding(text)

                # Prepare properties
                properties = {
                    TEXT_KEY: text,
                    "file_name": doc.metadata.get("file_name", "unknown"),
                    "category": doc.metadata.get("category", "unknown"),
                    "source_type": doc.metadata.get("source_type", "unknown"),
                    "url": doc.metadata.get("url", ""),
                    "title": doc.metadata.get("title", ""),
                    "fetched_at": doc.metadata.get("fetched_at", ""),
                }

                # Add object with vector
                batch.add_object(properties=properties, vector=embedding)

                if (idx + 1) % 10 == 0:
                    print(f"  Processed {idx + 1}/{len(chunked_docs)}...")

            except Exception as e:
                print(f"[ERROR] Failed to process document {idx}: {e}")

    # Verify insertion
    time.sleep(0.5)
    try:
        total = coll.aggregate.over_all(total_count=True).total_count
        print(f"[SUCCESS] Collection '{collection_name}' now has {total} objects")
    except Exception as e:
        print(f"[WARN] Could not verify count: {e}")


# ---------------- Main ----------------
def main():
    """Main function to create and populate Weaviate collections"""

    print("=" * 60)
    print("Creating Weaviate Collections for Agent")
    print("=" * 60)

    # Connect to local Weaviate
    try:
        auth_config = weaviate.auth.AuthApiKey(api_key=WEAVIATE_API_KEY) if WEAVIATE_API_KEY else None
        client = weaviate.connect_to_local(host="localhost", port=8080, auth_credentials=auth_config)
        print("[INFO] Connected to local Weaviate instance")
    except Exception as e:
        print(f"[ERROR] Failed to connect to Weaviate: {e}")
        print("[INFO] Make sure Weaviate is running: docker-compose up -d")
        return

    try:
        # Process each collection
        for collection_name in COLLECTIONS:
            print(f"\n{'='*60}")
            print(f"Processing: {collection_name.upper()}")
            print(f"{'='*60}")

            # Create collection
            create_collection(client, collection_name)

            # Load documents
            if collection_name == "sitemap":
                documents = load_sitemap_documents()
            else:
                documents = load_classified_documents(collection_name)

            print(f"[INFO] Loaded {len(documents)} documents")

            # Embed and insert
            embed_and_insert(client, collection_name, documents)

        # Final summary
        print(f"\n{'='*60}")
        print("Summary")
        print(f"{'='*60}")

        for collection_name in COLLECTIONS:
            try:
                coll = client.collections.get(collection_name)
                total = coll.aggregate.over_all(total_count=True).total_count
                print(f"✅ {collection_name:12} - {total:6} objects")
            except Exception as e:
                print(f"❌ {collection_name:12} - Error: {e}")

        print(f"\n{'='*60}")
        print("Collections ready for agent.py!")
        print(f"{'='*60}\n")

    finally:
        client.close()


if __name__ == "__main__":
    main()
