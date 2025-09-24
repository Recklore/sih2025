import os
import pprint
import weaviate
from weaviate.classes.init import Auth

from llama_index.readers.file import PyMuPDFReader
from llama_index.core import Document, VectorStoreIndex, SimpleDirectoryReader, Settings
from llama_index.core.schema import MetadataMode
from llama_index.core.node_parser import HierarchicalNodeParser
from llama_index.vector_stores.weaviate import WeaviateVectorStore
from llama_index.llms.google_genai import GoogleGenAI
from llama_index.embeddings.google_genai import GoogleGenAIEmbedding

from dotenv import load_dotenv


load_dotenv()

# Setting up llm and embedding model
Settings.llm = GoogleGenAI(model="models/gemini-1.5-flash-latest")
Settings.embed_model = GoogleGenAIEmbedding(model_name="text-embedding-004")

print(f"Embedding model set to: {Settings.embed_model.model_name}")
print(f"LLM set to: {Settings.llm.__dict__["model"]}")


# Setting up weaviate client
index_name = "Curaj"
with weaviate.connect_to_weaviate_cloud(
    cluster_url=os.getenv("WEAVIATE_URL"),
    auth_credentials=Auth.api_key(os.getenv("WEAVIATE_API_KEY")),
) as client:

    data_exists = client.collections.exists(index_name)

    if data_exists:
        vector_store = WeaviateVectorStore(weaviate_client=client, index_name=index_name)
        index = VectorStoreIndex.from_vector_store(vector_store=vector_store)
    else:

        # Setting reader and splitter
        reader = SimpleDirectoryReader(
            input_dir="./sorted_data",
            recursive=True,
            # file_extractor={".pdf": PyMuPDFReader()}
        )
        splitter = HierarchicalNodeParser.from_defaults()

        docs = reader.load_data()

        for doc in docs:
            doc.text_template = "Metadata:\n{metadata_str}\n---\nContent:\n{content}"

            doc.excluded_embed_metadata_keys = [key for key in doc.metadata.keys() if key != "file_name"]
            doc.excluded_llm_metadata_keys = [key for key in doc.metadata.keys() if key != "file_name"]

        nodes = splitter.get_nodes_from_documents(docs)
        print(f"Chunked documents into {len(nodes)} nodes.")

        vector_store = WeaviateVectorStore(weaviate_client=client, index_name=index_name)

        index = VectorStoreIndex(
            nodes=nodes,
            vector_store=vector_store,
        )

        print("Successfully created index and stored embeddings in Weaviate.")

    query_engine = index.as_query_engine(similarity_top_k=5)

    print("\n--- Starting Query Engine ---")
    print("Type 'exit' or 'quit' to end the session.")
    while True:
        query_text = input("\nEnter your query: ")
        if query_text.lower() in ["exit", "quit"]:
            print("Exiting query engine. Goodbye!")
            break
        if not query_text.strip():
            print("Query cannot be empty.")
            continue

        response = query_engine.query(query_text)
        # Print the response in a clean format
        print("\n--- Query Response ---")
        pprint.pprint(response.response)

        print("\n--- Source Nodes ---")
        if response.source_nodes:
            for node in response.source_nodes:
                print(f"Source: {node.metadata.get('file_name', 'N/A')}, Score: {node.score:.4f}")
        else:
            print("No source nodes found.")


# print(len(docs))
# pprint.pprint(docs[-1].__dict__)


# print(
#     "The LLM sees this: \n",
#     docs[-1].get_content(metadata_mode=MetadataMode.LLM),
# )
# print(
#     "The Embedding model sees this: \n",
#     docs[-1].get_content(metadata_mode=MetadataMode.EMBED),
# )
