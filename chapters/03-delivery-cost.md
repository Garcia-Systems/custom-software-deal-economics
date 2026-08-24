# Chapter 3 — What Does Delivery Actually Cost?

[Previous: Chapter 2](02-customer-pricing.md) · [Book home](../README.md) · [Next: Chapter 4](04-who-gets-what.md)

> **Core question:** What active labor and other direct inputs does delivery
> require, independently of elapsed duration and customer price?

## 1. Price is not delivery cost

Chapter 2 asked what the customer should pay. This chapter asks what an
engineering partner must spend to deliver. These are different numbers:

```text
PROJECT PRICE ≠ DELIVERY COST
```

An $8,000 project might cost $3,000, $7,500, or $12,000 to deliver. Price alone
does not establish sustainable delivery, just as cheap delivery alone does not
establish customer value.

## 2. Meet the $3,000 delivery-budget hypothesis

The editable scenario starts with a **fictional $3,000 delivery budget**. It is
not a claim that $3,000 buys six weeks of offshore development—or any fixed
amount of market labor. What it supports depends on labor mix, modeled rates,
effort, reuse, complexity, rework, QA, deployment, and support obligations.

Every rate in this chapter is an educational modeling input. It is not an
engineer salary, an offshore or other market rate, a company delivery rate, an
engineering quote, or a guaranteed outsourcing cost.

## 3. Break delivery into effort components

The base case deliberately stays compact:

| Component | Active hours | Fictional rate | Cost |
|---|---:|---:|---:|
| Engineering | 70 | $30/hour | $2,100 |
| QA | 15 | $25/hour | $375 |
| Deployment / DevOps | 8 | $30/hour | $240 |
| Visible rework reserve | — | — | $285 |
| **Total** | **93 labor hours** | | **$3,000** |

Coordination, infrastructure, or third-party setup should be explicit components
when the scope needs them; this constrained example does not invent them.

## 4. Engineering hours and rate

```text
engineering cost = engineering hours × engineering rate
70 × $30 = $2,100
```

Hours describe active work, not the dates between kickoff and completion. Rate
is an editable assumption used to translate that effort into modeled cost.

## 5. QA is part of delivery

The base case makes testing visible: `15 × $25 = $375`. Zero QA hours is valid
mathematically, so it is a useful experiment, but entering zero does not prove
that real delivery needs no testing.

## 6. Deployment is real work

The model includes eight hours for deployment/DevOps: `8 × $30 = $240`.
Environment preparation, access, release checks, and deployment windows consume
effort even though this example does not implement cloud billing or automation.

## 7. Rework and uncertainty

The $285 reserve is separate instead of being hidden in hourly rates. It makes
expected revisions and uncertainty discussable. Set it to zero and the model
still runs, but uncertainty has not disappeared; the estimate has merely stopped
funding it. Unclear requirements can materially increase delivery cost.

## 8. Add the cost components

```text
$2,100 engineering
  $375 QA
  $240 deployment
  $285 rework reserve
= $3,000 modeled delivery cost
```

This is a single-engagement cost model, not a timesheet, payroll system, invoice,
staffing plan, or project-management workflow.

## 9. Six weeks is not 240 hours

```text
ELAPSED PROJECT TIME ≠ ENGINEERING EFFORT
```

Effort is the 93 active labor hours in the table. Elapsed duration is the six
calendar weeks from start to completion. Those hours can span six weeks because
of discovery handoff, part-time staffing, customer feedback, QA cycles, access
delays, deployment windows, revisions, and coordination. Six elapsed weeks do
not imply `6 × 40 = 240` engineering hours.

Change elapsed duration from 3 to 6 to 10 weeks while leaving effort unchanged.
Modeled cost stays unchanged because no cost in this scenario depends on time.

## 10. Budget versus actual modeled cost

```text
budget variance = delivery budget − modeled delivery cost
```

A positive variance means under budget, zero means exactly at budget, and a
negative variance means over budget. **Variance is not profit.** The default
budget and cost are both $3,000, producing a $0 variance.

## 11. What happens when engineering takes twice as long?

Change engineering from 70 to 140 hours. Engineering becomes $4,200 and total
modeled cost becomes $5,100, so variance against $3,000 becomes **−$2,100**.
Elapsed duration does not cause this change; additional active effort does.

## 12. Scope determines effort

A small integration might be existing framework + configuration + one adapter +
validation + testing + deployment. A greenfield product might require
architecture + authentication + a data model + multiple integrations + a user
interface + deployment + monitoring + support. Those are not equivalent scopes,
so they should not inherit the same hours by assumption.

## 13. Existing assets can change effort

Existing authentication, deployment tooling, an API-adapter framework, or
validation utilities may reduce customer-specific effort. This chapter only
acknowledges that possibility. Chapter 5, not Chapter 3, owns reuse economics.

## 14. Expose assumptions

Before presenting a confident estimate, expose what it assumes about:

- API availability, documentation, data quality, and authentication complexity;
- the number of integrations and unknown legacy behavior;
- environment access, security requirements, and deployment process;
- acceptance criteria and customer responsiveness.

Unknowns belong in the conversation and, where appropriate, in explicit effort
or reserve—not in false precision.

## 15. Run the experiment

Run the default:

```bash
python examples/delivery_cost.py
```

Then try the requested experiments:

1. Double engineering hours with `--engineering-hours 140`.
2. Raise its fictional rate with `--engineering-rate 35` while holding hours.
3. Model integration risk with `--qa-hours 30`.
4. Increase uncertainty funding with `--rework-reserve 500`.
5. Remove it with `--rework-reserve 0`, remembering that risk remains.
6. Run `--elapsed-weeks 3`, `6`, and `10` with identical labor inputs.

Combine inputs to ask what the budget supports:

```bash
python examples/delivery_cost.py \
  --engineering-hours 100 \
  --engineering-rate 35 \
  --qa-hours 20 \
  --rework-reserve 500 \
  --delivery-budget 3000
```

## 16. When the budget does not work

Suppose customer project price is $8,000, planned delivery budget is $3,000,
and actual modeled delivery cost is $6,500. That does **not** automatically mean
the customer should simply be charged more. Disciplined responses include:

- reduce scope;
- improve reuse or redesign the solution;
- use a different implementation approach or existing SaaS;
- negotiate a higher price only if customer value supports it; or
- do not pursue the project.

## 17. Connection to Chapter 4

Chapter 2 showed how $8,000 could make sense from the customer's perspective.
Chapter 3 asks whether delivery can be sustainable inside the economics created
by that price. If price is $8,000 and modeled delivery cost is $3,000, $5,000
remains **before other engagement economics**. This chapter does not allocate or
interpret that remainder. Chapter 4 will address who gets what.

[Previous: Chapter 2](02-customer-pricing.md) · [Book home](../README.md) · [Next: Chapter 4](04-who-gets-what.md)
