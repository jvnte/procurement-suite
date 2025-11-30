from datetime import datetime
from enum import Enum
from typing import Protocol
from uuid import uuid4

from asklio_api.models.procurement import ProcurementRequestCreate


class ProcurementRequestStatus(str, Enum):
    """Status of a procurement request."""

    OPEN = "open"
    IN_PROGRESS = "in-progress"
    CLOSED = "closed"


class ProcurementRequestStored:
    """Represents a stored procurement request with metadata."""

    def __init__(
        self,
        request: ProcurementRequestCreate,
        status: ProcurementRequestStatus = ProcurementRequestStatus.OPEN,
    ):
        self.id: str = str(uuid4())
        self.created_at: datetime = datetime.utcnow()
        self.request: ProcurementRequestCreate = request
        self.status: ProcurementRequestStatus = status

    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            "id": self.id,
            "created_at": self.created_at.isoformat(),
            "status": self.status.value,
            "request": self.request.model_dump(),
        }


class Repository(Protocol):
    """Protocol for procurement request repository operations."""

    def store_procurement_request(
        self, request: ProcurementRequestCreate
    ) -> ProcurementRequestStored: ...

    def get_all(self) -> list[ProcurementRequestStored]: ...
    def get_by_id(self, request_id: str) -> ProcurementRequestStored | None: ...
    def clear(self) -> None: ...


class InMemoryRepository(Repository):
    """In-memory implementation of the procurement request repository."""

    def __init__(self) -> None:
        self._storage: dict[str, ProcurementRequestStored] = {}

    def store_procurement_request(
        self, request: ProcurementRequestCreate
    ) -> ProcurementRequestStored:
        """
        Store a procurement request in memory.

        Args:
            request: The procurement request to store

        Returns:
            The stored procurement request with ID and timestamp
        """
        stored_request = ProcurementRequestStored(request)
        self._storage[stored_request.id] = stored_request
        return stored_request

    def get_all(self) -> list[ProcurementRequestStored]:
        """Get all stored procurement requests."""
        return list(self._storage.values())

    def get_by_id(self, request_id: str) -> ProcurementRequestStored | None:
        """Get a procurement request by ID."""
        return self._storage.get(request_id)

    def clear(self) -> None:
        """Clear all stored requests (useful for testing)."""
        self._storage.clear()
