# Custom Software Deal Economics

This repository is a compact, executable textbook about the business economics
of custom-software engagements from a technical-sales and solutions-engineering
perspective. Its central question is: **when does an engagement make economic
sense for the customer, the solutions organization, and the engineering partner?**

**Chapter 0 — The Three-Party Deal**, **Chapter 1 — What Is the Business
Problem Worth?**, **Chapter 2 — What Should the Customer Pay?**, and **Chapter 3
— What Does Delivery Actually Cost?** are implemented. The repository is a
conceptual companion to restaurant-technology work, but it is technically
standalone and needs no other repository, service, or restaurant system.

> **Learning-model disclaimer:** James River Kitchen is a fictional
> Williamsburg-area restaurant. Every financial value here is a fictional,
> illustrative assumption for learning—not real restaurant financial data,
> financial advice, an engineering quote, a market rate, or a claim about what
> any engineering organization can deliver. The model is not evidence.

## Three different numbers

```text
VALUE  What the customer could economically gain
PRICE  What the customer pays
COST   What it takes to deliver
```

Customer value, customer price (vendor revenue), and delivery cost answer
different questions and must not be used interchangeably. A technically feasible
project becomes a viable engagement only when all three perspectives work:

```text
CUSTOMER: Does the economic benefit justify the purchase?
    +
SOLUTIONS ORGANIZATION: Does the engagement compensate discovery, selling,
design, coordination, responsibility, and risk?
    +
ENGINEERING PARTNER: Can implementation and support be sustainable?
    =
VIABLE ENGAGEMENT
```

The customer supplies its problem, operational knowledge, systems, data, employee
time, and budget. Garcia Systems is the fictional sales/solutions layer: it brings
market access, discovery, value engineering, translation, scope and design,
communication, coordination, acceptance, and relationship management. It does
not necessarily perform every implementation task. A non-specific engineering
partner supplies implementation capacity, integration, testing, QA, DevOps,
deployment, maintenance, and suitable reusable components; it could be domestic,
nearshore, offshore, or mixed. No real engineering company is implied.

## Install and run

Python 3.10 or later is required. From the repository root:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[test]'
python examples/three_party_deal.py
python examples/business_value.py
python examples/customer_pricing.py
python examples/delivery_cost.py
pytest
```

Run an experiment without editing the default JSON:

```bash
python examples/three_party_deal.py \
  --customer-price 10000 \
  --recoverable-value 22000 \
  --engineering-cost 4000
```

Money is parsed and calculated with `Decimal`. Calculations retain their precision;
the CLI rounds currency, percentages, and payback only for display. Undefined ROI,
margin, and payback edge cases are printed explicitly rather than divided by zero.

Read [Chapter 0](chapters/00-three-party-deal.md) alongside the code in
[`src/deal_economics/deal.py`](src/deal_economics/deal.py). The assumptions are
editable in [`data/james_river_kitchen.json`](data/james_river_kitchen.json).
Chapter 1's [practical guide](chapters/01-business-value.md),
[`value.py`](src/deal_economics/value.py), and editable
[`james_river_kitchen_value.json`](data/james_river_kitchen_value.json) show how
the fictional $30,000 burden decomposes into $18,000 of potential recovery.
Chapter 2's [customer-pricing guide](chapters/02-customer-pricing.md),
[`pricing.py`](src/deal_economics/pricing.py), and editable
[`james_river_kitchen_pricing.json`](data/james_river_kitchen_pricing.json)
compare implementation prices, recurring fees, ROI, and payback from the buyer's
perspective. Try an override without editing the data:

```bash
python examples/customer_pricing.py \
  --implementation-price 10000 \
  --monthly-fee 250 \
  --annual-benefit 22000 \
  --years 2
```

Chapter 3's [delivery-cost guide](chapters/03-delivery-cost.md),
[`delivery.py`](src/deal_economics/delivery.py), and editable
[`james_river_kitchen_delivery.json`](data/james_river_kitchen_delivery.json)
separate active effort from elapsed duration and compare a visible cost build-up
with its fictional delivery budget. Try:

```bash
python examples/delivery_cost.py \
  --engineering-hours 100 \
  --engineering-rate 35 \
  --qa-hours 20 \
  --rework-reserve 500 \
  --delivery-budget 3000
```

## Eight-chapter roadmap

Exactly four chapters are currently implemented; Chapters 4–7 below are titles only.

0. **The Three-Party Deal** *(implemented)*
1. **What Is the Business Problem Worth?** *(implemented)*
2. **What Should the Customer Pay?** *(implemented)*
3. **What Does Delivery Actually Cost?** *(implemented)*
4. **Who Gets What?** *(planned)*
5. **Reuse Changes Everything** *(planned)*
6. **Recurring Revenue, Support, and Maintenance** *(planned)*
7. **From One Williamsburg Restaurant to a Business** *(planned)*
