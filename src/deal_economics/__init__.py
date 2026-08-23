"""Small, executable models for custom-software deal economics."""

from .deal import DealScenario, ScenarioValidationError, load_scenario

__all__ = ["DealScenario", "ScenarioValidationError", "load_scenario"]

