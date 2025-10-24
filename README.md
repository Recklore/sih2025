docker-compose up -d
# Website RAG Chatbot for SIH 2025

This repository contains the code for a **multilingual Retrieval-Augmented Generation (RAG) chatbot** built for the **Smart India Hackathon (SIH) 2025**.

The project **scrapes website data**, processes it through an ETL and classification pipeline, stores the knowledge in a vector database, and serves a **tool-augmented RAG agent** capable of responding in multiple languages.

## Core Technologies

- **Language Model (LLM):** Sarvam `sarvam-m` (via Sarvam AI API)
- **Embedding Model:** Ollama `bge-m3` (local embedding endpoint)
- **Vector Database:** Weaviate (self-hosted via Docker)
- **Framework:** LlamaIndex for ingestion, routing, and agent orchestration
- **Scraping & ETL:** Scrapy, PyMuPDF, EasyOCR, BeautifulSoup, Transformers

## How to setup locally

Follow these steps to set up and run the project locally.

### ✅ Prerequisites
- Python **3.10+**
- **Docker** and **Docker Compose**
- **Ollama** runtime with the `bge-m3` model pulled (`ollama pull bge-m3`)
- Optional but recommended: **Ghostscript** (PDF repair) and GPU drivers for EasyOCR
- Active **Sarvam AI API Key** (for summarisation + agent responses)

### 1. Clone the Repository
```bash
git clone https://github.com/NitinDarker/sih2025.git
cd sih2025
```

### 2. Set Up a Virtual Environment

>It's highly recommended to use a virtual environment to manage dependencies.

```bash
python -m venv venv

# Activate it (Windows)
.\venv\Scripts\activate

# Activate it (macOS/Linux)
source venv/bin/activate
```

### 3. Install Dependencies

>Install all the required Python packages using the requirements.txt file.

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root (next to this README). At minimum, provide your Sarvam API key. Optional values let you point to remote services.

```
# File: .env
SARVAM_API_KEY="your-sarvam-api-key"
OLLAMA_URL="http://localhost:11434"         # optional if running Ollama locally
WEAVIATE_API_KEY=""                         # optional when securing Weaviate
WEAVIATE_URL="http://localhost:8080"        # optional override for watch service
```

> The scraper and agent both fall back to truncated text if `SARVAM_API_KEY` is missing, but quality is significantly better with it.

### 5. Start the Weaviate Database

The project ships with a Docker Compose file under `weaviate/`. Make sure Docker Desktop is running, then launch Weaviate:

```bash
cd weaviate
docker-compose up -d
```

This will start Weaviate on `http://localhost:8080` and persist data under `weaviate/weaviate_data/`.

### 6. Run the ETL + Agent Pipeline

The orchestrator at `scripts/main.py` runs the full five-stage pipeline: scraping → text extraction → classification → vector curation → agent.

```bash
python scripts/main.py
```

Useful flags:

- `--skip-scrape`: reuse previously scraped HTML/files
- `--agent-only`: start the agent assuming Weaviate already has data
- `--batch`: non-interactive mode that auto-confirms prompts and runs sample questions

> Start Ollama (`ollama serve`) before running the pipeline so embeddings can be generated.

## Pipeline Overview

1. **Web scraping (`scripts/scrape_01.py`)** – Crawls `curaj.ac.in`, normalises URLs, saves HTML/PDF/Office docs, and summarises pages via Sarvam.
2. **Extraction (`scripts/extract_02.py`)** – Converts PDFs (digital + OCR), DOCX, XLSX, PPTX, HTML into cleaned text segments.
3. **Classification (`scripts/classifier_03.py`)** – Uses mDeBERTa zero-shot classification to sort content into `static` vs `dynamic` knowledge buckets.
4. **Curation (`scripts/curation_04.py`)** – Chunks text, embeds with Ollama `bge-m3`, and populates Weaviate collections (`static`, `dynamic`, `sitemap`).
5. **Agent (`scripts/agent_05.py`)** – Spins up a LlamaIndex ReAct agent exposing three tools (static info, dynamic info, sitemap navigation).

## Script Reference

- `scripts/main.py`: single entry point coordinating every stage with retries, prompts, and status output.
- `scripts/watch_06.py`: background service watching `watch_folders/` to auto-ingest new documents into Weaviate using the same embeddings/classifier stack.
- `scripts/manual_add_07.py`: helper for manually pushing specific documents (see script docstring for usage).
- `scripts/extract_02.py`: standalone ETL utility; run directly to re-process the `data/` directory.
- `scripts/classifier_03.py`: runs classification in isolation and emits `classified_data.json` plus organised folders.

## Watch Folder Automation

Place new files into the relevant subfolder inside `watch_folders/` and run:

```bash
python scripts/watch_06.py
```

The watcher extracts text, classifies it (with hybrid logic for the `miscellaneous` inbox), embeds content, and inserts it into the correct Weaviate collections. Processed files are archived by timestamp under `watch_folders/processed/`.

## Troubleshooting & Tips

- Pull the embedding model once before first run: `ollama pull bge-m3`.
- Ghostscript is required for repairing certain PDFs; install it and ensure `gswin64c` is on `PATH` (Windows).
- EasyOCR downloads model weights on the first run; allow several minutes if GPU drivers are not available.
- Use `docker-compose logs -f` inside the `weaviate/` folder to inspect the vector DB if ingestion fails.
- If the agent cannot connect to Sarvam, check that `SARVAM_API_KEY` is valid and the API is reachable.