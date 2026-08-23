#!/usr/bin/env python3
"""Run the editable Chapter 2 James River Kitchen pricing assessment."""

from __future__ import annotations

import argparse
import sys
from dataclasses import replace
from decimal import Decimal, InvalidOperation
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from deal_economics import PricingScenario, ScenarioValidationError, load_pricing_scenario  # noqa: E402


def decimal_argument(value: str) -> Decimal:
    try:
        amount = Decimal(value)
    except InvalidOperation as exc:
        raise argparse.ArgumentTypeError(f"not a decimal amount: {value}") from exc
    if not amount.is_finite() or amount < 0:
        raise argparse.ArgumentTypeError("amount must be a finite, non-negative decimal")
    return amount


def positive_integer(value: str) -> int:
    try:
        years = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("years must be a positive integer") from exc
    if years <= 0:
        raise argparse.ArgumentTypeError("years must be a positive integer")
    return years


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Explore fictional customer pricing economics")
    parser.add_argument(
        "--scenario-file",
        type=Path,
        default=ROOT / "data" / "james_river_kitchen_pricing.json",
        help="editable JSON assumptions file",
    )
    parser.add_argument("--implementation-price", type=decimal_argument)
    parser.add_argument("--monthly-fee", type=decimal_argument)
    parser.add_argument("--annual-benefit", type=decimal_argument)
    parser.add_argument("--years", type=positive_integer)
    return parser.parse_args()


def apply_overrides(scenario: PricingScenario, args: argparse.Namespace) -> PricingScenario:
    changes = {}
    for argument, field in (
        ("implementation_price", "implementation_price"),
        ("monthly_fee", "monthly_recurring_fee"),
        ("annual_benefit", "annual_economic_benefit"),
        ("years", "analysis_years"),
    ):
        if (value := getattr(args, argument)) is not None:
            changes[field] = value
    return replace(scenario, **changes)


def currency(value: Decimal) -> str:
    return f"${value:,.2f}"


def percentage(value: Decimal | None) -> str:
    return "undefined" if value is None else f"{value * 100:.2f}%"


def payback(value: Decimal | None) -> str:
    return "no payback" if value is None else f"{value:.2f} months"


def print_comparison(scenario: PricingScenario) -> None:
    print("\nPRICE COMPARISON — SAME FICTIONAL CUSTOMER VALUE (FIRST YEAR)\n")
    print(f"{'Price':>12} {'First-year cost':>18} {'Annual benefit':>18} "
          f"{'Net benefit':>16} {'ROI':>12} {'Payback':>16} {'Positive?':>11}")
    for price in map(Decimal, ("3000", "8000", "15000", "25000")):
        comparison = replace(scenario, implementation_price=price, analysis_years=1)
        print(
            f"{currency(price):>12} {currency(comparison.first_year_customer_cost):>18} "
            f"{currency(comparison.annual_economic_benefit):>18} "
            f"{currency(comparison.first_year_net_benefit):>16} "
            f"{percentage(comparison.roi):>12} {payback(comparison.payback_months):>16} "
            f"{('yes' if comparison.first_year_economics_positive else 'no'):>11}"
        )


def print_summary(scenario: PricingScenario) -> None:
    print(f"{scenario.scenario} — Fictional Pricing Assessment")
    print("This educational pricing model is not a real customer quote.\n")
    print(f"Annual economic benefit:          {currency(scenario.annual_economic_benefit)}")
    print(f"Implementation price:             {currency(scenario.implementation_price)}")
    print(f"Monthly recurring fee:            {currency(scenario.monthly_recurring_fee)}")
    print(f"Analysis horizon:                 {scenario.analysis_years} year(s)\n")
    print("FIRST-YEAR ECONOMICS\n")
    print(f"Customer cost:                    {currency(scenario.first_year_customer_cost)}")
    print(f"Economic benefit:                 {currency(scenario.annual_economic_benefit)}")
    print(f"Net benefit:                      {currency(scenario.first_year_net_benefit)}")
    first_year = replace(scenario, analysis_years=1)
    print(f"ROI:                              {percentage(first_year.roi)}")
    print(f"Monthly gross economic benefit:   {currency(scenario.monthly_economic_benefit)}")
    print(f"Monthly net economic benefit:     {currency(scenario.monthly_net_economic_benefit)}")
    print(f"Approximate payback:              {payback(scenario.payback_months)}")
    if scenario.analysis_years != 1:
        print(f"\n{scenario.analysis_years}-YEAR ECONOMICS\n")
        print(f"Total customer cost:              {currency(scenario.total_customer_cost)}")
        print(f"Total economic benefit:           {currency(scenario.total_benefit)}")
        print(f"Net customer benefit:             {currency(scenario.net_benefit)}")
        print(f"ROI:                              {percentage(scenario.roi)}")
    print_comparison(scenario)
    print("\nA lower price is not automatically the best option, and custom software is not")
    print("automatically preferable to doing nothing, SaaS, process change, or small automation.")
    print("All figures are fictional assumptions, not restaurant data or market-rate claims.")


def main() -> int:
    args = parse_args()
    try:
        print_summary(apply_overrides(load_pricing_scenario(args.scenario_file), args))
    except (OSError, ScenarioValidationError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
