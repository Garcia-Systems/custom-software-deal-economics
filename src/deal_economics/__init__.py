"""Small, executable models for custom-software deal economics."""

from .allocation import EngagementEconomics, SolutionsEffort, load_engagement_economics
from .deal import DealScenario, ScenarioValidationError, load_scenario
from .delivery import DeliveryScenario, LaborComponent, load_delivery_scenario
from .pricing import PricingScenario, load_pricing_scenario
from .reuse import ReuseComparison, ReuseScenario, ScalePoint, load_reuse_comparison
from .value import (
    EventBurden,
    LaborBurden,
    PeriodicBurden,
    ValueAssessment,
    ValueComponent,
    load_value_assessment,
)

__all__ = [
    "DealScenario",
    "DeliveryScenario",
    "EngagementEconomics",
    "EventBurden",
    "LaborBurden",
    "LaborComponent",
    "PeriodicBurden",
    "PricingScenario",
    "ReuseComparison",
    "ReuseScenario",
    "ScenarioValidationError",
    "SolutionsEffort",
    "ScalePoint",
    "ValueAssessment",
    "ValueComponent",
    "load_delivery_scenario",
    "load_engagement_economics",
    "load_pricing_scenario",
    "load_reuse_comparison",
    "load_scenario",
    "load_value_assessment",
]
