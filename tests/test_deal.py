import json
from copy import deepcopy
from dataclasses import replace
from decimal import Decimal
from pathlib import Path

import pytest

from deal_economics import DealScenario, ScenarioValidationError, load_scenario

DATA_FILE = Path(__file__).parents[1] / "data" / "james_river_kitchen.json"


@pytest.fixture
def scenario() -> DealScenario:
    return load_scenario(DATA_FILE)


def test_default_deal_economics(scenario: DealScenario) -> None:
    assert scenario.total_direct_costs == Decimal("3500.00")
    assert scenario.gross_contribution == Decimal("4500.00")
    assert scenario.gross_margin == Decimal("0.5625")
    assert scenario.customer_first_year_benefit == Decimal("18000.00")
    assert scenario.customer_first_year_net_benefit == Decimal("10000.00")
    assert scenario.customer_roi == Decimal("1.25")
    assert scenario.approximate_payback_months == Decimal("5.333333333333333333333333333")


def test_engineering_cost_increase_reduces_contribution(scenario: DealScenario) -> None:
    changed = replace(scenario, engineering_cost=Decimal("6000"))
    assert changed.gross_contribution == scenario.gross_contribution - Decimal("3000")


def test_customer_price_increase_changes_roi(scenario: DealScenario) -> None:
    changed = replace(scenario, customer_price=Decimal("10000"))
    assert changed.customer_roi == Decimal("0.8")
    assert changed.customer_roi < scenario.customer_roi


def test_zero_revenue_has_undefined_margin(scenario: DealScenario) -> None:
    assert replace(scenario, customer_price=Decimal("0")).gross_margin is None


def test_zero_benefit_has_no_payback(scenario: DealScenario) -> None:
    assert replace(scenario, recoverable_value=Decimal("0")).approximate_payback_months is None


def test_zero_investment_has_undefined_roi(scenario: DealScenario) -> None:
    assert replace(scenario, customer_price=Decimal("0")).customer_roi is None


@pytest.mark.parametrize("field", [
    "current_state_cost", "recoverable_value", "customer_price",
    "engineering_cost", "other_direct_costs",
])
def test_negative_money_is_rejected(scenario: DealScenario, field: str) -> None:
    with pytest.raises(ScenarioValidationError, match="cannot be negative"):
        replace(scenario, **{field: Decimal("-0.01")})


def test_parsing_and_calculations_do_not_mutate_source() -> None:
    source = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    original = deepcopy(source)
    scenario = DealScenario.from_mapping(source)
    _ = (scenario.gross_contribution, scenario.customer_roi)
    assert source == original

