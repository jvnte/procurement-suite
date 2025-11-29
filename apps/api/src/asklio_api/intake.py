import json
from typing import Protocol

from asklio_api.models.commodity_group import CommodityGroupInfo


class IntakeApi(Protocol):
    def get_commodity_groups(self) -> set[CommodityGroupInfo]: ...
    def is_valid_commodity_group(self, name: str) -> bool: ...


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
        """Get all commodity groups."""
        return self.commodity_groups

    def is_valid_commodity_group(self, name: str) -> bool:
        """Check if a commodity group name is valid."""
        return name in self._valid_names
