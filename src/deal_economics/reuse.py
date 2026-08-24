"""Chapter 5's deterministic reusable-delivery economics model."""

from __future__ import annotations

import json
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation, ROUND_CEILING, ROUND_FLOOR
from pathlib import Path
from typing import Any, Mapping, Sequence

from .deal import ScenarioValidationError


def _money(name: str, value: Decimal) -> None:
    if not isinstance(value, Decimal) or not value.is_finite():
        raise ScenarioValidationError(f"{name} must be a finite Decimal")
    if value < 0:
        raise ScenarioValidationError(f"{name} cannot be negative")


def _customers(value: int) -> None:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ScenarioValidationError("customer count must be an integer")
    if value < 0:
        raise ScenarioValidationError("customer count cannot be negative")


@dataclass(frozen=True)
class ScalePoint:
    """Cumulative implementation economics at one customer count."""

    customers: int
    revenue: Decimal
    customer_specific_delivery_cost: Decimal
    foundation_investment: Decimal
    total_cost: Decimal
    cumulative_contribution: Decimal
    foundation_remaining: Decimal


@dataclass(frozen=True)
class ReuseScenario:
    """A fixed foundation plus explicit marginal implementation assumptions."""

    foundation_investment: Decimal
    implementation_price: Decimal
    delivery_cost_per_customer: Decimal

    def __post_init__(self) -> None:
        for name in (
            "foundation_investment",
            "implementation_price",
            "delivery_cost_per_customer",
        ):
            _money(name, getattr(self, name))

    @property
    def contribution_per_customer(self) -> Decimal:
        """Contribution available before recovering the foundation."""
        return self.implementation_price - self.delivery_cost_per_customer

    def revenue_at(self, customers: int) -> Decimal:
        _customers(customers)
        return self.implementation_price * customers

    def delivery_cost_at(self, customers: int) -> Decimal:
        _customers(customers)
        return self.delivery_cost_per_customer * customers

    def total_cost_at(self, customers: int) -> Decimal:
        return self.foundation_investment + self.delivery_cost_at(customers)

    def cumulative_contribution_at(self, customers: int) -> Decimal:
        return self.revenue_at(customers) - self.total_cost_at(customers)

    def foundation_remaining_at(self, customers: int) -> Decimal:
        _customers(customers)
        remaining = self.foundation_investment - self.contribution_per_customer * customers
        return max(Decimal("0"), remaining)

    def at(self, customers: int) -> ScalePoint:
        revenue = self.revenue_at(customers)
        delivery = self.delivery_cost_at(customers)
        total = self.foundation_investment + delivery
        return ScalePoint(
            customers,
            revenue,
            delivery,
            self.foundation_investment,
            total,
            revenue - total,
            self.foundation_remaining_at(customers),
        )

    @property
    def break_even_customer(self) -> int | None:
        """First count with cumulative contribution >= 0, or no break-even."""
        if self.contribution_per_customer <= 0:
            return None
        return int(
            (self.foundation_investment / self.contribution_per_customer).to_integral_value(
                rounding=ROUND_CEILING
            )
        )

    @classmethod
    def from_mapping(cls, source: Mapping[str, Any]) -> "ReuseScenario":
        try:
            return cls(
                Decimal(str(source["foundation_investment"])),
                Decimal(str(source["implementation_price"])),
                Decimal(str(source["delivery_cost_per_customer"])),
            )
        except KeyError as exc:
            raise ScenarioValidationError(f"missing reuse field: {exc.args[0]}") from exc
        except (InvalidOperation, TypeError, ValueError) as exc:
            if isinstance(exc, ScenarioValidationError):
                raise
            raise ScenarioValidationError("reuse fields must contain valid numbers") from exc


@dataclass(frozen=True)
class ReuseComparison:
    """Two fictional delivery approaches evaluated at identical scale."""

    scenario: str
    fictional: bool
    customer_counts: tuple[int, ...]
    custom_every_time: ReuseScenario
    reusable_foundation: ReuseScenario

    def __post_init__(self) -> None:
        if not self.scenario.strip():
            raise ScenarioValidationError("scenario must have a name")
        if self.fictional is not True:
            raise ScenarioValidationError("Chapter 5 scenarios must be explicitly fictional")
        for count in self.customer_counts:
            _customers(count)

    def stronger_at(self, customers: int) -> str:
        custom = self.custom_every_time.cumulative_contribution_at(customers)
        reuse = self.reusable_foundation.cumulative_contribution_at(customers)
        if reuse > custom:
            return "reusable foundation"
        if custom > reuse:
            return "custom every time"
        return "equal"

    @property
    def crossover_customer(self) -> int | None:
        """First count where reuse contribution is strictly greater than custom."""
        custom_rate = self.custom_every_time.contribution_per_customer
        reuse_rate = self.reusable_foundation.contribution_per_customer
        advantage_per_customer = reuse_rate - custom_rate
        initial_disadvantage = (
            self.reusable_foundation.foundation_investment
            - self.custom_every_time.foundation_investment
        )
        if advantage_per_customer <= 0:
            return 0 if initial_disadvantage < 0 else None
        if initial_disadvantage < 0:
            return 0
        # Strict crossover: floor(disadvantage / advantage) + 1.
        return int(
            (initial_disadvantage / advantage_per_customer).to_integral_value(
                rounding=ROUND_FLOOR
            )
        ) + 1

    @classmethod
    def from_mapping(cls, source: Mapping[str, Any]) -> "ReuseComparison":
        try:
            raw_counts = source["customer_counts"]
            if not isinstance(raw_counts, Sequence) or isinstance(raw_counts, (str, bytes)):
                raise ScenarioValidationError("customer_counts must be a list")
            counts = tuple(raw_counts)
            return cls(
                str(source["scenario"]),
                source["fictional"],
                counts,
                ReuseScenario.from_mapping(source["custom_every_time"]),
                ReuseScenario.from_mapping(source["reusable_foundation"]),
            )
        except KeyError as exc:
            raise ScenarioValidationError(f"missing comparison field: {exc.args[0]}") from exc


def load_reuse_comparison(path: str | Path) -> ReuseComparison:
    with Path(path).open(encoding="utf-8") as scenario_file:
        source = json.load(scenario_file)
    if not isinstance(source, dict):
        raise ScenarioValidationError("scenario JSON must contain an object")
    return ReuseComparison.from_mapping(source)
