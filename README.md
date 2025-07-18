# 🤖 BEJO Backend - RAG Service

Backend for a Retrieval-Augmented Generation (RAG) service built with FastAPI, LangGraph, Ollama, and Qdrant for an intelligent knowledge base system.

## 🚀 Key Features

- **Multi-level Knowledge Base**: Supports 4 levels of knowledge categorization
- **Chat with Memory**: Thread-based conversations with memory
- **Document Upload**: Supports PDF, DOCX, PPTX, HTML, TXT, CSV, and image files
- **Vector Search**: Semantic search powered by Qdrant
- **Health Check**: System health monitoring
- **RESTful API**: Complete and user-friendly endpoints

## 🛠️ Tech Stack

- **FastAPI**: Modern Python web framework
- **LangChain/LangGraph**: LLM and RAG workflow orchestration
- **Ollama**: Local LLM inference
- **Qdrant**: Vector database for similarity search
- **Docker**: Containerization and deployment
- **UV**: Fast Python package manager

## 📋 Requirements

- Docker & Docker Compose
- Python 3.11+ (for development)
- Running Ollama server
- Running Qdrant server

## 🔧 Setup and Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd bejo-backend
```

### 2. Configure Environment

Create a `.env` file based on `.env.example`:

```env
QDRANT_HOST=localhost
QDRANT_PORT=6333
OLLAMA_URL=http://localhost:11434
OLLAMA_EMBEDDING_MODEL=nomic-embed-text
OLLAMA_LLM_MODEL=qwen2.5:7b
```

### 3. Run with Docker

#### CPU Mode:

```bash
docker-compose --profile cpu up -d --build
```

#### GPU Mode (if available):

```bash
docker-compose --profile gpu up -d --build
```

### 4. Verify Installation

```bash
# Check container status
docker-compose ps

# Test health check
curl http://localhost:8000/health
```

## 📚 API Endpoints

### 🏥 Health Check

```http
GET /health
```

Check the health of the system (Qdrant, Ollama embeddings).

**Response:**

```json
{
  "status": "healthy",
  "qdrant": "connected",
  "ollama_embeddings": "working",
  "embedding_size": 768
}
```

### 📄 Upload Document

```http
POST /upload?category={1-4}&embed=true
Content-Type: multipart/form-data

file: <file>
```

**Parameters:**

- `category`: Knowledge category level (1, 2, 3, or 4)
- `embed`: Whether the document should be embedded (default: true)

**Supported File Types:**

- 📄 PDF, DOCX, PPTX
- 🌐 HTML, TXT, CSV
- 🖼️ PNG, JPG, JPEG, GIF, WebP, TIFF

**Response:**

```json
{
  "message": "Document uploaded and embedded successfully",
  "filename": "document.pdf",
  "document_id": "uuid-string",
  "chunks_created": 15
}
```

### 💬 Chat

```http
POST /chat/{thread_id}
Content-Type: application/json

{
  "question": "Your question",
  "category": "1"
}
```

**Response:**

```json
{
  "answer": "AI's answer with emoji 🎉",
  "thread_id": "thread-123",
  "sources": [
    {
      "filename": "document.pdf",
      "document_id": "uuid-string",
      "file_path": "/path/to/file"
    }
  ]
}
```

### 📋 Chat History

```http
GET /chat/history/{thread_id}
```

**Response:**

```json
{
  "thread_id": "thread-123",
  "messages": [
    {
      "type": "user",
      "content": "User's question",
      "timestamp": "2024-01-01T00:00:00Z"
    },
    {
      "type": "assistant",
      "content": "AI's answer",
      "timestamp": "2024-01-01T00:00:01Z"
    }
  ],
  "total_messages": 2
}
```

### 🗂️ Vector Store Management

#### View All Data

```http
GET /vectorstore/bejo-knowledge-level-{1-4}
```

#### Delete Data

```http
DELETE /vectorstore/bejo-knowledge-level-{1-4}?id={point_id}
```

#### Update Data

```http
PUT /vectorstore/bejo-knowledge-level-{1-4}?id={point_id}
Content-Type: application/json

{
  "page_content": "Updated content",
  "file_path": "/path/to/file",
  "uploaded_at": "2024-01-01T00:00:00Z"
}
```
## 🧠 How RAG Works

1. **📄 Document Processing**: Documents are processed using Docling for text extraction
2. **✂️ Text Splitting**: Text is split into chunks using `MarkdownHeaderTextSplitter`
3. **🌤️ Embedding**: Each chunk is converted into vectors using Ollama embeddings
4. **🗂️ Storage**: Vectors are stored in Qdrant under the appropriate category
5. **🔍 Retrieval**: On user query, relevant chunks are retrieved
6. **🤖 Generation**: LLM generates an answer based on the retrieved context

## 🐳 Docker Commands

```bash
# Build and start
docker-compose --profile cpu up -d --build

# Stop services
docker-compose down

# Restart services
docker-compose restart

# View logs
docker-compose logs -f bejo-backend

# Rebuild without cache
docker-compose build --no-cache

# Cleanup (⚠️ caution!)
docker system prune -af --volumes
```

## 📁 Project Structure

```
bejo-backend/
├── app/
│   ├── api/           # API endpoints
│   ├── core/          # Core components (LLM, embeddings, etc.)
│   ├── models/        # Pydantic models
│   └── services/      # Business logic
├── uploads/           # Directory for uploaded files
├── Dockerfile         # Container configuration
├── docker-compose.yml # Multi-container setup
└── pyproject.toml     # Dependencies
```

## 🔧 Development

### Local Development Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Run development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Environment Variables

```env
# Qdrant Configuration
QDRANT_HOST=localhost
QDRANT_PORT=6333

# Ollama Configuration
OLLAMA_URL=http://localhost:11434
OLLAMA_EMBEDDING_MODEL=nomic-embed-text
OLLAMA_LLM_MODEL=qwen2.5:7b
```

## 📊 Monitoring and Troubleshooting

### Health Check

```bash
curl http://localhost:8000/health
```

### Log Monitoring

```bash
# Realtime logs
docker-compose logs -f bejo-backend

# Specific container logs
docker logs <container_id>
```

### Debug Container

```bash
# Enter container
docker exec -it bejo-backend bash

# Check processes
docker exec -it bejo-backend ps aux
```
