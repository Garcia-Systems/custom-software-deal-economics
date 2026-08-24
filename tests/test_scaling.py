import json
from copy import deepcopy
from dataclasses import replace
from decimal import Decimal
from pathlib import Path

import pytest

from deal_economics import (
    CapacityModel, CapstoneComparison, ScaleScenario, ScenarioValidationError,
    load_capstone_comparison,
)

DATA_FILE = Path(__file__).parents[1] / "data" / "james_river_kitchen_scaling.json"


@pytest.fixture
def comparison() -> CapstoneComparison:
    return load_capstone_comparison(DATA_FILE)


@pytest.fixture
def scenario(comparison: CapstoneComparison) -> ScaleScenario:
    return comparison.reusable_delivery


def test_customer_value_and_customer_economics_aggregate(scenario: ScaleScenario) -> None:
    point = scenario.at(25)
    assert point.total_annual_customer_value == Decimal("450000.00")
    assert point.total_customer_implementation_investment == Decimal("200000.00")
    assert point.total_annual_recurring_customer_cost == Decimal("105000.00")
    assert point.aggregate_first_year_customer_net_benefit == Decimal("145000.00")
    assert point.representative_first_year_customer_roi == Decimal("5800") / Decimal("12200")


def test_implementation_reuses_chapter_five_model(scenario: ScaleScenario) -> None:
    point = scenario.at(10).implementation
    assert point.revenue == Decimal("80000.00")
    assert point.customer_specific_delivery_cost == Decimal("30000.00")
    assert point.foundation_investment == Decimal("25000.00")
    assert point.cumulative_contribution == Decimal("25000.00")
    assert scenario.implementation.break_even_customer == 5
    assert scenario.at(5).platform_recovered is True


def test_recurring_reuses_chapter_six_model(scenario: ScaleScenario) -> None:
    point = scenario.at(10).recurring
    assert point.mrr == Decimal("3500.00")
    assert point.arr == Decimal("42000.00")
    assert point.monthly_direct_recurring_cost == Decimal("1500.0000")
    assert point.monthly_recurring_gross_contribution == Decimal("2000.0000")
    assert point.annual_recurring_gross_contribution == Decimal("24000.0000")


def test_workloads_scale_independently(scenario: ScaleScenario) -> None:
    point = scenario.at(10)
    assert point.solutions_capacity.required_hours == Decimal("450.00")
    assert point.implementation_capacity.required_hours == Decimal("930.00")
    assert point.recurring.monthly_support_hours == Decimal("7.50")


def test_capacity_utilization_and_flags(scenario: ScaleScenario) -> None:
    point = scenario.at(25)
    assert point.solutions_capacity.utilization == Decimal("0.75")
    assert point.implementation_capacity.utilization == Decimal("1.1625")
    assert point.recurring.support_capacity_utilization == Decimal("0.234375")
    assert point.solutions_capacity.exceeded is False
    assert point.implementation_capacity.exceeded is True
    assert point.recurring.support_capacity_exceeded is False


def test_first_capacity_breaks_and_first_bottleneck(scenario: ScaleScenario) -> None:
    assert scenario.first_exceeded("solutions capacity") == 50
    assert scenario.first_exceeded("implementation capacity") == 25
    assert scenario.first_exceeded("support capacity") is None
    assert scenario.first_modeled_bottleneck == (25, ("implementation capacity",))


def test_tied_bottlenecks_are_reported_together(scenario: ScaleScenario) -> None:
    tied = replace(
        scenario,
        capacity=replace(scenario.capacity, annual_solutions_hours=Decimal("1000")),
        recurring=replace(scenario.recurring, available_support_hours_per_month=Decimal("18")),
    )
    assert tied.first_modeled_bottleneck == (
        25, ("solutions capacity", "implementation capacity", "support capacity")
    )


def test_zero_customers_are_safe_and_timing_dimensions_stay_separate(scenario: ScaleScenario) -> None:
    point = scenario.at(0)
    assert point.total_annual_customer_value == 0
    assert point.implementation.revenue == point.recurring.arr == 0
    assert point.implementation.cumulative_contribution == Decimal("-25000.00")
    assert point.recurring.annual_recurring_gross_contribution == 0
    assert point.solutions_capacity.utilization == 0
    assert point.representative_first_year_customer_roi == Decimal("5800") / Decimal("12200")


def test_negative_customer_count_is_rejected(scenario: ScaleScenario) -> None:
    with pytest.raises(ScenarioValidationError, match="cannot be negative"):
        scenario.at(-1)


@pytest.mark.parametrize("field", [
    "solutions_hours_per_customer", "implementation_hours_per_customer",
    "annual_solutions_hours", "annual_implementation_hours",
])
def test_negative_capacity_inputs_are_rejected(scenario: ScaleScenario, field: str) -> None:
    with pytest.raises(ScenarioValidationError, match="cannot be negative"):
        replace(scenario.capacity, **{field: Decimal("-1")})


def test_custom_and_reusable_known_checkpoint(comparison: CapstoneComparison) -> None:
    custom = comparison.custom_every_time.at(10)
    reusable = comparison.reusable_delivery.at(10)
    assert custom.implementation.cumulative_contribution == Decimal("20000.00")
    assert custom.implementation_capacity.required_hours == Decimal("1600.00")
    assert reusable.implementation.cumulative_contribution == Decimal("25000.00")
    assert reusable.implementation_capacity.required_hours == Decimal("930.00")


def test_aggressive_growth_exposes_capacity_without_inventing_more(comparison: CapstoneComparison) -> None:
    point = comparison.reusable_delivery.at(comparison.aggressive_growth_target)
    assert comparison.aggressive_growth_target == 100
    assert point.implementation.revenue == Decimal("800000.00")
    assert point.recurring.arr == Decimal("420000.00")
    assert point.active_bottlenecks == ("solutions capacity", "implementation capacity")


def test_capacity_equivalents_use_ceiling(scenario: ScaleScenario) -> None:
    point = scenario.at(100)
    assert point.solutions_capacity.capacity_equivalents == 3
    assert point.implementation_capacity.capacity_equivalents == 5


def test_source_data_is_not_mutated() -> None:
    source = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    original = deepcopy(source)
    comparison = CapstoneComparison.from_mapping(source)
    _ = comparison.reusable_delivery.at(100)
    assert source == original


def test_zero_capacity_model_is_safe() -> None:
    model = CapacityModel(Decimal("1"), Decimal("1"), Decimal("0"), Decimal("0"))
    assert model.solutions_at(0).utilization == 0
    assert model.solutions_at(1).utilization == Decimal("Infinity")
    assert model.solutions_at(1).exceeded is True
