from typing import Any, cast

from fastapi import APIRouter, Depends, HTTPException, Request, status

from asklio_api.intake import CommodityGroupNotFoundException, IntakeApi
from asklio_api.models.commodity_group import CommodityGroupInfo
from asklio_api.models.procurement import ProcurementRequestCreate

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


@router.post("/procurement_request", status_code=status.HTTP_201_CREATED)
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
