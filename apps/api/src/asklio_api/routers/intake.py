from typing import Any, cast

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel

from asklio_api.intake import CommodityGroupNotFoundException, IntakeApi
from asklio_api.models.commodity_group import CommodityGroupInfo
from asklio_api.models.procurement import ProcurementRequestCreate
from asklio_api.repository import ProcurementRequestStatus

router = APIRouter(prefix="/intake", tags=["intake"])


def get_intake(request: Request) -> IntakeApi:
    """Get intake API from request state."""
    return cast(IntakeApi, request.state.intake)


@router.get("/commodity_groups", status_code=status.HTTP_200_OK)
async def get_commodity_groups(
    intake: IntakeApi = Depends(get_intake),
) -> list[CommodityGroupInfo]:
    """
    Get all available commodity groups.
    """
    return list(intake.get_commodity_groups())


@router.post("/request", status_code=status.HTTP_201_CREATED)
async def create_procurement_request(
    request: ProcurementRequestCreate, intake: IntakeApi = Depends(get_intake)
) -> dict[str, str]:
    """
    Create a new procurement request.
    """
    # Validate commodity_group
    try:
        return intake.create_procurement_request(request)
    except CommodityGroupNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid commodity_group: '{request.commodity_group}'. Must be one of the valid commodity group names.",
        )


@router.get("/requests", status_code=status.HTTP_200_OK)
async def get_all_requests(intake: IntakeApi = Depends(get_intake)) -> list[dict]:
    """
    Get all procurement requests.
    """
    requests = intake.get_all_requests()
    return [req.to_dict() for req in requests]


@router.get("/requests/{request_id}", status_code=status.HTTP_200_OK)
async def get_request_by_id(
    request_id: str, intake: IntakeApi = Depends(get_intake)
) -> dict:
    """
    Get a single procurement request by ID.
    """
    request = intake.get_request_by_id(request_id)
    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Procurement request with ID '{request_id}' not found.",
        )
    return request.to_dict()


class StatusUpdate(BaseModel):
    """Request body for updating request status."""

    status: ProcurementRequestStatus


@router.patch("/requests/{request_id}/status", status_code=status.HTTP_200_OK)
async def update_request_status(
    request_id: str,
    status_update: StatusUpdate,
    intake: IntakeApi = Depends(get_intake),
) -> dict:
    """
    Update the status of a procurement request.
    """
    updated_request = intake.update_request_status(request_id, status_update.status)
    if not updated_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Procurement request with ID '{request_id}' not found.",
        )
    return updated_request.to_dict()
