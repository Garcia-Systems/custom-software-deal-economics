#!/usr/bin/env python3
"""Run the editable Chapter 1 James River Kitchen value assessment."""

from __future__ import annotations

import argparse
import sys
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from deal_economics import ScenarioValidationError, ValueAssessment, load_value_assessment  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Decompose a fictional business burden")
    parser.add_argument(
        "--scenario-file",
        type=Path,
        default=ROOT / "data" / "james_river_kitchen_value.json",
        help="editable JSON assumptions file",
    )
    return parser.parse_args()


def currency(value: Decimal) -> str:
    return f"${value:,.2f}"


def print_summary(assessment: ValueAssessment) -> None:
    print(f"{assessment.scenario} — Fictional Business Value Assessment")
    print("All figures and improvement rates are fictional, editable educational assumptions.")
    print("They are not restaurant data, financial advice, or industry benchmarks.\n")
    print("CURRENT-STATE BURDEN\n")
    for component in assessment.components:
        print(component.name)
        print(f"  Assumption:                  {component.description}")
        print(f"  Annual burden:              {currency(component.current_state_cost)}")
        print(f"  Expected improvement:       {component.improvement_rate * 100:.1f}%")
        print(f"  Potential recoverable value:{currency(component.recoverable_value):>15}\n")
    print("TOTAL")
    print(f"  Current-state economic burden: {currency(assessment.total_current_state_cost)}")
    print(f"  Potential recoverable value:   {currency(assessment.total_recoverable_value)}")
    print(f"  Unrecovered burden:             {currency(assessment.unrecovered_burden)}")
    print("\nCurrent-state cost is not software value; recovery depends on visible assumptions.")
    print("Edit data/james_river_kitchen_value.json, rerun, and observe the result.")


def main() -> int:
    args = parse_args()
    try:
        print_summary(load_value_assessment(args.scenario_file))
    except (OSError, ScenarioValidationError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
