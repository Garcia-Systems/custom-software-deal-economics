import json
from copy import deepcopy
from dataclasses import replace
from decimal import Decimal
from pathlib import Path

import pytest

from deal_economics import (
    DeliveryScenario,
    LaborComponent,
    ScenarioValidationError,
    load_delivery_scenario,
)

DATA_FILE = Path(__file__).parents[1] / "data" / "james_river_kitchen_delivery.json"


@pytest.fixture
def scenario() -> DeliveryScenario:
    return load_delivery_scenario(DATA_FILE)


def test_labor_cost_is_hours_times_rate() -> None:
    labor = LaborComponent("Engineering", Decimal("70"), Decimal("30"))
    assert labor.cost == Decimal("2100")


def test_default_labor_components_aggregate(scenario: DeliveryScenario) -> None:
    assert scenario.labor_cost == Decimal("2715.00")
    assert scenario.active_labor_hours == Decimal("93")


def test_reserve_and_total_delivery_cost(scenario: DeliveryScenario) -> None:
    assert scenario.rework_reserve == Decimal("285.00")
    assert scenario.total_delivery_cost == Decimal("3000.00")


def test_budget_variance(scenario: DeliveryScenario) -> None:
    assert scenario.budget_variance == Decimal("0.00")
    assert replace(scenario, delivery_budget=Decimal("3500")).budget_variance == Decimal("500.00")
    assert replace(scenario, delivery_budget=Decimal("2500")).budget_variance == Decimal("-500.00")


def test_elapsed_duration_does_not_change_effort_cost(scenario: DeliveryScenario) -> None:
    for weeks in map(Decimal, ("3", "6", "10")):
        changed = replace(scenario, elapsed_weeks=weeks)
        assert changed.labor_cost == scenario.labor_cost
        assert changed.total_delivery_cost == scenario.total_delivery_cost


def test_doubled_engineering_hours_increase_cost(scenario: DeliveryScenario) -> None:
    engineering, *rest = scenario.labor
    changed = replace(
        scenario,
        labor=(replace(engineering, hours=engineering.hours * 2), *rest),
    )
    assert changed.total_delivery_cost == Decimal("5100.00")
    assert changed.total_delivery_cost - scenario.total_delivery_cost == Decimal("2100.00")


def test_zero_hour_optional_component_is_allowed() -> None:
    assert LaborComponent("Optional QA", Decimal("0"), Decimal("25")).cost == 0


@pytest.mark.parametrize("field", ["hours", "hourly_rate"])
def test_negative_labor_input_is_rejected(field: str) -> None:
    values = {"hours": Decimal("1"), "hourly_rate": Decimal("1")}
    values[field] = Decimal("-0.01")
    with pytest.raises(ScenarioValidationError, match="cannot be negative"):
        LaborComponent("Labor", **values)


@pytest.mark.parametrize("field", ["rework_reserve", "delivery_budget"])
def test_negative_scenario_money_is_rejected(scenario: DeliveryScenario, field: str) -> None:
    with pytest.raises(ScenarioValidationError, match="cannot be negative"):
        replace(scenario, **{field: Decimal("-0.01")})


@pytest.mark.parametrize("weeks", [Decimal("0"), Decimal("-1")])
def test_invalid_elapsed_duration_is_rejected(scenario: DeliveryScenario, weeks: Decimal) -> None:
    with pytest.raises(ScenarioValidationError, match="elapsed_weeks"):
        replace(scenario, elapsed_weeks=weeks)


def test_source_scenario_data_is_not_mutated() -> None:
    source = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    original = deepcopy(source)
    scenario = DeliveryScenario.from_mapping(source)
    _ = (scenario.active_labor_hours, scenario.total_delivery_cost, scenario.budget_variance)
    assert source == original
