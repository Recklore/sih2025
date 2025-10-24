#!/usr/bin/env python3
"""
main.py - CURAJ Chatbot Pipeline Orchestrator
==============================================

Complete pipeline execution from web scraping to RAG agent deployment.

Stages:
1. Web Scraping      - Crawl university website
2. Text Extraction   - Extract text from documents
3. Classification    - Classify as static/dynamic
4. Database Curation - Populate Weaviate collections
5. Agent Deployment  - Initialize and run RAG agent

Usage:
    # Full pipeline
    python scripts/main.py

    # Skip scraping (use existing data)
    python scripts/main.py --skip-scrape

    # Skip to agent only
    python scripts/main.py --agent-only

    # Batch mode (no interaction)
    python scripts/main.py --batch
"""

import os
import sys
import time
import asyncio
import argparse
from pathlib import Path
from typing import Optional

# Add parent directory for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import pipeline modules
from scrapy.crawler import CrawlerProcess
from scrape_01 import SitemapSpider
from extract_02 import main as extract_main
from classifier_03 import main as classifier_main
from curation_04 import main as curation_main
from agent_05 import create_agent, query_agent, close_connections

# Load environment
from dotenv import load_dotenv

load_dotenv()


# ==================== CONFIGURATION ====================


class PipelineConfig:
    """Pipeline configuration"""

    # Directories
    DATA_DIR = "./data"
    PROCESSED_DIR = "./processed_data"
    CLASSIFIED_DIR = "./classified_data"

    # Files
    SITEMAP_FILE = "./sitemap.xml"
    PAGES_FILE = "./pages.jl"
    CLASSIFIED_JSON = "./classified_data.json"

    # Processing limits
    EXTRACT_LIMIT = None  # None = process all files

    # Colors for terminal output
    RESET = "\033[0m"
    BOLD = "\033[1m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"


# ==================== HELPER FUNCTIONS ====================


def print_header(title: str, char: str = "="):
    """Print formatted header"""
    print(f"\n{PipelineConfig.BOLD}{PipelineConfig.CYAN}")
    print(char * 70)
    print(f"  {title}")
    print(char * 70)
    print(PipelineConfig.RESET)


def print_step(step: int, total: int, title: str):
    """Print step header"""
    print(f"\n{PipelineConfig.BOLD}{PipelineConfig.BLUE}")
    print(f"━━━ STEP {step}/{total}: {title} ━━━")
    print(PipelineConfig.RESET)


def print_success(message: str):
    """Print success message"""
    print(f"{PipelineConfig.GREEN}✓ {message}{PipelineConfig.RESET}")


def print_warning(message: str):
    """Print warning message"""
    print(f"{PipelineConfig.YELLOW}⚠ {message}{PipelineConfig.RESET}")


def print_error(message: str):
    """Print error message"""
    print(f"{PipelineConfig.RED}✗ {message}{PipelineConfig.RESET}")


def print_info(message: str):
    """Print info message"""
    print(f"{PipelineConfig.CYAN}ℹ {message}{PipelineConfig.RESET}")


def check_directory(path: str) -> bool:
    """Check if directory exists and has files"""
    if not os.path.exists(path):
        return False

    # Check if directory has any files
    for root, dirs, files in os.walk(path):
        if files:
            return True
    return False


def get_user_confirmation(message: str, batch_mode: bool = False) -> bool:
    """Get user confirmation (auto-yes in batch mode)"""
    if batch_mode:
        return True

    response = input(f"{message} [y/N]: ").strip().lower()
    return response in ["y", "yes"]


def check_prerequisites() -> bool:
    """Check if required services are running"""
    print_info("Checking prerequisites...")

    # Check Weaviate
    try:
        import weaviate

        client = weaviate.connect_to_local(host="localhost", port=8080)
        client.close()
        print_success("Weaviate is running")
    except Exception as e:
        print_error(f"Weaviate not accessible: {e}")
        print_info("Start Weaviate: cd weaviate && docker-compose up -d")
        return False

    # Check Ollama (optional but recommended)
    try:
        import requests

        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        if response.status_code == 200:
            print_success("Ollama is running")
        else:
            print_warning("Ollama not responding correctly")
    except Exception:
        print_warning("Ollama not running (optional for embeddings)")

    return True


