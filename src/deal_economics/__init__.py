"""Small, executable models for custom-software deal economics."""

from .deal import DealScenario, ScenarioValidationError, load_scenario
from .value import (
    EventBurden,
    LaborBurden,
    PeriodicBurden,
    ValueAssessment,
    ValueComponent,
    load_value_assessment,
)

__all__ = [
    "DealScenario", "EventBurden", "LaborBurden", "PeriodicBurden",
    "ScenarioValidationError", "ValueAssessment", "ValueComponent",
    "load_scenario", "load_value_assessment",
]
