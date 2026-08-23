"""Chapter 0's deliberately small three-party deal model.

All calculations retain ``Decimal`` precision. Rounding is a presentation concern:
currency is normally displayed to cents, percentages to two decimal places, and
payback to two decimal places by the example program.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Mapping


class ScenarioValidationError(ValueError):
    """Raised when scenario data cannot represent a valid learning experiment."""


MONEY_FIELDS = (
    "current_state_cost",
    "recoverable_value",
    "customer_price",
    "engineering_cost",
    "other_direct_costs",
)


@dataclass(frozen=True)
class DealScenario:
    """Fictional assumptions for one introductory custom-software engagement."""

    scenario: str
    fictional: bool
    current_state_cost: Decimal
    recoverable_value: Decimal
    customer_price: Decimal
    engineering_cost: Decimal
    other_direct_costs: Decimal

    def __post_init__(self) -> None:
        if not self.scenario.strip():
            raise ScenarioValidationError("scenario must have a name")
        if self.fictional is not True:
            raise ScenarioValidationError("Chapter 0 scenarios must be explicitly fictional")
        for field_name in MONEY_FIELDS:
            value = getattr(self, field_name)
            if not isinstance(value, Decimal):
                raise ScenarioValidationError(f"{field_name} must be a Decimal")
            if not value.is_finite():
                raise ScenarioValidationError(f"{field_name} must be finite")
            if value < 0:
                raise ScenarioValidationError(f"{field_name} cannot be negative")

    @property
    def revenue(self) -> Decimal:
        """Money received from the customer (the customer price)."""
        return self.customer_price

    @property
    def total_direct_costs(self) -> Decimal:
        return self.engineering_cost + self.other_direct_costs

    @property
    def gross_contribution(self) -> Decimal:
        """Contribution before indirect overhead, taxes, and other expenses."""
        return self.revenue - self.total_direct_costs

    @property
    def gross_margin(self) -> Decimal | None:
        """Gross contribution divided by revenue, or ``None`` at zero revenue."""
        if self.revenue == 0:
            return None
        return self.gross_contribution / self.revenue

    @property
    def customer_first_year_benefit(self) -> Decimal:
        return self.recoverable_value

    @property
    def customer_first_year_net_benefit(self) -> Decimal:
        return self.customer_first_year_benefit - self.customer_price

    @property
    def customer_roi(self) -> Decimal | None:
        """Net benefit divided by investment, or ``None`` at zero investment."""
        if self.customer_price == 0:
            return None
        return self.customer_first_year_net_benefit / self.customer_price

    @property
    def approximate_payback_months(self) -> Decimal | None:
        """Price divided by average monthly benefit, or ``None`` with no benefit."""
        if self.customer_first_year_benefit == 0:
            return None
        monthly_benefit = self.customer_first_year_benefit / Decimal("12")
        return self.customer_price / monthly_benefit

    @classmethod
    def from_mapping(cls, source: Mapping[str, Any]) -> DealScenario:
        """Build a validated scenario without mutating ``source``."""
        try:
            values = {name: Decimal(str(source[name])) for name in MONEY_FIELDS}
            return cls(
                scenario=str(source["scenario"]),
                fictional=source["fictional"],
                **values,
            )
        except KeyError as exc:
            raise ScenarioValidationError(f"missing scenario field: {exc.args[0]}") from exc
        except (InvalidOperation, ValueError) as exc:
            raise ScenarioValidationError("monetary fields must be valid decimal numbers") from exc


def load_scenario(path: str | Path) -> DealScenario:
    """Load a UTF-8 JSON scenario and parse money exactly as ``Decimal`` values."""
    with Path(path).open(encoding="utf-8") as scenario_file:
        source = json.load(scenario_file)
    if not isinstance(source, dict):
        raise ScenarioValidationError("scenario JSON must contain an object")
    return DealScenario.from_mapping(source)

