import json
from copy import deepcopy
from dataclasses import replace
from decimal import Decimal
from pathlib import Path

import pytest

from deal_economics import (
    ReuseComparison,
    ReuseScenario,
    ScenarioValidationError,
    load_reuse_comparison,
)

DATA_FILE = Path(__file__).parents[1] / "data" / "james_river_kitchen_reuse.json"


@pytest.fixture
def comparison() -> ReuseComparison:
    return load_reuse_comparison(DATA_FILE)


@pytest.fixture
def reusable(comparison: ReuseComparison) -> ReuseScenario:
    return comparison.reusable_foundation


def test_scale_calculations(reusable: ReuseScenario) -> None:
    point = reusable.at(10)
    assert point.revenue == Decimal("80000.00")
    assert point.customer_specific_delivery_cost == Decimal("30000.00")
    assert point.total_cost == Decimal("55000.00")
    assert point.cumulative_contribution == Decimal("25000.00")
    assert point.foundation_remaining == Decimal("0")


def test_zero_customer_economics(reusable: ReuseScenario) -> None:
    point = reusable.at(0)
    assert point.revenue == 0
    assert point.customer_specific_delivery_cost == 0
    assert point.total_cost == Decimal("25000.00")
    assert point.cumulative_contribution == Decimal("-25000.00")
    assert point.foundation_remaining == Decimal("25000.00")


def test_break_even_uses_non_negative_contribution_boundary(reusable: ReuseScenario) -> None:
    assert reusable.break_even_customer == 5
    assert reusable.cumulative_contribution_at(4) == Decimal("-5000.00")
    assert reusable.cumulative_contribution_at(5) == Decimal("0.00")


def test_break_even_uses_ceiling_for_non_exact_boundary() -> None:
    scenario = ReuseScenario(Decimal("25001"), Decimal("8000"), Decimal("3000"))
    assert scenario.break_even_customer == 6


@pytest.mark.parametrize("cost", ["8000", "9000"])
def test_non_positive_per_customer_contribution_has_no_break_even(cost: str) -> None:
    scenario = ReuseScenario(Decimal("25000"), Decimal("8000"), Decimal(cost))
    assert scenario.break_even_customer is None


def test_larger_foundation_does_not_improve_break_even(reusable: ReuseScenario) -> None:
    larger = replace(reusable, foundation_investment=Decimal("50000"))
    assert larger.break_even_customer >= reusable.break_even_customer


def test_lower_marginal_cost_improves_contribution(reusable: ReuseScenario) -> None:
    lower = replace(reusable, delivery_cost_per_customer=Decimal("2000"))
    assert lower.cumulative_contribution_at(10) > reusable.cumulative_contribution_at(10)


def test_known_comparison_checkpoints(comparison: ReuseComparison) -> None:
    assert comparison.stronger_at(1) == "custom every time"
    assert comparison.stronger_at(5) == "custom every time"
    assert comparison.stronger_at(10) == "reusable foundation"
    assert comparison.crossover_customer == 9


def test_no_crossover_without_marginal_advantage(comparison: ReuseComparison) -> None:
    no_advantage = replace(
        comparison,
        reusable_foundation=replace(
            comparison.reusable_foundation,
            delivery_cost_per_customer=Decimal("6000"),
        ),
    )
    assert no_advantage.crossover_customer is None


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("foundation_investment", Decimal("-1")),
        ("implementation_price", Decimal("-1")),
        ("delivery_cost_per_customer", Decimal("-1")),
    ],
)
def test_negative_money_is_rejected(
    reusable: ReuseScenario, field: str, value: Decimal
) -> None:
    with pytest.raises(ScenarioValidationError, match="cannot be negative"):
        replace(reusable, **{field: value})


def test_negative_customer_count_is_rejected(reusable: ReuseScenario) -> None:
    with pytest.raises(ScenarioValidationError, match="cannot be negative"):
        reusable.at(-1)


def test_non_integer_customer_count_is_rejected(reusable: ReuseScenario) -> None:
    with pytest.raises(ScenarioValidationError, match="must be an integer"):
        reusable.at(Decimal("1"))  # type: ignore[arg-type]


def test_source_scenario_data_is_not_mutated() -> None:
    source = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    original = deepcopy(source)
    comparison = ReuseComparison.from_mapping(source)
    _ = comparison.reusable_foundation.at(25)
    _ = comparison.crossover_customer
    assert source == original
