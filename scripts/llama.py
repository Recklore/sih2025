import os
import weaviate
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from llama_index.vector_stores.weaviate import WeaviateVectorStore
from dotenv import load_dotenv

# --- [CHANGED] Import the new, recommended classes ---
from llama_index.llms.google_genai import GoogleGenAI
from llama_index.embeddings.google_genai import GoogleGenAIEmbedding

load_dotenv()
# Ensure your GOOGLE_API_KEY is in a .env file or set as an environment variable
# The new classes automatically pick it up from the environment.

# --- [CHANGED] Configure LlamaIndex with the new classes ---
print("Configuring LlamaIndex to use Google Generative AI...")
Settings.llm = GoogleGenAI(model_name="models/gemini-1.5-flash-latest")
Settings.embed_model = GoogleGenAIEmbedding(model_name="models/embedding-001")

DATA_DIR = "./data/pdfs/"

print("Loading documents...")
documents = SimpleDirectoryReader(DATA_DIR, recursive=True).load_data()
print(f"Loaded {len(documents)} documents.")

if not documents:
    print("❌ No documents found. Did the scraping script run correctly?")
    exit(1)

print("Connecting to Weaviate...")
try:
    # --- [CHANGED] This is the new Weaviate v4 connection method ---
    # It's simpler and connects to the default local Docker instance.
    client = weaviate.connect_to_local()
except Exception as e:
    print(f"❌ Could not connect to Weaviate. Is it running? Error: {e}")
    exit(1)
    
index_name = "CurajWebsiteGenai" # Updated index name for clarity
# The logic for checking and deleting an index is slightly different in v4
if client.collections.exists(index_name):
    print(f"Deleting existing collection: {index_name}")
    client.collections.delete(index_name)

vector_store = WeaviateVectorStore(weaviate_client=client, index_name=index_name)

print("Indexing documents with Google models... this may take a while.")
index = VectorStoreIndex.from_documents(
    documents, vector_store=vector_store, show_progress=True
)
print("✅ Indexing complete.")

print("\n--- Testing query engine with Gemini ---")
query_engine = index.as_query_engine()
response = query_engine.query("Tell me about Training of the Liaison Officers for Scheduled Castes/")
print(response)

# --- [CHANGED] Good practice to close the client connection ---
client.close()
print("\nWeaviate client closed.")