import json
from typing import Protocol

from fastmcp import Context
from pydantic import Field

from asklio_api.models.commodity_group import CommodityGroupInfo
from asklio_api.models.procurement import ProcurementRequestCreate
from asklio_api.repository import (
    ProcurementRequestStatus,
    ProcurementRequestStored,
    Repository,
)


class IntakeApi(Protocol):
    def get_commodity_groups(self) -> set[CommodityGroupInfo]: ...
    def is_valid_commodity_group(self, name: str) -> bool: ...
    def create_procurement_request(
        self,
        request: ProcurementRequestCreate,
        ctx: Context | None = None,
    ) -> dict[str, str]: ...
    def get_all_requests(self) -> list[ProcurementRequestStored]: ...
    def get_request_by_id(self, request_id: str) -> ProcurementRequestStored | None: ...
    def update_request_status(
        self, request_id: str, status: ProcurementRequestStatus
    ) -> ProcurementRequestStored | None: ...


class CommodityGroupNotFoundException(Exception): ...


class Intake(IntakeApi):
    """Manages intake operations including commodity group validation."""

    def __init__(self, commodity_group_path: str, repository: Repository) -> None:
        self.commodity_groups_path = commodity_group_path
        self.commodity_groups = self._load_commodity_groups()
        self._valid_names = {cg.name for cg in self.commodity_groups}
        self.repository = repository

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

        # Store the request in the repository
        stored_request = self.repository.store_procurement_request(request)

        return {
            "message": "Procurement request successful",
            "id": stored_request.id,
            "status": stored_request.status.value,
        }

    def is_valid_commodity_group(self, name: str) -> bool:
        """Check if a commodity group name is valid."""
        return name in self._valid_names

    def get_all_requests(self) -> list[ProcurementRequestStored]:
        """Get all stored procurement requests."""
        return self.repository.get_all()

    def get_request_by_id(self, request_id: str) -> ProcurementRequestStored | None:
        """Get a procurement request by ID."""
        return self.repository.get_by_id(request_id)

    def update_request_status(
        self, request_id: str, status: ProcurementRequestStatus
    ) -> ProcurementRequestStored | None:
        """Update the status of a procurement request."""
        stored_request = self.repository.get_by_id(request_id)
        if stored_request:
            stored_request.status = status
        return stored_request
