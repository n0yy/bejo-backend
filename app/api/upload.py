from fastapi import APIRouter, UploadFile, File, Query, HTTPException
from pathlib import Path
import shutil

from app.services.rag_service import rag_service, CATEGORY_TO_COLLECTION
from app.models.response import UploadResponse

router = APIRouter(prefix="/upload", tags=["Upload"])

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


@router.post("", response_model=UploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    category: str = Query(..., description="Category of the document"),
    embed: bool = Query(True, description="Collection name"),
):
    """
    Uploads a document to the server and optionally embeds it in a collection

    Args:
        file: The file to upload. Must be a PDF, DOCX, PPTX, HTML, or TEXT file.
        category: The category of the document. Must be one of the categories
            supported by the rag service.
        embed: Whether to embed the document in a collection. Defaults to True.

    Returns:
        An UploadResponse object containing information about the uploaded
        document, including the filename, document ID, and number of chunks
        created.

    Raises:
        HTTPException: If the file type is unsupported, the category is invalid,
            or an error occurs while processing the document.
    """
    if category not in CATEGORY_TO_COLLECTION:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid category. Must be one of: {list(CATEGORY_TO_COLLECTION.keys())}",
        )

    allowed_extensions = {
        ".pdf",
        ".docx",
        ".pptx",
        ".html",
        ".txt",
        ".csv",
        ".png",
        ".jpg",
        ".jpeg",
        ".gif",
        "webp",
        "tiff",
    }
    file_extension = Path(file.filename).suffix.lower()
    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Allowed types: {allowed_extensions}",
        )

    try:
        file_path = UPLOAD_DIR / file.filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        if embed:
            chunks_created, document_id = rag_service.process_document(
                str(file_path), file.filename, category
            )

            return UploadResponse(
                message="Document uploaded and embedded successfully",
                filename=file.filename,
                document_id=document_id,
                chunks_created=chunks_created,
            )
        else:
            return UploadResponse(
                message="Document uploaded successfully (not embedded)",
                filename=file.filename,
                document_id="",
                chunks_created=0,
            )

    except Exception as e:
        if file_path.exists():
            file_path.unlink()
        raise HTTPException(
            status_code=500, detail=f"Error processing document: {str(e)}"
        )
