import json
from copy import deepcopy
from dataclasses import replace
from decimal import Decimal
from pathlib import Path

import pytest

from deal_economics import (
    EngagementEconomics,
    ScenarioValidationError,
    SolutionsEffort,
    load_engagement_economics,
)

DATA_FILE = Path(__file__).parents[1] / "data" / "james_river_kitchen_allocation.json"


@pytest.fixture
def scenario() -> EngagementEconomics:
    return load_engagement_economics(DATA_FILE)


def test_default_contribution_and_effort(scenario: EngagementEconomics) -> None:
    assert scenario.gross_contribution == Decimal("4500.00")
    assert scenario.solutions_hours == Decimal("45")
    assert scenario.effective_contribution_per_solutions_hour == Decimal("100.00")


def test_zero_solutions_hours_is_safe(scenario: EngagementEconomics) -> None:
    changed = replace(scenario, solutions_effort=())
    assert changed.solutions_hours == 0
    assert changed.effective_contribution_per_solutions_hour is None


def test_engineering_cost_increase_reduces_contribution(scenario: EngagementEconomics) -> None:
    changed = replace(scenario, engineering_delivery_cost=Decimal("6000"))
    assert changed.gross_contribution == Decimal("1500.00")


def test_price_increase_helps_solutions_and_reduces_customer_benefit(
    scenario: EngagementEconomics,
) -> None:
    changed = replace(scenario, customer_price=Decimal("12000"))
    assert changed.gross_contribution == Decimal("8500.00")
    assert changed.customer_net_benefit == Decimal("6000.00")
    assert changed.customer_net_benefit < scenario.customer_net_benefit


def test_more_solutions_effort_reduces_effective_contribution(
    scenario: EngagementEconomics,
) -> None:
    changed = replace(scenario, solutions_effort=(SolutionsEffort("All effort", Decimal("90")),))
    assert changed.effective_contribution_per_solutions_hour == Decimal("50.00")


def test_lower_customer_value_does_not_change_vendor_contribution(
    scenario: EngagementEconomics,
) -> None:
    changed = replace(scenario, annual_customer_value=Decimal("9000"))
    assert changed.customer_net_benefit == Decimal("1000.00")
    assert changed.gross_contribution == scenario.gross_contribution


def test_negative_effort_is_rejected() -> None:
    with pytest.raises(ScenarioValidationError, match="cannot be negative"):
        SolutionsEffort("Discovery", Decimal("-1"))


def test_negative_other_direct_cost_is_rejected(scenario: EngagementEconomics) -> None:
    with pytest.raises(ScenarioValidationError, match="cannot be negative"):
        replace(scenario, other_direct_costs=Decimal("-0.01"))


def test_partner_payment_and_internal_cost_are_distinct(scenario: EngagementEconomics) -> None:
    changed = replace(
        scenario,
        engineering_delivery_cost=Decimal("3500"),
        partner_modeled_delivery_cost=Decimal("3000"),
    )
    assert changed.engineering_partner_revenue == Decimal("3500")
    assert changed.engineering_partner_contribution == Decimal("500")
    assert changed.delivery_budget_sustainable
    assert not replace(changed, partner_modeled_delivery_cost=Decimal("4000")).delivery_budget_sustainable


def test_source_data_is_not_mutated() -> None:
    source = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    original = deepcopy(source)
    scenario = EngagementEconomics.from_mapping(source)
    _ = (scenario.gross_contribution, scenario.solutions_hours, scenario.customer_net_benefit)
    assert source == original
