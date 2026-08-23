"""Chapter 2's customer-side pricing economics model."""

from __future__ import annotations

import json
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Mapping

from .deal import ScenarioValidationError


MONEY_FIELDS = ("annual_economic_benefit", "implementation_price", "monthly_recurring_fee")


@dataclass(frozen=True)
class PricingScenario:
    """Fictional price assumptions evaluated from the customer's perspective.

    ``roi`` is a ratio (for example, ``Decimal("0.4754")`` is 47.54%).
    Investment includes implementation and every recurring fee in the selected
    horizon. Payback assumes a stable monthly benefit and recurring fee.
    """

    scenario: str
    fictional: bool
    annual_economic_benefit: Decimal
    implementation_price: Decimal
    monthly_recurring_fee: Decimal
    analysis_years: int

    def __post_init__(self) -> None:
        if not self.scenario.strip():
            raise ScenarioValidationError("scenario must have a name")
        if self.fictional is not True:
            raise ScenarioValidationError("Chapter 2 scenarios must be explicitly fictional")
        for name in MONEY_FIELDS:
            value = getattr(self, name)
            if not isinstance(value, Decimal) or not value.is_finite():
                raise ScenarioValidationError(f"{name} must be a finite Decimal")
            if value < 0:
                raise ScenarioValidationError(f"{name} cannot be negative")
        if isinstance(self.analysis_years, bool) or not isinstance(self.analysis_years, int):
            raise ScenarioValidationError("analysis_years must be a positive integer")
        if self.analysis_years <= 0:
            raise ScenarioValidationError("analysis_years must be positive")

    @property
    def first_year_customer_cost(self) -> Decimal:
        return self.implementation_price + Decimal("12") * self.monthly_recurring_fee

    @property
    def first_year_net_benefit(self) -> Decimal:
        return self.annual_economic_benefit - self.first_year_customer_cost

    @property
    def first_year_economics_positive(self) -> bool:
        return self.first_year_net_benefit > 0

    @property
    def total_customer_cost(self) -> Decimal:
        months = Decimal("12") * Decimal(self.analysis_years)
        return self.implementation_price + self.monthly_recurring_fee * months

    @property
    def total_benefit(self) -> Decimal:
        return self.annual_economic_benefit * Decimal(self.analysis_years)

    @property
    def net_benefit(self) -> Decimal:
        return self.total_benefit - self.total_customer_cost

    @property
    def roi(self) -> Decimal | None:
        """Horizon net benefit / total customer investment; undefined at zero cost."""
        if self.total_customer_cost == 0:
            return None
        return self.net_benefit / self.total_customer_cost

    @property
    def monthly_economic_benefit(self) -> Decimal:
        return self.annual_economic_benefit / Decimal("12")

    @property
    def monthly_net_economic_benefit(self) -> Decimal:
        return self.monthly_economic_benefit - self.monthly_recurring_fee

    @property
    def payback_months(self) -> Decimal | None:
        """Implementation price / monthly net benefit, if monthly benefit is positive."""
        if self.monthly_net_economic_benefit <= 0:
            return None
        return self.implementation_price / self.monthly_net_economic_benefit

    @classmethod
    def from_mapping(cls, source: Mapping[str, Any]) -> "PricingScenario":
        """Build a validated pricing scenario without modifying ``source``."""
        try:
            values = {name: Decimal(str(source[name])) for name in MONEY_FIELDS}
            raw_years = source["analysis_years"]
            if isinstance(raw_years, bool):
                raise ScenarioValidationError("analysis_years must be a positive integer")
            years = int(raw_years)
            if Decimal(str(raw_years)) != Decimal(years):
                raise ScenarioValidationError("analysis_years must be a positive integer")
            return cls(str(source["scenario"]), source["fictional"], **values, analysis_years=years)
        except KeyError as exc:
            raise ScenarioValidationError(f"missing scenario field: {exc.args[0]}") from exc
        except (InvalidOperation, TypeError, ValueError) as exc:
            if isinstance(exc, ScenarioValidationError):
                raise
            raise ScenarioValidationError("pricing fields must contain valid numbers") from exc


def load_pricing_scenario(path: str | Path) -> PricingScenario:
    with Path(path).open(encoding="utf-8") as scenario_file:
        source = json.load(scenario_file)
    if not isinstance(source, dict):
        raise ScenarioValidationError("scenario JSON must contain an object")
    return PricingScenario.from_mapping(source)
