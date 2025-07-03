# Bejo Backend

![license](https://img.shields.io/badge/license-MIT-blue.svg)

**Bejo Backend** is a **Retrieval-Augmented Generation (RAG)** service built with **FastAPI**, **LangGraph**, **Google Gemini**, and **Qdrant**. It provides a set of APIs to upload documents, store them in a vector database, and answer questions with context-aware responses powered by LLMs.


## 🧭 Table of Contents

1. [📌 Introduction](#introduction)
2. [🛠️ Why These Tools?](#why-these-tools)
3. [✨ Features](#features)
4. [⚙️ Setup](#setup)
5. [🚀 Usage](#usage)
6. [📁 Project Structure](#project-structure)
7. [📝 License](#license)


## 📌 Introduction

Bejo Backend transforms your unstructured documents (PDFs, Word, etc.) into an interactive, queryable knowledge base. Documents are embedded using **Google Gemini embeddings**, stored in **Qdrant**, and queried using a LangGraph-powered RAG pipeline that retrieves relevant context and generates LLM-based answers.

## 🛠️ Why These Tools?

| Tool              | Reason                                                                                |
| ----------------- | ------------------------------------------------------------------------------------- |
| **FastAPI**       | Modern, high-performance web framework with automatic interactive docs (Swagger).     |
| **LangGraph**     | Explicit, debuggable RAG pipelines built as state machines.                           |
| **LangChain**     | Integration layer for LLMs, vector databases, and prompt orchestration.               |
| **Google Gemini** | Powerful, production-ready LLM by Google.                                             |
| **Qdrant**        | Open-source, high-performance vector database for similarity search.                  |
| **Docling**       | Flexible document loader supporting PDFs, Word docs, and more, with metadata support. |


## ✨ Features

* 📄 **Document Ingestion**
  Automatic file parsing, chunking, and metadata enrichment (page, level, filename, etc.).

* 🔍 **Semantic Search with Levels**
  Search across multi-level knowledge categories (e.g., `level_1`, `level_2`, ...).

* 🧠 **Context-Aware QA (RAG)**
  Answers questions by retrieving relevant document chunks and generating answers with Gemini.

* 🔄 **LangGraph Workflow**
  Clear, step-by-step pipeline for document retrieval and response generation.

* 📦 **Dockerized Deployment**
  Easily deploy both the API and vector store using `docker-compose`.

* 🧪 **Interactive API Docs**
  Swagger UI available at `/docs` when the server is running.


## ⚙️ Setup

### 🔧 Prerequisites

* Python `>= 3.11`
* Docker & Docker Compose *(optional but recommended)*

### 🔑 Environment Variables

Create a `.env` file in the project root:

```env
GOOGLE_API_KEY=your_google_genai_key
```

### 🧪 Local Development

```bash
# Set up virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -e .

# Optional: start Qdrant vector DB
docker compose up -d qdrant

# Run FastAPI server
uvicorn app.main:app --reload
```

Then navigate to [http://localhost:8000/docs](http://localhost:8000/docs) to view interactive API documentation.

### 🐳 Docker Compose (Full Stack)

```bash
docker compose up --build
```

> This runs both the API (`localhost:8000`) and Qdrant (`localhost:6335`).


## 🚀 Usage 

### 🔼 `POST /upload?embed=true`

Upload a document and immediately embed it. Requires a `category` (e.g., `level_1`, `level_2`, ...).

Example:

```bash
curl -X POST http://localhost:8000/upload?embed=true \
  -F "file=@yourfile.pdf" \
  -F "category=level_1"
```

### 💬 `POST /chat/{thread_id}`

Ask a question based on context (with optional conversation history). `thread_id` allows multi-turn conversations.

Example payload:

```json
{
  "query": "What is GMP?",
  "history": [
    {"role": "user", "content": "Explain the production procedure."}
  ]
}
```


## 📁 Project Structure

```
app/
 ├─ core/          # Embeddings, LLM setup, vectorstore config, text splitter, memory
 ├─ services/      # RAG orchestration logic using LangGraph
 ├─ api/           # FastAPI routers (upload, chat, healthcheck, etc.)
 └─ main.py        # FastAPI application entrypoint
Dockerfile
docker-compose.yml
.env.example        # Environment variable template
README.md
```

## 📝 License

MIT © 2025 [Danang Hapis Fadillah](mailto:danangpostman37@gmail.com)

> Free to use, modify, and distribute — just include the original license and give credit where it’s due 🙌
