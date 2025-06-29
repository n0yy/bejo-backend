from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.core.embeddings import embeddings
from app.core.vectorstore import qdrant_client

router = APIRouter(prefix="/health")


@router.get("")
async def health_check():
    """Health check endpoint"""
    try:
        # Check Qdrant connection
        qdrant_client.get_collections()

        # Check if Ollama is responding (basic check)
        test_embedding = embeddings.embed_query("test")

        return JSONResponse(
            content={
                "status": "healthy",
                "qdrant": "connected",
                "ollama_embeddings": "working",
                "embedding_size": len(test_embedding) if test_embedding else 0,
            }
        )
    except Exception as e:
        return JSONResponse(
            content={"status": "unhealthy", "error": str(e)}, status_code=503
        )
