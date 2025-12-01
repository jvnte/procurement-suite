from typing import cast

from fastapi import APIRouter, Depends, File, Request, UploadFile, status

from agent_api.agent import AgentApi
from agent_api.models.procurement import ProcurementRequestCreate

router = APIRouter(prefix="/agent", tags=["agent"])


def get_intake(request: Request) -> AgentApi:
    """Get intake Agent from request state."""
    return cast(AgentApi, request.state.intake_agent)


@router.post("/intake", status_code=status.HTTP_200_OK)
async def intake_document(
    file: UploadFile = File(...), intake_agent: AgentApi = Depends(get_intake)
) -> ProcurementRequestCreate:
    """
    Accept a PDF file upload and convert it to binary.

    Args:
        file: The uploaded PDF file

    Returns:
        Dictionary containing file metadata and size
    """
    contents = await file.read()

    agent_result = await intake_agent.complete(contents)

    return agent_result.output
    # return ProcurementRequestCreate(
    #     requestor_name="John Doe",
    #     title="Office Supplies and IT Equipment",
    #     vendor_name="Global Tech Solutions GmbH",
    #     vat_id="DE123456789",
    #     commodity_group="IT Services",
    #     order_lines=[
    #         OrderLine(
    #             position_description="Dell Latitude Laptop 15 inch",
    #             unit_price=899.99,
    #             amount=5,
    #             unit="pieces",
    #             total_price=4499.95,
    #         ),
    #         OrderLine(
    #             position_description="Microsoft Office 365 Business License",
    #             unit_price=12.50,
    #             amount=10,
    #             unit="licenses",
    #             total_price=125.00,
    #         ),
    #         OrderLine(
    #             position_description="Ergonomic Office Chair",
    #             unit_price=250.00,
    #             amount=3,
    #             unit="pieces",
    #             total_price=750.00,
    #         ),
    #     ],
    #     total_cost=5374.95,
    #     department="IT Department",
    # )