# ==================== PIPELINE STAGES ====================


def stage_1_scraping(skip: bool = False, batch_mode: bool = False) -> bool:
    """
    Stage 1: Web Scraping
    Crawls university website and generates sitemap
    """
    print_step(1, 5, "WEB SCRAPING")

    if skip:
        print_warning("Skipping web scraping (--skip-scrape flag)")

        # Check if data exists
        if os.path.exists(PipelineConfig.SITEMAP_FILE) and os.path.exists(PipelineConfig.PAGES_FILE):
            print_success(f"Using existing data: {PipelineConfig.SITEMAP_FILE}, {PipelineConfig.PAGES_FILE}")
            return True
        else:
            print_error("No existing scraping data found!")
            return False

    # Check if data already exists
    if os.path.exists(PipelineConfig.SITEMAP_FILE):
        print_info(f"Found existing sitemap: {PipelineConfig.SITEMAP_FILE}")
        if not get_user_confirmation("Re-scrape website?", batch_mode):
            print_success("Using existing scraping data")
            return True

    try:
        print_info("Starting web scraper...")
        print_info("This may take several minutes depending on website size")

        # Run Scrapy crawler
        process = CrawlerProcess(
            settings={
                "LOG_LEVEL": "INFO",
                "ROBOTSTXT_OBEY": True,
            }
        )
        process.crawl(SitemapSpider)
        process.start()

        # Verify output
        if os.path.exists(PipelineConfig.SITEMAP_FILE) and os.path.exists(PipelineConfig.PAGES_FILE):
            print_success(f"Scraping completed successfully")
            print_info(f"  → Sitemap: {PipelineConfig.SITEMAP_FILE}")
            print_info(f"  → Pages: {PipelineConfig.PAGES_FILE}")
            return True
        else:
            print_error("Scraping completed but output files not found")
            return False

    except Exception as e:
        print_error(f"Scraping failed: {e}")
        return False


def stage_2_extraction(batch_mode: bool = False) -> bool:
    """
    Stage 2: Text Extraction
    Extracts text from PDFs, DOCX, XLSX, PPTX, HTML
    """
    print_step(2, 5, "TEXT EXTRACTION")

    # Check if data directory exists
    if not check_directory(PipelineConfig.DATA_DIR):
        print_warning(f"Data directory '{PipelineConfig.DATA_DIR}' is empty or missing")
        print_info("Skipping text extraction (no documents to process)")
        return True

    # Check if already processed
    if check_directory(PipelineConfig.PROCESSED_DIR):
        print_info(f"Found existing processed data: {PipelineConfig.PROCESSED_DIR}")
        if not get_user_confirmation("Re-extract text from documents?", batch_mode):
            print_success("Using existing extracted data")
            return True

    try:
        print_info("Starting text extraction...")
        print_info("Supported formats: PDF, DOCX, XLSX, PPTX, HTML")

        # Run extraction
        extract_main(
            input_base_dir=PipelineConfig.DATA_DIR,
            output_base_dir=PipelineConfig.PROCESSED_DIR,
            limit_per_type=PipelineConfig.EXTRACT_LIMIT,
        )

        # Verify output
        if check_directory(PipelineConfig.PROCESSED_DIR):
            print_success("Text extraction completed successfully")
            return True
        else:
            print_error("Extraction completed but no output found")
            return False

    except Exception as e:
        print_error(f"Text extraction failed: {e}")
        return False


