from enum import Enum
from typing import List

from pydantic import BaseModel, Field


class CommodityGroup(str, Enum):
    """Enum for valid commodity groups."""

    ACCOMMODATION_RENTALS = "Accommodation Rentals"
    MEMBERSHIP_FEES = "Membership Fees"
    WORKPLACE_SAFETY = "Workplace Safety"
    CONSULTING = "Consulting"
    FINANCIAL_SERVICES = "Financial Services"
    FLEET_MANAGEMENT = "Fleet Management"
    RECRUITMENT_SERVICES = "Recruitment Services"
    PROFESSIONAL_DEVELOPMENT = "Professional Development"
    MISCELLANEOUS_SERVICES = "Miscellaneous Services"
    INSURANCE = "Insurance"
    ELECTRICAL_ENGINEERING = "Electrical Engineering"
    FACILITY_MANAGEMENT_SERVICES = "Facility Management Services"
    SECURITY = "Security"
    RENOVATIONS = "Renovations"
    OFFICE_EQUIPMENT = "Office Equipment"
    ENERGY_MANAGEMENT = "Energy Management"
    MAINTENANCE = "Maintenance"
    CAFETERIA_AND_KITCHENETTES = "Cafeteria and Kitchenettes"
    CLEANING = "Cleaning"
    AUDIO_AND_VISUAL_PRODUCTION = "Audio and Visual Production"
    BOOKS_VIDEOS_CDS = "Books/Videos/CDs"
    PRINTING_COSTS = "Printing Costs"
    SOFTWARE_DEVELOPMENT_FOR_PUBLISHING = "Software Development for Publishing"
    MATERIAL_COSTS = "Material Costs"
    SHIPPING_FOR_PRODUCTION = "Shipping for Production"
    DIGITAL_PRODUCT_DEVELOPMENT = "Digital Product Development"
    PRE_PRODUCTION = "Pre-production"
    POST_PRODUCTION_COSTS = "Post-production Costs"
    HARDWARE = "Hardware"
    IT_SERVICES = "IT Services"
    SOFTWARE = "Software"
    COURIER_EXPRESS_AND_POSTAL_SERVICES = "Courier, Express, and Postal Services"
    WAREHOUSING_AND_MATERIAL_HANDLING = "Warehousing and Material Handling"
    TRANSPORTATION_LOGISTICS = "Transportation Logistics"
    DELIVERY_SERVICES = "Delivery Services"
    ADVERTISING = "Advertising"
    OUTDOOR_ADVERTISING = "Outdoor Advertising"
    MARKETING_AGENCIES = "Marketing Agencies"
    DIRECT_MAIL = "Direct Mail"
    CUSTOMER_COMMUNICATION = "Customer Communication"
    ONLINE_MARKETING = "Online Marketing"
    EVENTS = "Events"
    PROMOTIONAL_MATERIALS = "Promotional Materials"
    WAREHOUSE_AND_OPERATIONAL_EQUIPMENT = "Warehouse and Operational Equipment"
    PRODUCTION_MACHINERY = "Production Machinery"
    SPARE_PARTS = "Spare Parts"
    INTERNAL_TRANSPORTATION = "Internal Transportation"
    PRODUCTION_MATERIALS = "Production Materials"
    CONSUMABLES = "Consumables"
    MAINTENANCE_AND_REPAIRS = "Maintenance and Repairs"


class OrderLine(BaseModel):
    """Represents a single order line in a procurement request."""

    position_description: str = Field(
        ..., description="Description of the item/service"
    )
    unit_price: float = Field(..., gt=0, description="Price per unit/item/service")
    amount: int = Field(
        ..., gt=0, description="The quantity or number of units being ordered"
    )
    unit: str = Field(
        ..., description="The unit of measure (e.g., licenses, pieces, hours)"
    )
    total_price: float = Field(
        ..., gt=0, description="Total price for this line (Unit Price x Amount)"
    )


class ProcurementRequestCreate(BaseModel):
    """Request payload for creating a new procurement request."""

    requestor_name: str = Field(
        ..., min_length=1, description="Full name of the person submitting the request"
    )
    title: str = Field(
        ...,
        min_length=1,
        description="Brief name or description of the product/service requested",
    )
    vendor_name: str = Field(
        ...,
        min_length=1,
        description="Name of the company or individual providing the items/services",
    )
    vat_id: str = Field(
        ..., min_length=1, description="VAT identification number of the vendor"
    )
    commodity_group: CommodityGroup = Field(
        ..., description="The category or group the requested items/services belong to"
    )
    order_lines: List[OrderLine] = Field(
        ..., min_length=1, description="List of order line items"
    )
    department: str = Field(
        ..., min_length=1, description="The department of the requestor"
    )
