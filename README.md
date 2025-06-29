# Bejo Backend

![license](https://img.shields.io/badge/license-MIT-blue.svg)

Bejo Backend is a Retrieval-Augmented Generation (RAG) service built with FastAPI, LangGraph, Gemini, and Qdrant. It provides an API for uploading documents, storing them in a vector store, and answering questions with context-aware responses.

## Table of Contents
1. [Introduction](#introduction)
2. [Why These Tools?](#why-these-tools)
3. [Features](#features)
4. [Setup](#setup)
5. [Usage](#usage)
6. [Project Structure](#project-structure)
7. [License](#license)

## Introduction
Bejo Backend turns your unstructured documents into an interactive knowledge base. It indexes documents in Qdrant, embeds them with Gemini embeddings, and responds to user queries by combining relevant snippets with the power of Google Gemini LLMs.

## Why These Tools?
- **FastAPI** – modern, fast web framework with automatic interactive docs.
- **LangGraph** – state-machine abstraction on top of LangChain that makes multi-step RAG pipelines explicit and debuggable.
- **LangChain** – glue between LLMs, vector stores, and prompt orchestration.
- **Google Gemini (langchain-google-genai)** – powerful, production-ready LLM provider.
- **Qdrant** – open-source, high-performance vector database for similarity search.
- **Docling** – robust loader for PDFs, Word docs, and more.

## Features
- 📄 **Document ingestion** with automatic splitting and metadata enrichment.
- 🔍 **Semantic search** over multiple knowledge levels (level_1 – level_4).
- 🧠 **Retrieval-Augmented Generation** giving cited answers powered by Gemini.
- 🔄 **LangGraph workflow** that separates retrieval and generation steps.
- 🐳 **Dockerized deployment** + `docker-compose` with Qdrant included.
- 📑 **OpenAPI docs** available at `/docs` once the server is running.

## Setup
### Prerequisites
- Python ≥ 3.11
- Docker & Docker Compose (optional but recommended)

### Environment Variables
Create a `.env` in the project root:
```env
GOOGLE_API_KEY=your_google_genai_key
```

### Local Development
```bash
# install dependencies
python -m venv .venv && source .venv/bin/activate
pip install -e .

# start Qdrant (optional: use docker compose)
docker compose up -d qdrant

# run the API
uvicorn app.main:app --reload
```
Navigate to `http://localhost:8000/docs` for interactive Swagger docs.

### Docker Compose
```bash
docker compose up --build
```
This launches both the API (`localhost:8000`) and Qdrant (`localhost:6333`).

## Usage
1. `POST /upload` – upload a document with a `category` (level_1-level_4).
2. `POST /chat` – ask a question; the service retrieves relevant chunks and generates an answer citing sources.

Check the Swagger UI for detailed schemas and examples.

## Project Structure
```
app/
 ├─ core/          # embeddings, llm, vectorstore, splitter, memory
 ├─ services/      # RAGService orchestrating ingestion & RAG graph
 ├─ api/           # FastAPI routers (upload, chat, health, …)
 └─ main.py        # FastAPI application factory
Dockerfile
docker-compose.yml
```

## License
MIT © 2025 Danang Hapis Fadillah
