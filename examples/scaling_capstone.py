#!/usr/bin/env python3
"""Run Chapter 7's fictional economics-and-capacity capstone."""

from __future__ import annotations

import argparse
import sys
from dataclasses import replace
from decimal import Decimal, InvalidOperation
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from deal_economics import (  # noqa: E402
    CapstoneComparison, ScaleScenario, ScenarioValidationError,
    load_capstone_comparison,
)


def decimal_argument(value: str) -> Decimal:
    try:
        result = Decimal(value)
    except InvalidOperation as exc:
        raise argparse.ArgumentTypeError(f"not a decimal amount: {value}") from exc
    if not result.is_finite() or result < 0:
        raise argparse.ArgumentTypeError("value must be a finite, non-negative decimal")
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Explore fictional scaling economics")
    parser.add_argument("--scenario-file", type=Path,
                        default=ROOT / "data" / "james_river_kitchen_scaling.json")
    parser.add_argument("--solutions-capacity", type=decimal_argument)
    parser.add_argument("--engineering-capacity", type=decimal_argument)
    parser.add_argument("--support-capacity", type=decimal_argument)
    parser.add_argument("--annual-value-per-customer", type=decimal_argument)
    parser.add_argument("--price-per-customer", type=decimal_argument)
    return parser.parse_args()


def apply_overrides(comparison: CapstoneComparison, args: argparse.Namespace) -> CapstoneComparison:
    def update(scenario: ScaleScenario) -> ScaleScenario:
        capacity = replace(
            scenario.capacity,
            annual_solutions_hours=args.solutions_capacity
            if args.solutions_capacity is not None else scenario.capacity.annual_solutions_hours,
            annual_implementation_hours=args.engineering_capacity
            if args.engineering_capacity is not None else scenario.capacity.annual_implementation_hours,
        )
        recurring = replace(
            scenario.recurring,
            available_support_hours_per_month=args.support_capacity
            if args.support_capacity is not None else scenario.recurring.available_support_hours_per_month,
        )
        implementation = replace(
            scenario.implementation,
            implementation_price=args.price_per_customer
            if args.price_per_customer is not None else scenario.implementation.implementation_price,
        )
        recurring = replace(recurring, implementation_price=implementation.implementation_price)
        return replace(
            scenario, capacity=capacity, recurring=recurring, implementation=implementation,
            annual_value_per_customer=args.annual_value_per_customer
            if args.annual_value_per_customer is not None else scenario.annual_value_per_customer,
        )
    return replace(comparison, custom_every_time=update(comparison.custom_every_time),
                   reusable_delivery=update(comparison.reusable_delivery))


def money(value: Decimal) -> str:
    sign = "-" if value < 0 else ""
    return f"{sign}${abs(value):,.0f}"


def utilization(value: Decimal, exceeded: bool) -> str:
    percentage = "∞" if value.is_infinite() else f"{value:.0%}"
    return f"{percentage} {'EXCEEDED' if exceeded else 'within'}"


def print_scale(scenario: ScaleScenario) -> None:
    print("James River Kitchen — Fictional Scaling Capstone")
    print("FICTIONAL EDUCATIONAL ASSUMPTIONS — NOT A FORECAST, QUOTE, OR BENCHMARK")
    print("Identical-customer snapshot; all customers are treated as acquired in one modeled year.\n")
    print("ASSUMPTIONS")
    print(f"Value/customer/year: {money(scenario.annual_value_per_customer)} | "
          f"implementation price: {money(scenario.implementation.implementation_price)} | "
          f"managed service: {money(scenario.recurring.monthly_fee_per_customer)}/month")
    print(f"Foundation: {money(scenario.implementation.foundation_investment)} | "
          f"marginal delivery: {money(scenario.implementation.delivery_cost_per_customer)} | "
          f"solutions/customer: {scenario.capacity.solutions_hours_per_customer:g}h | "
          f"delivery/customer: {scenario.capacity.implementation_hours_per_customer:g}h\n")
    print("SCALE — implementation figures are cumulative; MRR/ARR and recurring contribution are recurring run-rate")
    print("Customers | Customer Value | Impl Revenue | MRR | ARR | Impl Contribution | Annual Recurring Contribution | Sol Hrs | Delivery Hrs | Support Hrs/mo")
    for count in scenario.customer_counts:
        point = scenario.at(count)
        print(f"{count:>9} | {money(point.total_annual_customer_value):>14} | "
              f"{money(point.implementation.revenue):>12} | {money(point.recurring.mrr):>8} | "
              f"{money(point.recurring.arr):>9} | {money(point.implementation.cumulative_contribution):>17} | "
              f"{money(point.recurring.annual_recurring_gross_contribution):>29} | "
              f"{point.solutions_capacity.required_hours:>7g} | "
              f"{point.implementation_capacity.required_hours:>12g} | "
              f"{point.recurring.monthly_support_hours:>14g}")
    print("\nCAPACITY AT EACH CHECKPOINT")
    for count in scenario.customer_counts:
        point = scenario.at(count)
        print(f"{count:>3}: solutions {utilization(point.solutions_capacity.utilization, point.solutions_capacity.exceeded)}; "
              f"implementation {utilization(point.implementation_capacity.utilization, point.implementation_capacity.exceeded)}; "
              f"support {utilization(point.recurring.support_capacity_utilization, point.recurring.support_capacity_exceeded)}; "
              f"platform {'recovered' if point.platform_recovered else 'not recovered'}")
    first = scenario.first_modeled_bottleneck
    print("\nFirst modeled bottleneck: " + (
        "none at listed checkpoints" if first is None else f"{', '.join(first[1])} at {first[0]} customers"
    ))


def print_comparison(comparison: CapstoneComparison) -> None:
    print("\nSCENARIO COMPARISON")
    print("Scenario A is custom every time; Scenario B is reusable delivery; Scenario C uses B at the aggressive target with unchanged capacity.")
    print("Scenario | Customers | Cumulative Impl Contribution | ARR | Active Capacity Constraints")
    cases = [
        ("A — Custom Every Time", comparison.custom_every_time, 10),
        ("A — Custom Every Time", comparison.custom_every_time, 25),
        ("B — Reusable Delivery", comparison.reusable_delivery, 10),
        ("B — Reusable Delivery", comparison.reusable_delivery, 25),
        ("C — Aggressive Growth", comparison.reusable_delivery, comparison.aggressive_growth_target),
    ]
    for name, scenario, count in cases:
        point = scenario.at(count)
        constraints = ", ".join(point.active_bottlenecks) or "none"
        print(f"{name:<23} | {count:>9} | {money(point.implementation.cumulative_contribution):>28} | "
              f"{money(point.recurring.arr):>8} | {constraints}")
    target = comparison.reusable_delivery.at(comparison.aggressive_growth_target)
    print(f"\nAt {target.customers} customers revenue looks substantial ({money(target.implementation.revenue)} cumulative implementation revenue and {money(target.recurring.arr)} ARR),")
    print("but revenue opportunity is not executable capacity when required work exceeds the modeled pools.")
    print("Contribution is before indirect overhead and is not net income. Cumulative implementation")
    print("contribution is not added to ARR as though the two covered the same time period.")
    print("The combined model is assumption-sensitive; extra digits would not make it more credible.")
    print("100 customers ≠ 100 identical businesses. Edit the JSON to experiment, not to forecast.")


def main() -> int:
    args = parse_args()
    try:
        comparison = apply_overrides(load_capstone_comparison(args.scenario_file), args)
        print_scale(comparison.reusable_delivery)
        print_comparison(comparison)
    except (OSError, ScenarioValidationError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
