from fastapi import APIRouter, Query, HTTPException, Body
from app.core.vectorstore import qdrant_client
from qdrant_client.http.exceptions import UnexpectedResponse
from pydantic import BaseModel
from typing import Optional
from qdrant_client.models import PointIdsList


class PointPayload(BaseModel):
    page_content: Optional[str]
    file_path: Optional[str]
    uploaded_at: Optional[str]


class PointOut(BaseModel):
    id: str
    payload: PointPayload


router = APIRouter(prefix="/vectorstore", tags=["VectorStore"])


@router.get("/bejo-knowledge-level-{level}", response_model=list[PointOut])
async def get_knowledge(level: str):
    try:
        collection_name = f"bejo_knowledge_level_{level}"
        try:
            qdrant_client.get_collection(collection_name)
        except UnexpectedResponse as e:
            if e.status_code == 404:
                raise HTTPException(
                    status_code=404,
                    detail=f"Collection {collection_name} does not exist.",
                )
            raise

        points, _ = qdrant_client.scroll(
            collection_name=collection_name,
            limit=1000,
            with_payload=True,
            with_vectors=False,
        )

        results = []
        for point in points:
            payload = point.payload or {}
            results.append(
                PointOut(
                    id=point.id,
                    payload=PointPayload(
                        page_content=payload.get("page_content"),
                        file_path=payload.get("metadata", {}).get("file_path", ""),
                        uploaded_at=payload.get("metadata", {}).get("upload_date", ""),
                    ),
                )
            )

        return results

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while fetching the vector store: {str(e)}",
        )


@router.delete("/bejo-knowledge-level-{level}")
async def delete_knowledge(
    level: str, id: str = Query(..., description="ID of the document to delete")
):
    try:
        collection_name = f"bejo_knowledge_level_{level}"
        try:
            qdrant_client.get_collection(collection_name)
        except UnexpectedResponse as e:
            if e.status_code == 404:
                raise HTTPException(
                    status_code=404,
                    detail=f"Collection {collection_name} does not exist.",
                )
            raise

        qdrant_client.delete(
            collection_name=collection_name,
            points_selector=PointIdsList(points=[id]),
        )

        return {"detail": f"Document with ID {id} deleted from {collection_name}"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while deleting the document: {str(e)}",
        )


@router.put("/bejo-knowledge-level-{level}")
async def update_knowledge(
    level: str,
    id: str = Query(..., description="ID of the document to update"),
    payload: PointPayload = Body(...),
):
    try:
        collection_name = f"bejo_knowledge_level_{level}"

        try:
            qdrant_client.get_collection(collection_name)
        except UnexpectedResponse as e:
            if e.status_code == 404:
                raise HTTPException(
                    status_code=404,
                    detail=f"Collection {collection_name} does not exist.",
                )
            raise

        new_payload = {
            "page_content": payload.page_content,
        }

        qdrant_client.set_payload(
            collection_name=collection_name,
            payload=new_payload,
            points=[id],
        )

        return {"detail": f"Document with ID {id} updated in {collection_name}"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while updating the document: {str(e)}",
        )
