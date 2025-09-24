# Website RAG Chatbot for SIH 2025

This repository contains the code for a **multilingual Retrieval-Augmented Generation (RAG) chatbot** built for the **Smart India Hackathon (SIH) 2025**.  

The project **scrapes website data**, processes it, and uses it as a **knowledge base** for a chatbot.  
It leverages **powerful AI models** to understand and respond to user queries in **multiple languages** based on the scraped content.

## Core Technologies

- **Language Model (LLM):** Google Gemini 1.5 Flash (`gemini-1.5-flash-latest`)  
- **Embedding Model:** Google `embedding-001`  
- **Vector Database:** Qdrant  
- **Framework:** LlamaIndex  

## How to setup locally

Follow these steps to set up and run the project locally.

### ✅ Prerequisites
- Python **3.10+**
- **Docker** and **Docker Compose**
- An active **Google AI Studio API Key**


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

### 4. Configure Your API Key

You need to provide your Google API Key. Create a file named .env in the root of the project folder.
Now, open the .env file and add your key like this:
```
# File: .env
GOOGLE_API_KEY="your-google-api-key-goes-here"
```

### 5. Start the Qdrant Database

The project uses Docker to run a Qdrant vector database instance. Make sure Docker Desktop is running on your machine, then run the following command from your project's root directory:

```bash
docker-compose up -d
```

This will start the Qdrant container in the background.

### 6. Run the Application

The main script will handle everything from loading your data to indexing it and running a test query.


Then, run the main script:

```bash
python scrape.py
python llama.py
```

The script will:

- Load the documents from the data folder.

- Connect to the Qdrant database.

- Create embeddings for the documents using the Google model.

- Store the embeddings in Qdrant.

- Run a test query and print the result.

You can now modify the query at the end of llama.py to ask your own questions!