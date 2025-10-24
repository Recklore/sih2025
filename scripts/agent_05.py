"""
Reusable Agent Module for CURAJ Chatbot
=======================================
This module provides a ReActAgent configured with three tools:
- StaticInfoTool: Evergreen info (policies, FAQs, contact details)
- DynamicInfoTool: Time-sensitive info (events, deadlines, scholarships)
- NavDocTool: Sitemap navigation and page content

Usage:
    from scripts.agent import create_agent, query_agent

    agent = create_agent()
    response = await query_agent(agent, "What are admission deadlines?")
"""

import os
import asyncio
import weaviate
from dotenv import load_dotenv
from llama_index.core import VectorStoreIndex, Settings, Response
from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.core.agent import ReActAgent
from llama_index.llms.sarvam import Sarvam
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.vector_stores.weaviate import WeaviateVectorStore


# --- Connection Management ---
def get_weaviate_client(host: str = "localhost", port: int = 8080, api_key: str = None):
    """
    Get a Weaviate client connection.

    Args:
        host: Weaviate host address
        port: Weaviate port number
        api_key: Optional API key for authentication

    Returns:
        weaviate.Client: Connected Weaviate client

    Raises:
        Exception: If connection fails
    """
    try:
        auth_config = weaviate.auth.AuthApiKey(api_key=api_key) if api_key else None
        client = weaviate.connect_to_local(host=host, port=port, auth_credentials=auth_config)
        print(f"✓ Connected to Weaviate at {host}:{port}")
        return client
    except Exception as e:
        print(f"✗ Failed to connect to Weaviate: {e}")
        raise


def close_connections(weaviate_client):
    """
    Close Weaviate client connection.

    Args:
        weaviate_client: Weaviate client to close
    """
    try:
        if weaviate_client:
            weaviate_client.close()
            print("✓ Weaviate connection closed")
    except Exception as e:
        print(f"✗ Error closing Weaviate connection: {e}")


# --- Helper Function to Create Index from Weaviate Class ---
def index_from_weaviate(weaviate_client, class_name: str) -> VectorStoreIndex:
    """
    Creates a LlamaIndex VectorStoreIndex from a Weaviate collection.

    Args:
        weaviate_client: Connected Weaviate client
        class_name: Name of Weaviate collection (e.g., 'static', 'dynamic', 'sitemap')

    Returns:
        VectorStoreIndex: LlamaIndex index for querying
    """
    vector_store = WeaviateVectorStore(weaviate_client=weaviate_client, index_name=class_name)
    return VectorStoreIndex.from_vector_store(vector_store=vector_store)


