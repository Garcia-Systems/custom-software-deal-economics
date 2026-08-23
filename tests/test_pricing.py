import json
from copy import deepcopy
from dataclasses import replace
from decimal import Decimal
from pathlib import Path

import pytest

from deal_economics import PricingScenario, ScenarioValidationError, load_pricing_scenario

DATA_FILE = Path(__file__).parents[1] / "data" / "james_river_kitchen_pricing.json"


@pytest.fixture
def scenario() -> PricingScenario:
    return load_pricing_scenario(DATA_FILE)


def test_first_year_cost_includes_twelve_monthly_fees(scenario: PricingScenario) -> None:
    assert scenario.first_year_customer_cost == Decimal("12200.00")


def test_total_cost_over_multiple_years(scenario: PricingScenario) -> None:
    assert replace(scenario, analysis_years=3).total_customer_cost == Decimal("20600.00")


def test_net_benefit_and_roi(scenario: PricingScenario) -> None:
    assert scenario.net_benefit == Decimal("5800.00")
    assert scenario.roi == Decimal("5800") / Decimal("12200")


def test_monthly_net_benefit_and_recurring_fee_payback(scenario: PricingScenario) -> None:
    assert scenario.monthly_net_economic_benefit == Decimal("1150.00")
    assert scenario.payback_months == Decimal("8000") / Decimal("1150")


def test_zero_recurring_fee_produces_simple_payback(scenario: PricingScenario) -> None:
    changed = replace(scenario, monthly_recurring_fee=Decimal("0"))
    assert changed.payback_months == Decimal("8000") / Decimal("1500")


def test_zero_implementation_price_is_safe(scenario: PricingScenario) -> None:
    changed = replace(scenario, implementation_price=Decimal("0"))
    assert changed.roi == Decimal("13800") / Decimal("4200")
    assert changed.payback_months == 0


def test_zero_customer_investment_has_undefined_roi(scenario: PricingScenario) -> None:
    changed = replace(scenario, implementation_price=Decimal("0"), monthly_recurring_fee=Decimal("0"))
    assert changed.roi is None


@pytest.mark.parametrize(
    "annual_benefit, monthly_fee",
    [("0", "0"), ("18000", "1500"), ("18000", "1500.01")],
)
def test_nonpositive_monthly_net_benefit_has_no_payback(
    scenario: PricingScenario, annual_benefit: str, monthly_fee: str
) -> None:
    changed = replace(
        scenario,
        annual_economic_benefit=Decimal(annual_benefit),
        monthly_recurring_fee=Decimal(monthly_fee),
    )
    assert changed.payback_months is None


@pytest.mark.parametrize(
    "field", ["annual_economic_benefit", "implementation_price", "monthly_recurring_fee"]
)
def test_negative_money_is_rejected(scenario: PricingScenario, field: str) -> None:
    with pytest.raises(ScenarioValidationError, match="cannot be negative"):
        replace(scenario, **{field: Decimal("-0.01")})


@pytest.mark.parametrize("years", [0, -1])
def test_nonpositive_analysis_years_are_rejected(scenario: PricingScenario, years: int) -> None:
    with pytest.raises(ScenarioValidationError, match="must be positive"):
        replace(scenario, analysis_years=years)


def test_scenario_calculations_do_not_mutate_source() -> None:
    source = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    original = deepcopy(source)
    scenario = PricingScenario.from_mapping(source)
    _ = (scenario.first_year_customer_cost, scenario.net_benefit, scenario.roi, scenario.payback_months)
    assert source == original
