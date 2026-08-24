#!/usr/bin/env python3
"""Compare Chapter 5's fictional custom and reusable delivery approaches."""

from __future__ import annotations

import argparse
import sys
from dataclasses import replace
from decimal import Decimal, InvalidOperation
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from deal_economics import (  # noqa: E402
    ReuseComparison,
    ReuseScenario,
    ScenarioValidationError,
    load_reuse_comparison,
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
    parser = argparse.ArgumentParser(description="Explore fictional reuse economics")
    parser.add_argument(
        "--scenario-file",
        type=Path,
        default=ROOT / "data" / "james_river_kitchen_reuse.json",
    )
    parser.add_argument("--foundation-investment", type=decimal_argument)
    parser.add_argument("--price-per-customer", type=decimal_argument)
    parser.add_argument("--delivery-cost-per-customer", type=decimal_argument)
    return parser.parse_args()


def apply_overrides(comparison: ReuseComparison, args: argparse.Namespace) -> ReuseComparison:
    reusable = comparison.reusable_foundation
    changes = {
        name: value
        for name, value in {
            "foundation_investment": args.foundation_investment,
            "implementation_price": args.price_per_customer,
            "delivery_cost_per_customer": args.delivery_cost_per_customer,
        }.items()
        if value is not None
    }
    return replace(comparison, reusable_foundation=replace(reusable, **changes))


def currency(value: Decimal) -> str:
    sign = "-" if value < 0 else ""
    return f"{sign}${abs(value):,.2f}"


def print_scenario(title: str, scenario: ReuseScenario, counts: tuple[int, ...]) -> None:
    print(title)
    print(f"Price/customer:          {currency(scenario.implementation_price):>14}")
    print(f"Delivery/customer:       {currency(scenario.delivery_cost_per_customer):>14}")
    print(f"Foundation investment:   {currency(scenario.foundation_investment):>14}")
    break_even = scenario.break_even_customer
    break_even_text = (
        str(break_even) if break_even is not None else "no break-even under modeled assumptions"
    )
    print(f"Break-even customer:      {break_even_text}\n")
    print("Customers | Revenue       | Marginal delivery | Foundation     | Total cost     | Contribution   | Foundation left")
    for count in counts:
        point = scenario.at(count)
        print(
            f"{count:>9} | {currency(point.revenue):>13} | "
            f"{currency(point.customer_specific_delivery_cost):>17} | "
            f"{currency(point.foundation_investment):>14} | "
            f"{currency(point.total_cost):>14} | "
            f"{currency(point.cumulative_contribution):>14} | "
            f"{currency(point.foundation_remaining):>15}"
        )
    print()


def print_summary(comparison: ReuseComparison) -> None:
    print("James River Kitchen — Fictional Reuse Economics\n")
    print_scenario(
        "SCENARIO A — CUSTOM EVERY TIME\n", comparison.custom_every_time, comparison.customer_counts
    )
    print_scenario(
        "SCENARIO B — REUSABLE FOUNDATION\n",
        comparison.reusable_foundation,
        comparison.customer_counts,
    )
    crossover = comparison.crossover_customer
    crossover_text = str(crossover) if crossover is not None else "no crossover under modeled assumptions"
    print(f"Strict crossover customer (reuse becomes stronger): {crossover_text}\n")
    print("CHECKPOINT COMPARISON")
    for count in comparison.customer_counts:
        print(f"{count:>3} customer(s): {comparison.stronger_at(count)}")
    print("\nContribution means cumulative implementation revenue minus modeled foundation")
    print("and customer-specific delivery cost, before other overhead—not net profit.")
    print("All figures are fictional learning assumptions, not estimates or quotes.")
    print("This structural model excludes recurring revenue and cash-flow timing.")


def main() -> int:
    args = parse_args()
    try:
        comparison = apply_overrides(load_reuse_comparison(args.scenario_file), args)
        print_summary(comparison)
    except (OSError, ScenarioValidationError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