def stage_3_classification(batch_mode: bool = False) -> bool:
    """
    Stage 3: Classification
    Classifies documents as static or dynamic using AI
    """
    print_step(3, 5, "DOCUMENT CLASSIFICATION")

    # Check if processed data exists
    if not check_directory(PipelineConfig.PROCESSED_DIR):
        print_error(f"Processed data not found: {PipelineConfig.PROCESSED_DIR}")
        return False

    # Check if already classified
    if check_directory(PipelineConfig.CLASSIFIED_DIR):
        print_info(f"Found existing classified data: {PipelineConfig.CLASSIFIED_DIR}")
        if not get_user_confirmation("Re-classify documents?", batch_mode):
            print_success("Using existing classification")
            return True

    try:
        print_info("Starting document classification...")
        print_info("Using mDeBERTa multilingual model for zero-shot classification")

        # Run classification
        results = classifier_main()

        # Verify output
        if check_directory(PipelineConfig.CLASSIFIED_DIR) and os.path.exists(PipelineConfig.CLASSIFIED_JSON):
            print_success(f"Classification completed successfully")
            print_info(f"  → Results: {PipelineConfig.CLASSIFIED_JSON}")
            print_info(f"  → Organized: {PipelineConfig.CLASSIFIED_DIR}")

            # Print summary
            static_count = sum(1 for r in results if r.get("category") == "static")
            dynamic_count = sum(1 for r in results if r.get("category") == "dynamic")
            print_info(f"  → Static documents: {static_count}")
            print_info(f"  → Dynamic documents: {dynamic_count}")

            return True
        else:
            print_error("Classification completed but output not found")
            return False

    except Exception as e:
        print_error(f"Classification failed: {e}")
        return False


def stage_4_curation(batch_mode: bool = False) -> bool:
    """
    Stage 4: Database Curation
    Creates Weaviate collections and populates with embeddings
    """
    print_step(4, 5, "DATABASE CURATION")

    # Check if classified data exists
    if not check_directory(PipelineConfig.CLASSIFIED_DIR):
        print_error(f"Classified data not found: {PipelineConfig.CLASSIFIED_DIR}")
        return False

    # Check if collections exist
    try:
        import weaviate

        client = weaviate.connect_to_local(host="localhost", port=8080)

        collections_exist = all(client.collections.exists(name) for name in ["static", "dynamic", "sitemap"])
        client.close()

        if collections_exist:
            print_info("Weaviate collections already exist")
            if not get_user_confirmation("Re-create and populate collections?", batch_mode):
                print_success("Using existing collections")
                return True
    except Exception:
        pass

    try:
        print_info("Starting database curation...")
        print_info("Creating Weaviate collections: static, dynamic, sitemap")
        print_info("Embedding with Ollama BGE-M3 model")

        # Run curation
        curation_main()

        print_success("Database curation completed successfully")
        return True

    except Exception as e:
        print_error(f"Database curation failed: {e}")
        return False


async def stage_5_agent(batch_mode: bool = False) -> bool:
    """
    Stage 5: Agent Deployment
    Initializes RAG agent and provides interactive query interface
    """
    print_step(5, 5, "RAG AGENT DEPLOYMENT")

    try:
        print_info("Initializing RAG agent...")
        print_info("Creating ReActAgent with three tools:")
        print_info("  1. StaticInfoTool - Permanent information")
        print_info("  2. DynamicInfoTool - Time-sensitive information")
        print_info("  3. NavDocTool - Sitemap navigation")

        # Create agent
        agent, weaviate_client = create_agent(verbose=False)

        print_success("RAG agent initialized successfully!")
        print("")

        # Interactive query loop
        if not batch_mode:
            print(f"{PipelineConfig.BOLD}{PipelineConfig.GREEN}")
            print("╔" + "═" * 68 + "╗")
            print("║" + " " * 20 + "🤖 AGENT READY - ASK QUESTIONS!" + " " * 19 + "║")
            print("╚" + "═" * 68 + "╝")
            print(PipelineConfig.RESET)
            print_info("Type your questions (or 'quit'/'exit' to stop)")
            print("")

            try:
                while True:
                    # Get user query
                    query = input(f"{PipelineConfig.BOLD}{PipelineConfig.CYAN}You: {PipelineConfig.RESET}").strip()

                    if not query:
                        continue

                    if query.lower() in ["quit", "exit", "q"]:
                        print_info("Shutting down agent...")
                        break

                    # Query agent
                    print(f"{PipelineConfig.BOLD}{PipelineConfig.GREEN}Agent: {PipelineConfig.RESET}", end="")
                    await query_agent(agent, query, print_output=True)
                    print("")

            except KeyboardInterrupt:
                print("\n")
                print_info("Interrupted by user")
        else:
            # Batch mode - run example queries
            print_info("Running example queries (batch mode)...")

            example_queries = [
                "What are the admission deadlines?",
                "Tell me about the faculty of Computer Science",
                "What scholarships are available?",
            ]

            for i, query in enumerate(example_queries, 1):
                print(f"\n{PipelineConfig.BOLD}Example {i}: {query}{PipelineConfig.RESET}")
                await query_agent(agent, query, print_output=True)
                print("")

        # Cleanup
        close_connections(weaviate_client)
        print_success("Agent shutdown complete")
        return True

    except Exception as e:
        print_error(f"Agent deployment failed: {e}")
        return False


