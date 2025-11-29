from pydantic import BaseModel


class CommodityGroupInfo(BaseModel):
    """Represents a commodity group with its category and name."""

    category: str
    name: str

    def __hash__(self) -> int:
        """Make CommodityGroupInfo hashable so it can be used in sets."""
        return hash((self.category, self.name))

    def __eq__(self, other: object) -> bool:
        """Check equality based on category and name."""
        if not isinstance(other, CommodityGroupInfo):
            return False
        return self.category == other.category and self.name == other.name
