#!/usr/bin/env python3
"""Explore Chapter 6's fictional recurring economics and support workload."""

from __future__ import annotations

import argparse
import sys
from dataclasses import replace
from decimal import Decimal, InvalidOperation
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from deal_economics import (  # noqa: E402
    RecurringScenario,
    ScenarioValidationError,
    load_recurring_scenario,
)


def decimal_argument(value: str) -> Decimal:
    try:
        amount = Decimal(value)
    except InvalidOperation as exc:
        raise argparse.ArgumentTypeError(f"not a decimal amount: {value}") from exc
    if not amount.is_finite() or amount < 0:
        raise argparse.ArgumentTypeError("value must be a finite, non-negative decimal")
    return amount


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Explore fictional recurring economics")
    parser.add_argument("--scenario-file", type=Path, default=ROOT / "data" / "james_river_kitchen_recurring.json")
    parser.add_argument("--monthly-fee", type=decimal_argument)
    parser.add_argument("--support-hours-per-customer", type=decimal_argument)
    parser.add_argument("--support-rate", type=decimal_argument)
    parser.add_argument("--support-capacity", type=decimal_argument)
    return parser.parse_args()


def apply_overrides(scenario: RecurringScenario, args: argparse.Namespace) -> RecurringScenario:
    changes = {
        name: value
        for name, value in {
            "monthly_fee_per_customer": args.monthly_fee,
            "support_hours_per_customer": args.support_hours_per_customer,
            "support_hourly_cost": args.support_rate,
            "available_support_hours_per_month": args.support_capacity,
        }.items()
        if value is not None
    }
    return replace(scenario, **changes)


def currency(value: Decimal) -> str:
    sign = "-" if value < 0 else ""
    return f"{sign}${abs(value):,.2f}"


def print_summary(scenario: RecurringScenario) -> None:
    one = scenario.at(1)
    print("James River Kitchen — Fictional Recurring Economics")
    print("FICTIONAL EDUCATIONAL ASSUMPTIONS — NOT RATES, BENCHMARKS, OR A QUOTE\n")
    print("MONTHLY MODEL PER CUSTOMER\n")
    print(f"Managed service fee:           {currency(scenario.monthly_fee_per_customer)}")
    print(f"Hosting:                       {currency(scenario.hosting_per_customer)}")
    print(f"Monitoring:                    {currency(scenario.monitoring_per_customer)}")
    print(f"Support labor:                 {currency(scenario.support_labor_cost_per_customer)}")
    print(f"Total recurring direct cost:  {currency(scenario.direct_recurring_cost_per_customer)}")
    print(f"Recurring gross contribution: {currency(scenario.recurring_gross_contribution_per_customer)}")
    print(f"Support effort:                {scenario.support_hours_per_customer:.2f} hours/month")
    maximum = scenario.maximum_customers_within_support_capacity
    maximum_text = "unbounded at zero modeled hours/customer" if maximum is None else str(maximum)
    print(f"Current capacity threshold:    {maximum_text} customers\n")
    print("SCALE")
    print("Customers | MRR | ARR | Monthly Cost | Monthly Contribution | Annual Contribution | Support Hours | Utilization | Capacity")
    for count in scenario.customer_counts:
        point = scenario.at(count)
        utilization = (
            "unbounded" if point.support_capacity_utilization.is_infinite()
            else f"{point.support_capacity_utilization:.1%}"
        )
        capacity = "EXCEEDED" if point.support_capacity_exceeded else "within"
        print(
            f"{count:>9} | {currency(point.mrr):>10} | {currency(point.arr):>11} | "
            f"{currency(point.monthly_direct_recurring_cost):>12} | "
            f"{currency(point.monthly_recurring_gross_contribution):>20} | "
            f"{currency(point.annual_recurring_gross_contribution):>19} | "
            f"{point.monthly_support_hours:>13.2f} | {utilization:>11} | {capacity}"
        )
    print("\nImplementation revenue remains separate: the implementation price is")
    print(f"{currency(scenario.implementation_price)} once per customer; it is never included in ARR.")
    print("Gross contribution is before indirect overhead and broader expenses—not profit.")
    print("Support hours are a linear average; incidents can create non-linear spikes.")
    if one.monthly_recurring_gross_contribution <= 0:
        print("WARNING: contribution/customer is non-positive; adding customers compounds it.")


def main() -> int:
    args = parse_args()
    try:
        print_summary(apply_overrides(load_recurring_scenario(args.scenario_file), args))
    except (OSError, ScenarioValidationError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