# ==================== MAIN PIPELINE ====================


async def run_pipeline(args):
    """Run the complete pipeline"""

    # Print welcome header
    print_header("CURAJ CHATBOT PIPELINE", "═")
    print(
        f"{PipelineConfig.BOLD}Complete RAG Pipeline: Scraping → Extraction → Classification → Curation → Agent{PipelineConfig.RESET}"
    )
    print("")

    # Track timing
    start_time = time.time()

    # Check prerequisites
    if not check_prerequisites():
        print_error("Prerequisites check failed. Please fix issues and try again.")
        return False

    print_success("All prerequisites met!")

    # Determine which stages to run
    if args.agent_only:
        print_warning("Running agent only (--agent-only flag)")
        stages_to_run = [5]
    else:
        stages_to_run = [1, 2, 3, 4, 5]

    # Run stages
    try:
        # Stage 1: Scraping
        if 1 in stages_to_run:
            if not stage_1_scraping(skip=args.skip_scrape, batch_mode=args.batch):
                if not get_user_confirmation("Stage 1 failed. Continue anyway?", args.batch):
                    return False

        # Stage 2: Extraction
        if 2 in stages_to_run:
            if not stage_2_extraction(batch_mode=args.batch):
                if not get_user_confirmation("Stage 2 failed. Continue anyway?", args.batch):
                    return False

        # Stage 3: Classification
        if 3 in stages_to_run:
            if not stage_3_classification(batch_mode=args.batch):
                if not get_user_confirmation("Stage 3 failed. Continue anyway?", args.batch):
                    return False

        # Stage 4: Curation
        if 4 in stages_to_run:
            if not stage_4_curation(batch_mode=args.batch):
                print_error("Stage 4 is critical. Cannot proceed without database.")
                return False

        # Stage 5: Agent
        if 5 in stages_to_run:
            await stage_5_agent(batch_mode=args.batch)

        # Print completion summary
        elapsed_time = time.time() - start_time
        print_header("PIPELINE COMPLETE", "═")
        print_success(f"All stages completed successfully!")
        print_info(f"Total time: {elapsed_time:.2f} seconds ({elapsed_time/60:.2f} minutes)")

        return True

    except KeyboardInterrupt:
        print("\n")
        print_warning("Pipeline interrupted by user")
        return False
    except Exception as e:
        print_error(f"Pipeline failed with error: {e}")
        import traceback

        traceback.print_exc()
        return False


# ==================== CLI ====================


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="CURAJ Chatbot Pipeline - Complete RAG system orchestrator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run full pipeline
  python scripts/main.py
  
  # Skip scraping (use existing data)
  python scripts/main.py --skip-scrape
  
  # Run agent only (database already populated)
  python scripts/main.py --agent-only
  
  # Batch mode (no user interaction)
  python scripts/main.py --batch
  
  # Combine flags
  python scripts/main.py --skip-scrape --batch
        """,
    )

    parser.add_argument("--skip-scrape", action="store_true", help="Skip web scraping stage (use existing data)")

    parser.add_argument("--agent-only", action="store_true", help="Skip all stages except agent deployment")

    parser.add_argument("--batch", action="store_true", help="Batch mode (no user interaction, auto-confirm all)")

    args = parser.parse_args()

    # Run pipeline
    asyncio.run(run_pipeline(args))


if __name__ == "__main__":
    main()
