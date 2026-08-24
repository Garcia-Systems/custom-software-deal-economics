#!/usr/bin/env python3
"""Run the editable Chapter 3 James River Kitchen delivery-cost model."""

from __future__ import annotations

import argparse
import sys
from dataclasses import replace
from decimal import Decimal, InvalidOperation
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from deal_economics import DeliveryScenario, LaborComponent, ScenarioValidationError, load_delivery_scenario  # noqa: E402


def decimal_argument(value: str) -> Decimal:
    try:
        amount = Decimal(value)
    except InvalidOperation as exc:
        raise argparse.ArgumentTypeError(f"not a decimal amount: {value}") from exc
    if not amount.is_finite() or amount < 0:
        raise argparse.ArgumentTypeError("value must be a finite, non-negative decimal")
    return amount


def positive_decimal(value: str) -> Decimal:
    amount = decimal_argument(value)
    if amount == 0:
        raise argparse.ArgumentTypeError("elapsed weeks must be positive")
    return amount


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Explore fictional delivery-cost assumptions")
    parser.add_argument(
        "--scenario-file", type=Path,
        default=ROOT / "data" / "james_river_kitchen_delivery.json",
        help="editable JSON assumptions file",
    )
    parser.add_argument("--engineering-hours", type=decimal_argument)
    parser.add_argument("--engineering-rate", type=decimal_argument)
    parser.add_argument("--qa-hours", type=decimal_argument)
    parser.add_argument("--qa-rate", type=decimal_argument)
    parser.add_argument("--deployment-hours", type=decimal_argument)
    parser.add_argument("--rework-reserve", type=decimal_argument)
    parser.add_argument("--delivery-budget", type=decimal_argument)
    parser.add_argument("--elapsed-weeks", type=positive_decimal)
    return parser.parse_args()


def apply_overrides(scenario: DeliveryScenario, args: argparse.Namespace) -> DeliveryScenario:
    labor_changes = {
        "Engineering": (args.engineering_hours, args.engineering_rate),
        "QA": (args.qa_hours, args.qa_rate),
        "Deployment / DevOps": (args.deployment_hours, None),
    }
    changed_labor = []
    for component in scenario.labor:
        hours, rate = labor_changes.get(component.name, (None, None))
        changed_labor.append(
            replace(
                component,
                hours=hours if hours is not None else component.hours,
                hourly_rate=rate if rate is not None else component.hourly_rate,
            )
        )
    labor = tuple(changed_labor)
    changes = {"labor": labor}
    for name in ("rework_reserve", "delivery_budget", "elapsed_weeks"):
        if (value := getattr(args, name)) is not None:
            changes[name] = value
    return replace(scenario, **changes)


def currency(value: Decimal) -> str:
    sign = "-" if value < 0 else ""
    return f"{sign}${abs(value):,.2f}"


def print_summary(scenario: DeliveryScenario) -> None:
    print(f"{scenario.scenario} — Fictional Delivery Cost Model\n")
    print("All figures are fictional educational assumptions.")
    print("They are not engineering quotes, compensation data, or market-rate claims.\n")
    print("DELIVERY EFFORT\n")
    for component in scenario.labor:
        print(component.name)
        print(
            f"{component.hours:.2f} hours × {currency(component.hourly_rate)}/hour "
            f"= {currency(component.cost)}\n"
        )
    print(f"Rework reserve:                 {currency(scenario.rework_reserve):>12}")
    print(f"TOTAL ACTIVE LABOR HOURS:       {scenario.active_labor_hours:>12.2f}\n")
    print(f"MODELED DELIVERY COST:          {currency(scenario.total_delivery_cost):>12}")
    print(f"DELIVERY BUDGET:                {currency(scenario.delivery_budget):>12}")
    print(f"BUDGET VARIANCE:                {currency(scenario.budget_variance):>12}")
    status = "under budget" if scenario.budget_variance > 0 else "over budget" if scenario.budget_variance < 0 else "exactly at budget"
    print(f"STATUS:                         {status:>12}\n")
    print(f"ELAPSED PROJECT DURATION:       {scenario.elapsed_weeks:g} weeks\n")
    full_time_hours = scenario.elapsed_weeks * Decimal("40")
    print(
        f"{scenario.active_labor_hours:g} active delivery hours spread across "
        f"{scenario.elapsed_weeks:g} elapsed weeks"
    )
    print(f"does not mean {full_time_hours:g} engineering hours.")
    print("Duration and effort are separate; changing elapsed weeks alone does not change cost.")


def main() -> int:
    args = parse_args()
    try:
        scenario = apply_overrides(load_delivery_scenario(args.scenario_file), args)
        print_summary(scenario)
    except (OSError, ScenarioValidationError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
