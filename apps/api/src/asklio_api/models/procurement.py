from pydantic import BaseModel, Field
from typing import List


class OrderLine(BaseModel):
    """Represents a single order line in a procurement request."""

    position_description: str = Field(..., description="Description of the item/service")
    unit_price: float = Field(..., gt=0, description="Price per unit/item/service")
    amount: int = Field(..., gt=0, description="The quantity or number of units being ordered")
    unit: str = Field(..., description="The unit of measure (e.g., licenses, pieces, hours)")
    total_price: float = Field(..., gt=0, description="Total price for this line (Unit Price x Amount)")


class ProcurementRequestCreate(BaseModel):
    """Request payload for creating a new procurement request."""

    requestor_name: str = Field(..., min_length=1, description="Full name of the person submitting the request")
    title: str = Field(..., min_length=1, description="Brief name or description of the product/service requested")
    vendor_name: str = Field(..., min_length=1, description="Name of the company or individual providing the items/services")
    vat_id: str = Field(..., min_length=1, description="VAT identification number of the vendor")
    commodity_group: str = Field(..., min_length=1, description="The category or group the requested items/services belong to")
    order_lines: List[OrderLine] = Field(..., min_length=1, description="List of order line items")
    total_cost: float = Field(..., gt=0, description="Estimated total cost of the request")
    department: str = Field(..., min_length=1, description="The department of the requestor")
