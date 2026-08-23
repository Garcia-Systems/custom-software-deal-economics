#!/usr/bin/env python3
"""Run the editable Chapter 0 James River Kitchen experiment."""

from __future__ import annotations

import argparse
import sys
from dataclasses import replace
from decimal import Decimal, InvalidOperation
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from deal_economics import DealScenario, ScenarioValidationError, load_scenario  # noqa: E402


def decimal_argument(value: str) -> Decimal:
    try:
        amount = Decimal(value)
    except InvalidOperation as exc:
        raise argparse.ArgumentTypeError(f"not a decimal amount: {value}") from exc
    if not amount.is_finite() or amount < 0:
        raise argparse.ArgumentTypeError("amount must be a finite, non-negative decimal")
    return amount


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Explore a fictional three-party deal")
    parser.add_argument(
        "--scenario-file",
        type=Path,
        default=ROOT / "data" / "james_river_kitchen.json",
        help="JSON assumptions file",
    )
    for option in (
        "current-state-cost",
        "recoverable-value",
        "customer-price",
        "engineering-cost",
        "other-direct-costs",
    ):
        parser.add_argument(f"--{option}", type=decimal_argument)
    return parser.parse_args()


def apply_overrides(scenario: DealScenario, args: argparse.Namespace) -> DealScenario:
    changes = {
        field: value
        for field in (
            "current_state_cost",
            "recoverable_value",
            "customer_price",
            "engineering_cost",
            "other_direct_costs",
        )
        if (value := getattr(args, field)) is not None
    }
    return replace(scenario, **changes)


def currency(value: Decimal) -> str:
    return f"${value:,.2f}"


def percentage(value: Decimal | None) -> str:
    return "undefined (zero investment/revenue)" if value is None else f"{value * 100:.2f}%"


def print_summary(scenario: DealScenario) -> None:
    payback = scenario.approximate_payback_months
    print(f"{scenario.scenario} — Fictional Deal Scenario\n")
    print("CUSTOMER")
    print(f"Current-state burden:              {currency(scenario.current_state_cost)}")
    print(f"Potential recoverable value:       {currency(scenario.customer_first_year_benefit)}")
    print(f"Project price:                     {currency(scenario.customer_price)}")
    print(f"Potential first-year net benefit:  {currency(scenario.customer_first_year_net_benefit)}")
    print(f"ROI:                               {percentage(scenario.customer_roi)}")
    print(f"Approximate payback:               {'no payback (zero benefit)' if payback is None else f'{payback:.2f} months'}")
    print("\nSOLUTIONS ORGANIZATION / DEAL")
    print(f"Customer revenue:                  {currency(scenario.revenue)}")
    print(f"Engineering delivery cost:         {currency(scenario.engineering_cost)}")
    print(f"Other direct costs:                {currency(scenario.other_direct_costs)}")
    print(f"Total direct costs:                {currency(scenario.total_direct_costs)}")
    print(f"Gross contribution:                {currency(scenario.gross_contribution)}")
    print(f"Gross margin:                      {percentage(scenario.gross_margin)}")
    print("\nENGINEERING PARTNER")
    print(f"Illustrative delivery allocation:  {currency(scenario.engineering_cost)}")
    print("\nAll figures are fictional assumptions for educational modeling.")
    print("They are not restaurant financial data, engineering quotes, or market-rate claims.")
    print("Gross contribution is before indirect overhead, taxes, and other business expenses.")


def main() -> int:
    args = parse_args()
    try:
        print_summary(apply_overrides(load_scenario(args.scenario_file), args))
    except (OSError, ScenarioValidationError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

