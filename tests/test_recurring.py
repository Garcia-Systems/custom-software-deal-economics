import json
from copy import deepcopy
from dataclasses import replace
from decimal import Decimal
from pathlib import Path

import pytest

from deal_economics import RecurringScenario, ScenarioValidationError, load_recurring_scenario

DATA_FILE = Path(__file__).parents[1] / "data" / "james_river_kitchen_recurring.json"


@pytest.fixture
def scenario() -> RecurringScenario:
    return load_recurring_scenario(DATA_FILE)


def test_per_customer_cost_decomposition(scenario: RecurringScenario) -> None:
    assert scenario.support_labor_cost_per_customer == Decimal("90.0000")
    assert scenario.direct_recurring_cost_per_customer == Decimal("150.0000")
    assert scenario.recurring_gross_contribution_per_customer == Decimal("200.0000")


def test_ten_customer_recurring_economics(scenario: RecurringScenario) -> None:
    point = scenario.at(10)
    assert point.mrr == Decimal("3500.00")
    assert point.arr == Decimal("42000.00")
    assert point.monthly_support_hours == Decimal("7.50")
    assert point.monthly_support_labor_cost == Decimal("900.0000")
    assert point.monthly_direct_recurring_cost == Decimal("1500.0000")
    assert point.monthly_recurring_gross_contribution == Decimal("2000.0000")
    assert point.annual_recurring_gross_contribution == Decimal("24000.0000")
    assert point.recurring_gross_margin == Decimal("2000") / Decimal("3500")


def test_zero_customers_produce_zero_economics(scenario: RecurringScenario) -> None:
    point = scenario.at(0)
    assert point.mrr == point.arr == point.monthly_support_hours == 0
    assert point.monthly_support_labor_cost == point.monthly_direct_recurring_cost == 0
    assert point.monthly_recurring_gross_contribution == 0
    assert point.annual_recurring_gross_contribution == 0
    assert point.recurring_gross_margin is None
    assert point.support_capacity_utilization == 0
    assert point.support_capacity_exceeded is False


def test_zero_fee_does_not_divide_by_zero(scenario: RecurringScenario) -> None:
    point = replace(scenario, monthly_fee_per_customer=Decimal("0")).at(10)
    assert point.recurring_gross_margin is None
    assert point.monthly_recurring_gross_contribution == Decimal("-1500.0000")


def test_more_customers_increase_revenue_and_work(scenario: RecurringScenario) -> None:
    assert scenario.at(100).mrr > scenario.at(1).mrr
    assert scenario.at(100).monthly_support_hours > scenario.at(1).monthly_support_hours


def test_capacity_utilization_threshold_and_maximum(scenario: RecurringScenario) -> None:
    assert scenario.at(100).support_capacity_utilization == Decimal("0.9375")
    assert scenario.at(100).support_capacity_exceeded is False
    assert scenario.at(107).support_capacity_exceeded is True
    assert scenario.maximum_customers_within_support_capacity == 106


def test_positive_economics_can_exceed_operational_capacity(scenario: RecurringScenario) -> None:
    high_support = replace(scenario, support_hours_per_customer=Decimal("2"))
    point = high_support.at(50)
    assert point.monthly_recurring_gross_contribution > 0
    assert point.monthly_support_hours == 100
    assert point.support_capacity_exceeded is True


def test_zero_capacity_is_safe(scenario: RecurringScenario) -> None:
    no_capacity = replace(scenario, available_support_hours_per_month=Decimal("0"))
    assert no_capacity.at(0).support_capacity_utilization == 0
    assert no_capacity.at(0).support_capacity_exceeded is False
    assert no_capacity.at(1).support_capacity_utilization == Decimal("Infinity")
    assert no_capacity.at(1).support_capacity_exceeded is True
    assert no_capacity.maximum_customers_within_support_capacity == 0


def test_zero_support_effort_has_unbounded_customer_threshold(scenario: RecurringScenario) -> None:
    no_support = replace(scenario, support_hours_per_customer=Decimal("0"))
    assert no_support.maximum_customers_within_support_capacity is None


@pytest.mark.parametrize(
    "field",
    [
        "implementation_price", "monthly_fee_per_customer", "hosting_per_customer",
        "monitoring_per_customer", "support_hours_per_customer", "support_hourly_cost",
        "available_support_hours_per_month",
    ],
)
def test_negative_inputs_are_rejected(scenario: RecurringScenario, field: str) -> None:
    with pytest.raises(ScenarioValidationError, match="cannot be negative"):
        replace(scenario, **{field: Decimal("-1")})


def test_negative_customer_count_is_rejected(scenario: RecurringScenario) -> None:
    with pytest.raises(ScenarioValidationError, match="cannot be negative"):
        scenario.at(-1)


def test_non_integer_customer_count_is_rejected(scenario: RecurringScenario) -> None:
    with pytest.raises(ScenarioValidationError, match="must be an integer"):
        scenario.at(Decimal("1"))  # type: ignore[arg-type]


def test_source_data_is_not_mutated() -> None:
    source = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    original = deepcopy(source)
    scenario = RecurringScenario.from_mapping(source)
    _ = scenario.at(25)
    assert source == original