# --- Agent Creation Factory ---
def create_agent(
    weaviate_host: str = "localhost",
    weaviate_port: int = 8080,
    weaviate_api_key: str = None,
    sarvam_api_key: str = None,
    sarvam_model: str = "sarvam-m",
    sarvam_temperature: float = 0.2,
    sarvam_max_tokens: int = 1024,
    ollama_url: str = None,
    ollama_model: str = "bge-m3",
    verbose: bool = True,
) -> tuple[ReActAgent, weaviate.Client]:
    """
    Create a configured ReActAgent with three query tools.

    Args:
        weaviate_host: Weaviate server host
        weaviate_port: Weaviate server port
        weaviate_api_key: Optional API key for Weaviate
        sarvam_api_key: Sarvam AI API key (loads from .env if None)
        sarvam_model: Sarvam LLM model name
        sarvam_temperature: LLM temperature setting
        sarvam_max_tokens: LLM max tokens
        ollama_url: Ollama base URL (loads from .env if None)
        ollama_model: Ollama embedding model name
        verbose: Enable verbose agent output

    Returns:
        tuple: (ReActAgent, weaviate.Client)

    Raises:
        Exception: If Weaviate collections don't exist or connection fails
    """
    # Load environment variables
    load_dotenv()

    # Get API keys from args or environment
    if sarvam_api_key is None:
        sarvam_api_key = os.getenv("SARVAM_API_KEY")
    if ollama_url is None:
        ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
    if weaviate_api_key is None:
        weaviate_api_key = os.getenv("WEAVIATE_API_KEY")

    # Configure LlamaIndex Settings
    Settings.llm = Sarvam(
        api_key=sarvam_api_key, model=sarvam_model, temperature=sarvam_temperature, max_tokens=sarvam_max_tokens
    )
    Settings.embed_model = OllamaEmbedding(model_name=ollama_model, base_url=ollama_url)

    # Connect to Weaviate
    weaviate_client = get_weaviate_client(host=weaviate_host, port=weaviate_port, api_key=weaviate_api_key)

    # Create indexes from Weaviate collections
    try:
        static_index = index_from_weaviate(weaviate_client, "static")
        dynamic_index = index_from_weaviate(weaviate_client, "dynamic")
        sitemap_index = index_from_weaviate(weaviate_client, "sitemap")

        static_qe = static_index.as_query_engine(response_mode="compact")
        dynamic_qe = dynamic_index.as_query_engine(response_mode="compact")
        sitemap_qe = sitemap_index.as_query_engine(response_mode="compact")

        print("✓ Query engines created from Weaviate collections")
    except Exception as e:
        weaviate_client.close()
        raise Exception(
            f"Failed to create query engines. Ensure 'static', 'dynamic', and 'sitemap' "
            f"collections exist in Weaviate. Error: {e}"
        )

    # Define tools
    static_tool = QueryEngineTool(
        query_engine=static_qe,
        metadata=ToolMetadata(
            name="StaticInfoTool",
            description=(
                "Useful for fetching evergreen information and FAQs from the institute. "
                "This includes policies, contact details, and answers to frequently asked questions."
            ),
        ),
    )

    dynamic_tool = QueryEngineTool(
        query_engine=dynamic_qe,
        metadata=ToolMetadata(
            name="DynamicInfoTool",
            description=(
                "Useful for fetching time-sensitive information. "
                "This includes events, admission dates, application deadlines, and available scholarships. "
                "Also useful for calendar-related queries."
            ),
        ),
    )

    navdoc_tool = QueryEngineTool(
        query_engine=sitemap_qe,
        metadata=ToolMetadata(
            name="NavDocTool",
            description=(
                "Useful for navigating the site map and fetching page fragments or documents for grounding. "
                "This can return URLs and content excerpts from specific pages."
            ),
        ),
    )

    # Create agent
    agent = ReActAgent(
        tools=[static_tool, dynamic_tool, navdoc_tool],
        verbose=verbose,
    )

    print("✓ ReActAgent created with 3 tools")

    return agent, weaviate_client


# --- Query Helper Function ---
async def query_agent(
    agent: ReActAgent, question: str, print_response: bool = True, print_sources: bool = True
) -> Response:
    """
    Query the agent asynchronously and optionally print formatted output.

    Args:
        agent: ReActAgent instance
        question: User question to ask
        print_response: Whether to print the response
        print_sources: Whether to print source information

    Returns:
        Response: Agent's response object with answer and sources
    """
    if print_response:
        print(f"\n{'='*60}")
        print(f"QUESTION: {question}")
        print(f"{'='*60}\n")

    # Get response from agent
    response = await agent.arun(question)

    if print_response:
        print("\n=== ANSWER ===")
        print(str(response))

    if print_sources:
        try:
            print("\n=== SOURCES ===")
            if response.sources:
                for source in response.sources:
                    raw_output = source.raw_output
                    if isinstance(raw_output, Response) and raw_output.source_nodes:
                        print(f"Tool Used: {source.tool_name}")
                        for node in raw_output.source_nodes:
                            file_name = node.metadata.get("file_name", "N/A")
                            category = node.metadata.get("category", "N/A")
                            source_type = node.metadata.get("source_type", "N/A")
                            print(f"  - {file_name} [{category}/{source_type}] (Score: {node.score:.2f})")
                    else:
                        print(f"- Tool '{source.tool_name}' was called, but returned no source nodes.")
            else:
                print("No tools were called to generate this response.")
        except Exception as e:
            print(f"Error printing sources: {e}")

    return response


# --- Example Usage ---
async def main():
    """
    Example usage demonstrating the agent module.
    Shows how to create an agent, query it, and cleanup connections.
    """
    # Create agent with default settings
    agent, weaviate_client = create_agent(verbose=True)

    try:
        # Example queries
        await query_agent(agent, "What are the admission deadlines for the upcoming semester?")

        await query_agent(agent, "Where can I find the student conduct policy?")

    finally:
        # Always close connections when done
        close_connections(weaviate_client)


# --- Script Entry Point ---
if __name__ == "__main__":
    asyncio.run(main())
