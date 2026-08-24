"""Chapter 4's three-party engagement-economics model."""

from __future__ import annotations

import json
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Mapping, Sequence

from .deal import ScenarioValidationError


def _non_negative_decimal(name: str, value: Decimal) -> None:
    if not isinstance(value, Decimal) or not value.is_finite():
        raise ScenarioValidationError(f"{name} must be a finite Decimal")
    if value < 0:
        raise ScenarioValidationError(f"{name} cannot be negative")


@dataclass(frozen=True)
class SolutionsEffort:
    """One category of solutions-layer work for a closed engagement."""

    name: str
    hours: Decimal

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ScenarioValidationError("solutions effort name cannot be blank")
        _non_negative_decimal("solutions effort hours", self.hours)


@dataclass(frozen=True)
class EngagementEconomics:
    """Fictional customer, solutions, and engineering assumptions for one deal.

    ``engineering_delivery_cost`` is Garcia Systems' direct delivery allocation
    (and therefore revenue to the partner). ``partner_modeled_delivery_cost`` is
    the partner's distinct internal modeled cost; equality is only an assumption.
    """

    scenario: str
    fictional: bool
    annual_customer_value: Decimal
    customer_price: Decimal
    engineering_delivery_cost: Decimal
    partner_modeled_delivery_cost: Decimal
    other_direct_costs: Decimal
    solutions_effort: tuple[SolutionsEffort, ...]

    def __post_init__(self) -> None:
        if not self.scenario.strip():
            raise ScenarioValidationError("scenario must have a name")
        if self.fictional is not True:
            raise ScenarioValidationError("Chapter 4 scenarios must be explicitly fictional")
        for name in (
            "annual_customer_value",
            "customer_price",
            "engineering_delivery_cost",
            "partner_modeled_delivery_cost",
            "other_direct_costs",
        ):
            _non_negative_decimal(name, getattr(self, name))
        if any(not isinstance(item, SolutionsEffort) for item in self.solutions_effort):
            raise ScenarioValidationError("solutions_effort must contain SolutionsEffort values")

    @property
    def customer_revenue(self) -> Decimal:
        return self.customer_price

    @property
    def gross_contribution(self) -> Decimal:
        """Contribution before indirect company overhead, not net profit."""
        return self.customer_revenue - self.engineering_delivery_cost - self.other_direct_costs

    @property
    def solutions_hours(self) -> Decimal:
        return sum((item.hours for item in self.solutions_effort), Decimal("0"))

    @property
    def effective_contribution_per_solutions_hour(self) -> Decimal | None:
        return None if self.solutions_hours == 0 else self.gross_contribution / self.solutions_hours

    @property
    def customer_net_benefit(self) -> Decimal:
        return self.annual_customer_value - self.customer_price

    @property
    def customer_roi(self) -> Decimal | None:
        return None if self.customer_price == 0 else self.customer_net_benefit / self.customer_price

    @property
    def engineering_partner_revenue(self) -> Decimal:
        return self.engineering_delivery_cost

    @property
    def engineering_partner_contribution(self) -> Decimal:
        return self.engineering_partner_revenue - self.partner_modeled_delivery_cost

    @property
    def delivery_budget_sustainable(self) -> bool:
        return self.engineering_partner_revenue >= self.partner_modeled_delivery_cost

    @classmethod
    def from_mapping(cls, source: Mapping[str, Any]) -> "EngagementEconomics":
        """Build an immutable model without modifying the editable source data."""
        try:
            raw_effort = source["solutions_effort"]
            if not isinstance(raw_effort, Sequence) or isinstance(raw_effort, (str, bytes)):
                raise ScenarioValidationError("solutions_effort must be a list")
            effort = tuple(_parse_effort(item) for item in raw_effort)
            return cls(
                scenario=str(source["scenario"]),
                fictional=source["fictional"],
                annual_customer_value=Decimal(str(source["annual_customer_value"])),
                customer_price=Decimal(str(source["customer_price"])),
                engineering_delivery_cost=Decimal(str(source["engineering_delivery_cost"])),
                partner_modeled_delivery_cost=Decimal(
                    str(source["partner_modeled_delivery_cost"])
                ),
                other_direct_costs=Decimal(str(source["other_direct_costs"])),
                solutions_effort=effort,
            )
        except KeyError as exc:
            raise ScenarioValidationError(f"missing allocation field: {exc.args[0]}") from exc
        except (InvalidOperation, TypeError, ValueError) as exc:
            if isinstance(exc, ScenarioValidationError):
                raise
            raise ScenarioValidationError("allocation fields must contain valid numbers") from exc


def _parse_effort(source: Any) -> SolutionsEffort:
    if not isinstance(source, Mapping):
        raise ScenarioValidationError("each solutions effort item must be an object")
    try:
        return SolutionsEffort(str(source["name"]), Decimal(str(source["hours"])))
    except KeyError as exc:
        raise ScenarioValidationError(f"missing solutions effort field: {exc.args[0]}") from exc


def load_engagement_economics(path: str | Path) -> EngagementEconomics:
    with Path(path).open(encoding="utf-8") as scenario_file:
        source = json.load(scenario_file)
    if not isinstance(source, dict):
        raise ScenarioValidationError("scenario JSON must contain an object")
    return EngagementEconomics.from_mapping(source)
