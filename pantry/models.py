"""Python objects built from database rows (PROVIDED)."""

from dataclasses import dataclass, fields
from decimal import Decimal
from typing import Any

from pantry.exceptions import PantryError

CATEGORIES = ("meat", "fish", "plant", "mineral", "magic")


@dataclass
class Food:
    """One food of the pantry. Mirrors one row of the ``foods`` table."""

    name: str
    category: str
    stock: int
    unit_price: Decimal
    id: int | None = None  # None until PostgreSQL gives it one

    def __post_init__(self) -> None:
        """Same rules as the CHECK constraints of schema.sql: one rule, two guards."""
        if self.category not in CATEGORIES:
            raise PantryError(f"Unknown category: {self.category!r}.")
        if self.stock < 0:
            raise PantryError(f"stock must be >= 0, got {self.stock}.")

    @classmethod
    def from_row(cls, row: dict[str, Any]) -> "Food":
        """Build a Food from a RealDictCursor row. Extra columns are ignored."""
        return cls(**{f.name: row[f.name] for f in fields(cls) if f.name in row})

    @property
    def stock_value(self) -> Decimal:
        """Value of what is on the shelf."""
        return self.stock * self.unit_price
