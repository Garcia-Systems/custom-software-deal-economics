"""Chapter 6's recurring revenue, direct-cost, and support-capacity model."""

from __future__ import annotations

import json
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation, ROUND_FLOOR
from pathlib import Path
from typing import Any, Mapping, Sequence

from .deal import ScenarioValidationError


def _non_negative_decimal(name: str, value: Decimal) -> None:
    if not isinstance(value, Decimal) or not value.is_finite():
        raise ScenarioValidationError(f"{name} must be a finite Decimal")
    if value < 0:
        raise ScenarioValidationError(f"{name} cannot be negative")


def _customer_count(customers: int) -> None:
    if isinstance(customers, bool) or not isinstance(customers, int):
        raise ScenarioValidationError("customer count must be an integer")
    if customers < 0:
        raise ScenarioValidationError("customer count cannot be negative")


@dataclass(frozen=True)
class RecurringScalePoint:
    """Recurring economics and workload for one active-customer count."""

    customers: int
    mrr: Decimal
    arr: Decimal
    monthly_support_hours: Decimal
    monthly_support_labor_cost: Decimal
    monthly_direct_recurring_cost: Decimal
    monthly_recurring_gross_contribution: Decimal
    annual_recurring_gross_contribution: Decimal
    recurring_gross_margin: Decimal | None
    support_capacity_utilization: Decimal
    support_capacity_exceeded: bool


@dataclass(frozen=True)
class RecurringScenario:
    """Fictional per-customer recurring assumptions and monthly support capacity.

    Support labor is calculated from hours and rate and is not included in either
    hosting or monitoring, preventing it from being counted twice.

    Capacity utilization is zero when capacity and required hours are both zero;
    with required work and zero capacity it is represented as ``Infinity``.
    """

    scenario: str
    fictional: bool
    implementation_price: Decimal
    monthly_fee_per_customer: Decimal
    hosting_per_customer: Decimal
    monitoring_per_customer: Decimal
    support_hours_per_customer: Decimal
    support_hourly_cost: Decimal
    available_support_hours_per_month: Decimal
    customer_counts: tuple[int, ...]

    def __post_init__(self) -> None:
        if not self.scenario.strip():
            raise ScenarioValidationError("scenario must have a name")
        if self.fictional is not True:
            raise ScenarioValidationError("Chapter 6 scenarios must be explicitly fictional")
        for name in (
            "implementation_price", "monthly_fee_per_customer", "hosting_per_customer",
            "monitoring_per_customer", "support_hours_per_customer", "support_hourly_cost",
            "available_support_hours_per_month",
        ):
            _non_negative_decimal(name, getattr(self, name))
        for count in self.customer_counts:
            _customer_count(count)

    @property
    def support_labor_cost_per_customer(self) -> Decimal:
        return self.support_hours_per_customer * self.support_hourly_cost

    @property
    def direct_recurring_cost_per_customer(self) -> Decimal:
        return (
            self.hosting_per_customer
            + self.monitoring_per_customer
            + self.support_labor_cost_per_customer
        )

    @property
    def recurring_gross_contribution_per_customer(self) -> Decimal:
        return self.monthly_fee_per_customer - self.direct_recurring_cost_per_customer

    @property
    def maximum_customers_within_support_capacity(self) -> int | None:
        """Maximum count at the modeled average, or None for zero hours/customer."""
        if self.support_hours_per_customer == 0:
            return None
        return int(
            (self.available_support_hours_per_month / self.support_hours_per_customer)
            .to_integral_value(rounding=ROUND_FLOOR)
        )

    def at(self, customers: int) -> RecurringScalePoint:
        _customer_count(customers)
        count = Decimal(customers)
        mrr = self.monthly_fee_per_customer * count
        support_hours = self.support_hours_per_customer * count
        support_labor = support_hours * self.support_hourly_cost
        direct_cost = (
            (self.hosting_per_customer + self.monitoring_per_customer) * count
            + support_labor
        )
        contribution = mrr - direct_cost
        if mrr == 0:
            margin = None
        else:
            margin = contribution / mrr
        if self.available_support_hours_per_month == 0:
            utilization = Decimal("0") if support_hours == 0 else Decimal("Infinity")
        else:
            utilization = support_hours / self.available_support_hours_per_month
        return RecurringScalePoint(
            customers, mrr, mrr * 12, support_hours, support_labor, direct_cost,
            contribution, contribution * 12, margin, utilization,
            support_hours > self.available_support_hours_per_month,
        )

    @classmethod
    def from_mapping(cls, source: Mapping[str, Any]) -> "RecurringScenario":
        try:
            raw_counts = source["customer_counts"]
            if not isinstance(raw_counts, Sequence) or isinstance(raw_counts, (str, bytes)):
                raise ScenarioValidationError("customer_counts must be a list")
            return cls(
                scenario=str(source["scenario"]), fictional=source["fictional"],
                implementation_price=Decimal(str(source["implementation_price"])),
                monthly_fee_per_customer=Decimal(str(source["monthly_fee_per_customer"])),
                hosting_per_customer=Decimal(str(source["hosting_per_customer"])),
                monitoring_per_customer=Decimal(str(source["monitoring_per_customer"])),
                support_hours_per_customer=Decimal(str(source["support_hours_per_customer"])),
                support_hourly_cost=Decimal(str(source["support_hourly_cost"])),
                available_support_hours_per_month=Decimal(
                    str(source["available_support_hours_per_month"])
                ),
                customer_counts=tuple(raw_counts),
            )
        except KeyError as exc:
            raise ScenarioValidationError(f"missing recurring field: {exc.args[0]}") from exc
        except (InvalidOperation, TypeError, ValueError) as exc:
            if isinstance(exc, ScenarioValidationError):
                raise
            raise ScenarioValidationError("recurring fields must contain valid numbers") from exc


def load_recurring_scenario(path: str | Path) -> RecurringScenario:
    with Path(path).open(encoding="utf-8") as scenario_file:
        source = json.load(scenario_file)
    if not isinstance(source, dict):
        raise ScenarioValidationError("scenario JSON must contain an object")
    return RecurringScenario.from_mapping(source)
