from fastapi import APIRouter, HTTPException, Path as FastAPIPath
from fastapi.responses import JSONResponse
from app.models.request import ChatRequest
from app.models.response import ChatResponse
from app.services import rag_service
from app.services.rag_service import CATEGORY_TO_COLLECTION
from app.core.memory import memory
from langchain_core.messages import HumanMessage
from datetime import datetime

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("/{thread_id}", response_model=ChatResponse)
async def chat(thread_id: str, request: ChatRequest):
    # Validate category
    """
    Chat with the AI.

    Args:
        thread_id: The ID of the conversation thread.
        request: The ChatRequest object, containing the question to ask the AI and the category of the conversation.

    Returns:
        A ChatResponse object, containing the response from the AI and the sources used to generate the response.

    Raises:
        HTTPException: If the category is invalid or if there is an error during the chat.
    """
    if request.category not in CATEGORY_TO_COLLECTION:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid category. Must be one of: {list(CATEGORY_TO_COLLECTION.keys())}",
        )

    try:
        # Create RAG graph for the specific category
        rag_graph = rag_service.create_rag_graph(request.category)

        # Configuration for conversation thread
        config = {"configurable": {"thread_id": thread_id}}

        # Create user message with timestamp
        input_message = {
            "messages": [
                HumanMessage(
                    content=request.question,
                    additional_kwargs={"timestamp": datetime.utcnow().isoformat()},
                )
            ]
        }

        # Run the graph and collect all steps
        messages = []
        sources = []

        for step in rag_graph.stream(
            input_message, config=config, stream_mode="values"
        ):
            messages = step["messages"]

        # Get the final AI response
        final_response = messages[-1]

        # Extract sources from tool messages
        for message in messages:
            # Only process tool messages that contain artifacts (retrieved documents)
            if getattr(message, "type", None) == "tool" and hasattr(message, "artifact"):
                # message.artifact can be None or a list of retrieved documents
                artifacts = message.artifact or []
                for doc in artifacts:
                    # Support both `Document` objects and their dict representations
                    if isinstance(doc, dict):
                        metadata = doc.get("metadata", {})
                    else:
                        metadata = getattr(doc, "metadata", {}) or {}

                    source_info = {
                        "filename": metadata.get("filename", "Unknown"),
                        "document_id": metadata.get("document_id", ""),
                        "file_path": metadata.get("file_path", ""),
                    }
                    if source_info not in sources:
                        sources.append(source_info)

        return ChatResponse(
            answer=final_response.content, thread_id=thread_id, sources=sources
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during chat: {str(e)}")


@router.get("/history/{thread_id}")
async def get_chat_history(thread_id: str = FastAPIPath(..., description="Thread ID")):
    """Get conversation history for a thread"""

    try:
        # Get conversation state from memory
        config = {"configurable": {"thread_id": thread_id}}

        # Try to get the checkpoint for this thread
        checkpoint = memory.get(config)

        if not checkpoint or not checkpoint.get("channel_values", {}).get("messages"):
            return JSONResponse(
                content={
                    "thread_id": thread_id,
                    "messages": [],
                    "message": "No conversation history found",
                },
                status_code=200,
            )

        messages = checkpoint["channel_values"]["messages"]

        # Format messages for response
        formatted_messages = []
        for msg in messages:
            if msg.type in ["human", "ai"]:
                formatted_messages.append(
                    {
                        "type": msg.type,
                        "content": msg.content,
                        "timestamp": getattr(msg, "timestamp", None)
                        or getattr(msg, "additional_kwargs", {}).get("timestamp"),
                    }
                )

        return JSONResponse(
            content={
                "thread_id": thread_id,
                "messages": formatted_messages,
                "total_messages": len(formatted_messages),
            }
        )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error retrieving chat history: {str(e)}"
        )
