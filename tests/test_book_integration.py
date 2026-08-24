"""Cross-chapter checks for assumptions the book intentionally shares."""

from decimal import Decimal
from pathlib import Path

from deal_economics import (
    load_capstone_comparison,
    load_delivery_scenario,
    load_engagement_economics,
    load_pricing_scenario,
    load_recurring_scenario,
    load_reuse_comparison,
    load_scenario,
    load_value_assessment,
)


DATA = Path(__file__).parents[1] / "data"


def test_introductory_value_is_decomposed_by_chapter_one() -> None:
    deal = load_scenario(DATA / "james_river_kitchen.json")
    value = load_value_assessment(DATA / "james_river_kitchen_value.json")

    assert value.total_current_state_cost == deal.current_state_cost
    assert value.total_recoverable_value == deal.recoverable_value


def test_pricing_and_allocation_share_customer_economics() -> None:
    pricing = load_pricing_scenario(DATA / "james_river_kitchen_pricing.json")
    allocation = load_engagement_economics(DATA / "james_river_kitchen_allocation.json")

    assert pricing.annual_economic_benefit == allocation.annual_customer_value
    assert pricing.implementation_price == allocation.customer_price
    assert allocation.customer_net_benefit == Decimal("10000.00")


def test_delivery_cost_flows_into_single_deal_allocation() -> None:
    delivery = load_delivery_scenario(DATA / "james_river_kitchen_delivery.json")
    allocation = load_engagement_economics(DATA / "james_river_kitchen_allocation.json")

    assert delivery.total_delivery_cost == allocation.engineering_delivery_cost
    assert allocation.gross_contribution == Decimal("4500.00")


def test_reuse_and_recurring_defaults_flow_into_capstone() -> None:
    reuse = load_reuse_comparison(DATA / "james_river_kitchen_reuse.json")
    recurring = load_recurring_scenario(DATA / "james_river_kitchen_recurring.json")
    capstone = load_capstone_comparison(DATA / "james_river_kitchen_scaling.json")

    scaled = capstone.reusable_delivery
    assert scaled.implementation == reuse.reusable_foundation
    assert scaled.implementation.break_even_customer == 5
    assert recurring.implementation_price == scaled.implementation.implementation_price
    assert recurring.at(10).mrr == scaled.recurring.at(10).mrr
    assert recurring.at(10).monthly_direct_recurring_cost == (
        scaled.recurring.at(10).monthly_direct_recurring_cost
    )
