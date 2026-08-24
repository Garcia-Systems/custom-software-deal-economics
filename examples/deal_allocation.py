#!/usr/bin/env python3
"""Run the editable Chapter 4 three-party allocation experiment."""

from __future__ import annotations

import argparse
import sys
from dataclasses import replace
from decimal import Decimal, InvalidOperation
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from deal_economics import (  # noqa: E402
    EngagementEconomics,
    ScenarioValidationError,
    SolutionsEffort,
    load_engagement_economics,
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
    parser = argparse.ArgumentParser(description="Explore fictional engagement economics")
    parser.add_argument(
        "--scenario-file",
        type=Path,
        default=ROOT / "data" / "james_river_kitchen_allocation.json",
    )
    for option in (
        "annual-customer-value",
        "customer-price",
        "engineering-cost",
        "partner-modeled-cost",
        "other-direct-costs",
        "solutions-hours",
    ):
        parser.add_argument(f"--{option}", type=decimal_argument)
    return parser.parse_args()


def apply_overrides(
    scenario: EngagementEconomics, args: argparse.Namespace
) -> EngagementEconomics:
    mappings = {
        "annual_customer_value": args.annual_customer_value,
        "customer_price": args.customer_price,
        "engineering_delivery_cost": args.engineering_cost,
        "partner_modeled_delivery_cost": args.partner_modeled_cost,
        "other_direct_costs": args.other_direct_costs,
    }
    changes = {name: value for name, value in mappings.items() if value is not None}
    if args.solutions_hours is not None:
        changes["solutions_effort"] = (
            SolutionsEffort("Total solutions effort (override)", args.solutions_hours),
        )
    return replace(scenario, **changes)


def currency(value: Decimal) -> str:
    sign = "-" if value < 0 else ""
    return f"{sign}${abs(value):,.2f}"


def percentage(value: Decimal | None) -> str:
    return "undefined (zero price)" if value is None else f"{value * 100:.2f}%"


def print_summary(scenario: EngagementEconomics) -> None:
    hourly = scenario.effective_contribution_per_solutions_hour
    print(f"{scenario.scenario} — Fictional Engagement Economics\n")
    print("CUSTOMER\n")
    print(f"Potential annual value:          {currency(scenario.annual_customer_value):>12}")
    print(f"Project price:                   {currency(scenario.customer_price):>12}")
    print(f"Potential net benefit:           {currency(scenario.customer_net_benefit):>12}")
    print(f"ROI:                             {percentage(scenario.customer_roi):>12}\n")
    print("GARCIA SYSTEMS / SOLUTIONS LAYER\n")
    print(f"Customer revenue:                {currency(scenario.customer_revenue):>12}")
    print(f"Engineering partner payment:     {currency(scenario.engineering_delivery_cost):>12}")
    print(f"Other direct costs:              {currency(scenario.other_direct_costs):>12}")
    print(f"Gross contribution:              {currency(scenario.gross_contribution):>12}")
    print("                              (before indirect company overhead)\n")
    print(f"Solutions effort:                {scenario.solutions_hours:>12.2f} hours")
    hourly_text = "undefined (zero hours)" if hourly is None else currency(hourly)
    print(f"Effective contribution/hour:     {hourly_text:>12}\n")
    print("ENGINEERING PARTNER\n")
    print(f"Delivery allocation / revenue:   {currency(scenario.engineering_partner_revenue):>12}")
    print(f"Modeled internal delivery cost:  {currency(scenario.partner_modeled_delivery_cost):>12}")
    print(f"Partner contribution:            {currency(scenario.engineering_partner_contribution):>12}")
    delivery_status = "WITHIN MODEL" if scenario.delivery_budget_sustainable else "NOT SUSTAINABLE"
    print("\nTHREE-PARTY CONDITIONS\n")
    print(f"CUSTOMER ECONOMICS:              {'POSITIVE' if scenario.customer_net_benefit > 0 else 'NON-POSITIVE'}")
    print(f"SOLUTIONS ECONOMICS:             {'POSITIVE' if scenario.gross_contribution > 0 else 'NON-POSITIVE'}")
    print(f"DELIVERY ECONOMICS:              {delivery_status}")
    print("\nThese signs expose assumptions; they do not label the deal good or set a threshold.")
    print("\nAll figures are fictional assumptions for educational modeling.")
    print("They are not real restaurant economics, engineering quotes,")
    print("compensation data, or market-rate claims.")


def main() -> int:
    args = parse_args()
    try:
        print_summary(apply_overrides(load_engagement_economics(args.scenario_file), args))
    except (OSError, ScenarioValidationError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
