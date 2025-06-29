from pydantic import BaseModel
from typing import List, Dict, Any


class ChatResponse(BaseModel):
    answer: str
    thread_id: str
    sources: List[Dict[str, Any]] = []


class UploadResponse(BaseModel):
    message: str
    filename: str
    document_id: str
    chunks_created: int
