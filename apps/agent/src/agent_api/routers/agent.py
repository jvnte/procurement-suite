from fastapi import APIRouter, File, UploadFile, status

router = APIRouter(prefix="/agent", tags=["agent"])


@router.post("/intake", status_code=status.HTTP_200_OK)
async def intake_document(file: UploadFile = File(...)) -> dict[str, str | int]:
    """
    Accept a PDF file upload and convert it to binary.

    Args:
        file: The uploaded PDF file

    Returns:
        Dictionary containing file metadata and size
    """
    # Read the file contents as binary
    contents = await file.read()

    # TODO: Add logic to process the PDF and extract information

    return {
        "filename": file.filename or "unknown",
        "content_type": file.content_type or "application/pdf",
        "size": len(contents),
        "message": "File received and converted to binary successfully"
    }
