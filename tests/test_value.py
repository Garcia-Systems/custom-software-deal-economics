import json
from copy import deepcopy
from dataclasses import replace
from decimal import Decimal
from pathlib import Path

import pytest

from deal_economics import (
    EventBurden,
    LaborBurden,
    PeriodicBurden,
    ScenarioValidationError,
    ValueAssessment,
    ValueComponent,
    load_value_assessment,
)

DATA_FILE = Path(__file__).parents[1] / "data" / "james_river_kitchen_value.json"


def component(burden, rate="0.6") -> ValueComponent:
    return ValueComponent("Test burden", "Fictional test assumption", burden, Decimal(rate))


def test_weekly_labor_burden_annualizes() -> None:
    assert LaborBurden(Decimal("5"), Decimal("52"), Decimal("35")).annual_cost == Decimal("9100")


def test_periodic_waste_burden_annualizes() -> None:
    assert PeriodicBurden(Decimal("150"), Decimal("52")).annual_cost == Decimal("7800")


def test_event_burden_annualizes() -> None:
    assert EventBurden(Decimal("20"), Decimal("190")).annual_cost == Decimal("3800")


def test_recoverable_value_applies_improvement() -> None:
    assert component(PeriodicBurden(Decimal("100"), Decimal("10")), "0.7").recoverable_value == Decimal("700.0")


def test_default_components_aggregate_and_leave_unrecovered_burden() -> None:
    assessment = load_value_assessment(DATA_FILE)
    assert assessment.total_current_state_cost == Decimal("30000.00")
    assert assessment.total_recoverable_value == Decimal("18000.000")
    assert assessment.unrecovered_burden == Decimal("12000.000")


@pytest.mark.parametrize("rate, expected", [("0", "0"), ("1", "1000")])
def test_zero_and_full_improvement(rate: str, expected: str) -> None:
    value = component(EventBurden(Decimal("10"), Decimal("100")), rate)
    assert value.recoverable_value == Decimal(expected)


@pytest.mark.parametrize(
    "burden",
    [
        LaborBurden(Decimal("1"), Decimal("1"), Decimal("1")),
        PeriodicBurden(Decimal("1"), Decimal("1")),
        EventBurden(Decimal("1"), Decimal("1")),
    ],
)
def test_negative_monetary_values_are_rejected(burden) -> None:
    field = {
        LaborBurden: "loaded_hourly_cost",
        PeriodicBurden: "cost_per_period",
        EventBurden: "cost_per_event",
    }[type(burden)]
    with pytest.raises(ScenarioValidationError, match="cannot be negative"):
        replace(burden, **{field: Decimal("-0.01")})


@pytest.mark.parametrize(
    "burden, field",
    [
        (LaborBurden(Decimal("1"), Decimal("1"), Decimal("1")), "hours_per_occurrence"),
        (LaborBurden(Decimal("1"), Decimal("1"), Decimal("1")), "occurrences_per_year"),
        (PeriodicBurden(Decimal("1"), Decimal("1")), "periods_per_year"),
        (EventBurden(Decimal("1"), Decimal("1")), "events_per_year"),
    ],
)
def test_negative_frequencies_and_hours_are_rejected(burden, field: str) -> None:
    with pytest.raises(ScenarioValidationError, match="cannot be negative"):
        replace(burden, **{field: Decimal("-1")})


@pytest.mark.parametrize("rate", ["-0.01", "1.01"])
def test_improvement_outside_zero_to_one_is_rejected(rate: str) -> None:
    with pytest.raises(ScenarioValidationError, match="improvement_rate"):
        component(EventBurden(Decimal("1"), Decimal("1")), rate)


def test_source_scenario_data_is_not_mutated() -> None:
    source = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    original = deepcopy(source)
    assessment = ValueAssessment.from_mapping(source)
    _ = (assessment.total_current_state_cost, assessment.total_recoverable_value)
    assert source == original
