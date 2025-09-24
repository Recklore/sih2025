import qdrant_client 
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from llama_index.vector_stores.qdrant import QdrantVectorStore 
from dotenv import load_dotenv

from llama_index.llms.google_genai import GoogleGenAI
from llama_index.embeddings.google_genai import GoogleGenAIEmbedding

load_dotenv()

print("Configuring LlamaIndex to use Google Generative AI...")
Settings.llm = GoogleGenAI(model_name="models/gemini-1.5-flash-latest")
Settings.embed_model = GoogleGenAIEmbedding(model_name="models/embedding-001")

# Change the path depending upon the folder where you have stored the scraped data
DATA_DIR = "./data/pdfs/"

print("Loading documents...")
documents = SimpleDirectoryReader(DATA_DIR, recursive=True).load_data()
print(f"Loaded {len(documents)} documents.")

if not documents:
    print("❌ No documents found. Did the scraping script run correctly?")
    exit(1)

print("Connecting to Qdrant...")
client = qdrant_client.QdrantClient(host="localhost", port=6333)
    
index_name = "curaj_website_qdrant"

vector_store = QdrantVectorStore(client=client, collection_name=index_name)

print("Indexing documents with Google models... this may take a while.")
index = VectorStoreIndex.from_documents(
    documents, vector_store=vector_store, show_progress=True
)
print("✅ Indexing complete.")

print("\n--- Testing query engine with Qdrant ---")
query_engine = index.as_query_engine()
response = query_engine.query("Tell me about Training of the Liaison Officers for Scheduled Castes/")
print(response)

client.close()
print("\nQdrant client closed.")