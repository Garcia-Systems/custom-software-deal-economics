"""Small, executable models for custom-software deal economics."""

from .allocation import EngagementEconomics, SolutionsEffort, load_engagement_economics
from .deal import DealScenario, ScenarioValidationError, load_scenario
from .delivery import DeliveryScenario, LaborComponent, load_delivery_scenario
from .pricing import PricingScenario, load_pricing_scenario
from .recurring import RecurringScalePoint, RecurringScenario, load_recurring_scenario
from .reuse import ReuseComparison, ReuseScenario, ScalePoint, load_reuse_comparison
from .scaling import (
    CapacityModel,
    CapacityResult,
    CapstoneComparison,
    CapstoneScalePoint,
    ScaleScenario,
    load_capstone_comparison,
)
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
    "RecurringScalePoint",
    "RecurringScenario",
    "ReuseComparison",
    "ReuseScenario",
    "ScenarioValidationError",
    "SolutionsEffort",
    "ScalePoint",
    "ScaleScenario",
    "CapacityModel",
    "CapacityResult",
    "CapstoneComparison",
    "CapstoneScalePoint",
    "ValueAssessment",
    "ValueComponent",
    "load_delivery_scenario",
    "load_engagement_economics",
    "load_pricing_scenario",
    "load_recurring_scenario",
    "load_reuse_comparison",
    "load_capstone_comparison",
    "load_scenario",
    "load_value_assessment",
]
