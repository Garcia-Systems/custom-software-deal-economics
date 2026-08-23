"""Chapter 1's transparent current-state business-value model."""

from __future__ import annotations

import json
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Mapping, Sequence

from .deal import ScenarioValidationError


def _validate_decimal(name: str, value: Decimal) -> None:
    if not isinstance(value, Decimal) or not value.is_finite():
        raise ScenarioValidationError(f"{name} must be a finite Decimal")
    if value < 0:
        raise ScenarioValidationError(f"{name} cannot be negative")


@dataclass(frozen=True)
class LaborBurden:
    """Time per occurrence × annual frequency × loaded hourly cost."""

    hours_per_occurrence: Decimal
    occurrences_per_year: Decimal
    loaded_hourly_cost: Decimal

    def __post_init__(self) -> None:
        for name in ("hours_per_occurrence", "occurrences_per_year", "loaded_hourly_cost"):
            _validate_decimal(name, getattr(self, name))

    @property
    def annual_cost(self) -> Decimal:
        return self.hours_per_occurrence * self.occurrences_per_year * self.loaded_hourly_cost


@dataclass(frozen=True)
class PeriodicBurden:
    """Economic burden per period × periods per year."""

    cost_per_period: Decimal
    periods_per_year: Decimal

    def __post_init__(self) -> None:
        _validate_decimal("cost_per_period", self.cost_per_period)
        _validate_decimal("periods_per_year", self.periods_per_year)

    @property
    def annual_cost(self) -> Decimal:
        return self.cost_per_period * self.periods_per_year


@dataclass(frozen=True)
class EventBurden:
    """Annual event frequency × economic cost per event."""

    events_per_year: Decimal
    cost_per_event: Decimal

    def __post_init__(self) -> None:
        _validate_decimal("events_per_year", self.events_per_year)
        _validate_decimal("cost_per_event", self.cost_per_event)

    @property
    def annual_cost(self) -> Decimal:
        return self.events_per_year * self.cost_per_event


Burden = LaborBurden | PeriodicBurden | EventBurden


@dataclass(frozen=True)
class ValueComponent:
    """One understandable burden and its explicit improvement assumption."""

    name: str
    description: str
    burden: Burden
    improvement_rate: Decimal

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ScenarioValidationError("component name cannot be blank")
        _validate_decimal("improvement_rate", self.improvement_rate)
        if self.improvement_rate > 1:
            raise ScenarioValidationError("improvement_rate cannot exceed 1 (100%)")

    @property
    def current_state_cost(self) -> Decimal:
        return self.burden.annual_cost

    @property
    def recoverable_value(self) -> Decimal:
        return self.current_state_cost * self.improvement_rate


@dataclass(frozen=True)
class ValueAssessment:
    """A fictional scenario composed from independently inspectable burdens."""

    scenario: str
    fictional: bool
    components: tuple[ValueComponent, ...]

    def __post_init__(self) -> None:
        if not self.scenario.strip():
            raise ScenarioValidationError("scenario must have a name")
        if self.fictional is not True:
            raise ScenarioValidationError("Chapter 1 scenarios must be explicitly fictional")
        if not self.components:
            raise ScenarioValidationError("at least one value component is required")

    @property
    def total_current_state_cost(self) -> Decimal:
        return sum((component.current_state_cost for component in self.components), Decimal("0"))

    @property
    def total_recoverable_value(self) -> Decimal:
        return sum((component.recoverable_value for component in self.components), Decimal("0"))

    @property
    def unrecovered_burden(self) -> Decimal:
        return self.total_current_state_cost - self.total_recoverable_value

    @classmethod
    def from_mapping(cls, source: Mapping[str, Any]) -> "ValueAssessment":
        """Parse editable data without modifying the supplied mapping."""
        try:
            raw_components = source["components"]
            if not isinstance(raw_components, Sequence) or isinstance(raw_components, (str, bytes)):
                raise ScenarioValidationError("components must be a list")
            components = tuple(_parse_component(item) for item in raw_components)
            return cls(str(source["scenario"]), source["fictional"], components)
        except KeyError as exc:
            raise ScenarioValidationError(f"missing scenario field: {exc.args[0]}") from exc
        except (InvalidOperation, ValueError) as exc:
            if isinstance(exc, ScenarioValidationError):
                raise
            raise ScenarioValidationError("numeric fields must be valid decimal numbers") from exc


def _decimal(source: Mapping[str, Any], name: str) -> Decimal:
    return Decimal(str(source[name]))


def _parse_component(source: Any) -> ValueComponent:
    if not isinstance(source, Mapping):
        raise ScenarioValidationError("each component must be an object")
    try:
        kind = source["type"]
        if kind == "labor":
            burden: Burden = LaborBurden(
                _decimal(source, "hours_per_occurrence"),
                _decimal(source, "occurrences_per_year"),
                _decimal(source, "loaded_hourly_cost"),
            )
        elif kind == "periodic":
            burden = PeriodicBurden(
                _decimal(source, "cost_per_period"), _decimal(source, "periods_per_year")
            )
        elif kind == "event":
            burden = EventBurden(
                _decimal(source, "events_per_year"), _decimal(source, "cost_per_event")
            )
        else:
            raise ScenarioValidationError(f"unknown component type: {kind}")
        return ValueComponent(
            str(source["name"]),
            str(source.get("description", "")),
            burden,
            _decimal(source, "improvement_rate"),
        )
    except KeyError as exc:
        raise ScenarioValidationError(f"missing component field: {exc.args[0]}") from exc


def load_value_assessment(path: str | Path) -> ValueAssessment:
    with Path(path).open(encoding="utf-8") as scenario_file:
        source = json.load(scenario_file)
    if not isinstance(source, dict):
        raise ScenarioValidationError("scenario JSON must contain an object")
    return ValueAssessment.from_mapping(source)
