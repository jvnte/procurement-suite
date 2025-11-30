from typing import cast

from fastapi import APIRouter, Depends, File, Request, UploadFile, status

from agent_api.agent import IntakeAgent
from agent_api.models.procurement import ProcurementRequestCreate

router = APIRouter(prefix="/agent", tags=["agent"])


def get_intake(request: Request) -> IntakeAgent:
    """Get intake Agent from request state."""
    return cast(IntakeAgent, request.state.intake_agent)


@router.post("/intake", status_code=status.HTTP_200_OK)
async def intake_document(
    file: UploadFile = File(...), intake_agent: IntakeAgent = Depends(get_intake)
) -> ProcurementRequestCreate:
    """
    Accept a PDF file upload and convert it to binary.

    Args:
        file: The uploaded PDF file

    Returns:
        Dictionary containing file metadata and size
    """
    # Read the file contents as binary
    contents = await file.read()
    agent_result = await intake_agent.complete(contents)

    return agent_result.output
