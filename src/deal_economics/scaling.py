"""Chapter 7 orchestration for economics and capacity at customer scale."""

from __future__ import annotations

import json
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation, ROUND_CEILING
from pathlib import Path
from typing import Any, Mapping, Sequence

from .deal import ScenarioValidationError
from .recurring import RecurringScalePoint, RecurringScenario
from .reuse import ReuseScenario, ScalePoint


def _non_negative(name: str, value: Decimal) -> None:
    if not isinstance(value, Decimal) or not value.is_finite():
        raise ScenarioValidationError(f"{name} must be a finite Decimal")
    if value < 0:
        raise ScenarioValidationError(f"{name} cannot be negative")


def _count(customers: int) -> None:
    if isinstance(customers, bool) or not isinstance(customers, int):
        raise ScenarioValidationError("customer count must be an integer")
    if customers < 0:
        raise ScenarioValidationError("customer count cannot be negative")


@dataclass(frozen=True)
class CapacityResult:
    """Required work compared with one explicitly modeled capacity pool."""

    required_hours: Decimal
    available_hours: Decimal

    @property
    def utilization(self) -> Decimal:
        if self.available_hours == 0:
            return Decimal("0") if self.required_hours == 0 else Decimal("Infinity")
        return self.required_hours / self.available_hours

    @property
    def exceeded(self) -> bool:
        return self.required_hours > self.available_hours

    @property
    def capacity_equivalents(self) -> int:
        """Whole full-capacity equivalents needed; these are not necessarily employees."""
        if self.required_hours == 0:
            return 0
        if self.available_hours == 0:
            return 0  # no meaningful unit size exists
        return int(
            (self.required_hours / self.available_hours).to_integral_value(
                rounding=ROUND_CEILING
            )
        )


@dataclass(frozen=True)
class CapacityModel:
    solutions_hours_per_customer: Decimal
    implementation_hours_per_customer: Decimal
    annual_solutions_hours: Decimal
    annual_implementation_hours: Decimal

    def __post_init__(self) -> None:
        for name in (
            "solutions_hours_per_customer", "implementation_hours_per_customer",
            "annual_solutions_hours", "annual_implementation_hours",
        ):
            _non_negative(name, getattr(self, name))

    def solutions_at(self, customers: int) -> CapacityResult:
        _count(customers)
        return CapacityResult(self.solutions_hours_per_customer * customers,
                              self.annual_solutions_hours)

    def implementation_at(self, customers: int) -> CapacityResult:
        _count(customers)
        return CapacityResult(self.implementation_hours_per_customer * customers,
                              self.annual_implementation_hours)


@dataclass(frozen=True)
class CapstoneScalePoint:
    customers: int
    total_annual_customer_value: Decimal
    total_customer_implementation_investment: Decimal
    total_annual_recurring_customer_cost: Decimal
    aggregate_first_year_customer_net_benefit: Decimal
    representative_first_year_customer_roi: Decimal | None
    implementation: ScalePoint
    recurring: RecurringScalePoint
    solutions_capacity: CapacityResult
    implementation_capacity: CapacityResult

    @property
    def active_bottlenecks(self) -> tuple[str, ...]:
        constraints: list[str] = []
        if self.solutions_capacity.exceeded:
            constraints.append("solutions capacity")
        if self.implementation_capacity.exceeded:
            constraints.append("implementation capacity")
        if self.recurring.support_capacity_exceeded:
            constraints.append("support capacity")
        return tuple(constraints)

    @property
    def platform_recovered(self) -> bool:
        return self.implementation.foundation_remaining == 0


