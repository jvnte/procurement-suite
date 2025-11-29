import json
from typing import Protocol

from fastmcp import Context
from pydantic import Field

from asklio_api.models.commodity_group import CommodityGroupInfo
from asklio_api.models.procurement import ProcurementRequestCreate


class IntakeApi(Protocol):
    def get_commodity_groups(self) -> set[CommodityGroupInfo]: ...
    def is_valid_commodity_group(self, name: str) -> bool: ...
    def create_procurement_request(
        self,
        request: ProcurementRequestCreate,
        ctx: Context | None = None,
    ) -> dict[str, str]: ...


class CommodityGroupNotFoundException(Exception): ...


class Intake(IntakeApi):
    """Manages intake operations including commodity group validation."""

    def __init__(self, commodity_group_path: str) -> None:
        self.commodity_groups_path = commodity_group_path
        self.commodity_groups = self._load_commodity_groups()
        self._valid_names = {cg.name for cg in self.commodity_groups}

    def _load_commodity_groups(self) -> set[CommodityGroupInfo]:
        with open(self.commodity_groups_path, "r") as f:
            data = json.load(f)
        return {CommodityGroupInfo(**item) for item in data}

    def get_commodity_groups(self) -> set[CommodityGroupInfo]:
        """Get information about all valid commodity groups"""
        return self.commodity_groups

    def create_procurement_request(
        self,
        request: ProcurementRequestCreate = Field(
            ..., description="The request payload of a procurement request"
        ),
        ctx: Context | None = None,
    ) -> dict[str, str]:
        """Try to perform a procurement request"""
        if not self.is_valid_commodity_group(request.commodity_group):
            # TODO Return something useful for the Agent
            raise CommodityGroupNotFoundException
        return {"message": f"Procurement request successful: {request}"}

    def is_valid_commodity_group(self, name: str) -> bool:
        """Check if a commodity group name is valid."""
        return name in self._valid_names
