"""Chapter 3's compact, effort-based delivery-cost model."""

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
class LaborComponent:
    """One fictional delivery role modeled as active hours times an hourly rate."""

    name: str
    hours: Decimal
    hourly_rate: Decimal

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ScenarioValidationError("labor component name cannot be blank")
        _non_negative_decimal("hours", self.hours)
        _non_negative_decimal("hourly_rate", self.hourly_rate)

    @property
    def cost(self) -> Decimal:
        return self.hours * self.hourly_rate


@dataclass(frozen=True)
class DeliveryScenario:
    """Fictional single-engagement labor, reserve, budget, and elapsed duration."""

    scenario: str
    fictional: bool
    labor: tuple[LaborComponent, ...]
    rework_reserve: Decimal
    delivery_budget: Decimal
    elapsed_weeks: Decimal

    def __post_init__(self) -> None:
        if not self.scenario.strip():
            raise ScenarioValidationError("scenario must have a name")
        if self.fictional is not True:
            raise ScenarioValidationError("Chapter 3 scenarios must be explicitly fictional")
        if not self.labor:
            raise ScenarioValidationError("at least one labor component is required")
        if any(not isinstance(component, LaborComponent) for component in self.labor):
            raise ScenarioValidationError("labor must contain LaborComponent values")
        _non_negative_decimal("rework_reserve", self.rework_reserve)
        _non_negative_decimal("delivery_budget", self.delivery_budget)
        _non_negative_decimal("elapsed_weeks", self.elapsed_weeks)
        if self.elapsed_weeks == 0:
            raise ScenarioValidationError("elapsed_weeks must be positive")

    @property
    def labor_cost(self) -> Decimal:
        return sum((component.cost for component in self.labor), Decimal("0"))

    @property
    def active_labor_hours(self) -> Decimal:
        return sum((component.hours for component in self.labor), Decimal("0"))

    @property
    def total_delivery_cost(self) -> Decimal:
        return self.labor_cost + self.rework_reserve

    @property
    def budget_variance(self) -> Decimal:
        """Budget minus modeled cost: positive is under and negative is over budget."""
        return self.delivery_budget - self.total_delivery_cost

    @classmethod
    def from_mapping(cls, source: Mapping[str, Any]) -> "DeliveryScenario":
        """Build a scenario from editable data without modifying ``source``."""
        try:
            raw_labor = source["labor"]
            if not isinstance(raw_labor, Sequence) or isinstance(raw_labor, (str, bytes)):
                raise ScenarioValidationError("labor must be a list")
            labor = tuple(_parse_labor(item) for item in raw_labor)
            return cls(
                scenario=str(source["scenario"]),
                fictional=source["fictional"],
                labor=labor,
                rework_reserve=Decimal(str(source["rework_reserve"])),
                delivery_budget=Decimal(str(source["delivery_budget"])),
                elapsed_weeks=Decimal(str(source["elapsed_weeks"])),
            )
        except KeyError as exc:
            raise ScenarioValidationError(f"missing delivery field: {exc.args[0]}") from exc
        except (InvalidOperation, TypeError, ValueError) as exc:
            if isinstance(exc, ScenarioValidationError):
                raise
            raise ScenarioValidationError("delivery fields must contain valid numbers") from exc


def _parse_labor(source: Any) -> LaborComponent:
    if not isinstance(source, Mapping):
        raise ScenarioValidationError("each labor component must be an object")
    try:
        return LaborComponent(
            name=str(source["name"]),
            hours=Decimal(str(source["hours"])),
            hourly_rate=Decimal(str(source["hourly_rate"])),
        )
    except KeyError as exc:
        raise ScenarioValidationError(f"missing labor field: {exc.args[0]}") from exc


def load_delivery_scenario(path: str | Path) -> DeliveryScenario:
    with Path(path).open(encoding="utf-8") as scenario_file:
        source = json.load(scenario_file)
    if not isinstance(source, dict):
        raise ScenarioValidationError("scenario JSON must contain an object")
    return DeliveryScenario.from_mapping(source)