@dataclass(frozen=True)
class ScaleScenario:
    """Compose Chapters 5 and 6 with customer value and two capacity pools.

    All customers are deliberately treated as identical and acquired in one modeled
    year. That simplifying snapshot is a sensitivity tool, not a sales forecast.
    """

    scenario: str
    fictional: bool
    customer_counts: tuple[int, ...]
    annual_value_per_customer: Decimal
    implementation: ReuseScenario
    recurring: RecurringScenario
    capacity: CapacityModel

    def __post_init__(self) -> None:
        if not self.scenario.strip():
            raise ScenarioValidationError("scenario must have a name")
        if self.fictional is not True:
            raise ScenarioValidationError("Chapter 7 scenarios must be explicitly fictional")
        _non_negative("annual_value_per_customer", self.annual_value_per_customer)
        for count in self.customer_counts:
            _count(count)

    def at(self, customers: int) -> CapstoneScalePoint:
        _count(customers)
        implementation = self.implementation.at(customers)
        recurring = self.recurring.at(customers)
        count = Decimal(customers)
        implementation_investment = self.implementation.implementation_price * count
        annual_recurring_cost = recurring.arr
        total_cost = implementation_investment + annual_recurring_cost
        value = self.annual_value_per_customer * count
        net_benefit = value - total_cost
        per_customer_cost = (
            self.implementation.implementation_price
            + self.recurring.monthly_fee_per_customer * Decimal("12")
        )
        representative_roi = (
            None if per_customer_cost == 0
            else (self.annual_value_per_customer - per_customer_cost) / per_customer_cost
        )
        return CapstoneScalePoint(
            customers, value, implementation_investment, annual_recurring_cost,
            net_benefit, representative_roi, implementation, recurring,
            self.capacity.solutions_at(customers),
            self.capacity.implementation_at(customers),
        )

    def first_exceeded(self, constraint: str) -> int | None:
        checks = {
            "solutions capacity": lambda p: p.solutions_capacity.exceeded,
            "implementation capacity": lambda p: p.implementation_capacity.exceeded,
            "support capacity": lambda p: p.recurring.support_capacity_exceeded,
        }
        if constraint not in checks:
            raise ScenarioValidationError(f"unknown capacity constraint: {constraint}")
        return next((count for count in self.customer_counts if checks[constraint](self.at(count))), None)

    @property
    def first_modeled_bottleneck(self) -> tuple[int, tuple[str, ...]] | None:
        for count in self.customer_counts:
            bottlenecks = self.at(count).active_bottlenecks
            if bottlenecks:
                return count, bottlenecks
        return None

    @classmethod
    def from_mapping(cls, source: Mapping[str, Any]) -> "ScaleScenario":
        try:
            counts = source["customer_counts"]
            if not isinstance(counts, Sequence) or isinstance(counts, (str, bytes)):
                raise ScenarioValidationError("customer_counts must be a list")
            implementation = ReuseScenario.from_mapping(source["implementation"])
            recurring_source = source["recurring"]
            capacity_source = source["capacity"]
            recurring = RecurringScenario(
                scenario=str(source["scenario"]), fictional=source["fictional"],
                implementation_price=implementation.implementation_price,
                monthly_fee_per_customer=Decimal(str(recurring_source["monthly_fee_per_customer"])),
                hosting_per_customer=Decimal(str(recurring_source["hosting_per_customer"])),
                monitoring_per_customer=Decimal(str(recurring_source["monitoring_per_customer"])),
                support_hours_per_customer=Decimal(str(recurring_source["support_hours_per_customer"])),
                support_hourly_cost=Decimal(str(recurring_source["support_hourly_cost"])),
                available_support_hours_per_month=Decimal(str(capacity_source["monthly_support_hours"])),
                customer_counts=tuple(counts),
            )
            capacity = CapacityModel(
                Decimal(str(capacity_source["solutions_hours_per_customer"])),
                Decimal(str(capacity_source["implementation_hours_per_customer"])),
                Decimal(str(capacity_source["annual_solutions_hours"])),
                Decimal(str(capacity_source["annual_implementation_hours"])),
            )
            return cls(str(source["scenario"]), source["fictional"], tuple(counts),
                       Decimal(str(source["annual_value_per_customer"])),
                       implementation, recurring, capacity)
        except KeyError as exc:
            raise ScenarioValidationError(f"missing scaling field: {exc.args[0]}") from exc
        except (InvalidOperation, TypeError, ValueError) as exc:
            if isinstance(exc, ScenarioValidationError):
                raise
            raise ScenarioValidationError("scaling fields must contain valid values") from exc


@dataclass(frozen=True)
class CapstoneComparison:
    custom_every_time: ScaleScenario
    reusable_delivery: ScaleScenario
    aggressive_growth_target: int

    def __post_init__(self) -> None:
        _count(self.aggressive_growth_target)

    @classmethod
    def from_mapping(cls, source: Mapping[str, Any]) -> "CapstoneComparison":
        reusable = ScaleScenario.from_mapping(source)
        try:
            custom = ScaleScenario.from_mapping({
                **source,
                "scenario": "Scenario A — Custom Every Time",
                "implementation": source["custom_every_time"],
                "capacity": {
                    **source["capacity"],
                    "implementation_hours_per_customer": source["custom_every_time"][
                        "implementation_hours_per_customer"
                    ],
                },
            })
            return cls(custom, reusable, int(source["aggressive_growth_target"]))
        except KeyError as exc:
            raise ScenarioValidationError(f"missing scaling field: {exc.args[0]}") from exc


def load_capstone_comparison(path: str | Path) -> CapstoneComparison:
    with Path(path).open(encoding="utf-8") as scenario_file:
        source = json.load(scenario_file)
    if not isinstance(source, dict):
        raise ScenarioValidationError("scenario JSON must contain an object")
    return CapstoneComparison.from_mapping(source)
