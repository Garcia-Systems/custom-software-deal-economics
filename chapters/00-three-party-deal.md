# Chapter 0 — The Three-Party Deal

[Book home](../README.md) · [Next: Chapter 1](01-business-value.md)

> **Core question:** Where does the money come from, where does it go, and why
> does each participant agree to the deal?

> **Important:** James River Kitchen and every number in this chapter are
> fictional assumptions for educational modeling. They are not real restaurant
> financial information, engineering quotes, market rates, or claims about what
> any organization can deliver.

## 1. Meet James River Kitchen

James River Kitchen is a fictional Williamsburg-area restaurant used to make an
abstract framework executable. Suppose discovery suggests a manual operating
process creates an estimated annual burden and that a narrowly scoped improvement
might recover only part of it:

```text
Current-state economic burden:     $30,000/year
Potential recoverable value:       $18,000/year

Customer project price:             $8,000

Illustrative allocation:
Engineering delivery:               $3,000
Other direct costs/reserve:           $500
Garcia Systems gross contribution:  $4,500
```

These are fictional learning inputs. In particular, **$3,000 is not an offshore
rate, quote, market benchmark, staffing claim, or promise of deliverable scope.**

## 2. The operational problem

A **business problem** is the operational condition creating an economic burden:
for example, a repetitive manual process that is slow or error-prone. The
**current-state cost** estimates the burden of leaving that condition unchanged.
The **potential recoverable value** is the portion an improvement may plausibly
recover. Here it is $18,000 of $30,000—not an assumption that 100% disappears.

Real inputs must come from discovery, not wishful arithmetic:

- What process is manual, who performs it, how often, and for how long?
- What happens when it is late or wrong?
- Is revenue lost, inventory wasted, or scheduling inefficient?
- Which existing systems hold relevant information?
- What improvement would actually matter?

The fictional values merely let us run the framework. Chapter 1 now investigates
how to form a credible value hypothesis from visible operational assumptions.

## 3. The three participants

```text
LOCAL CUSTOMER (restaurant / business)
        ↕
GARCIA SYSTEMS (sales / solutions layer)
        ↕
ENGINEERING PARTNER (implementation / delivery capacity)
```

The customer contributes its problem, operating knowledge, systems, data,
employee time, and budget. It seeks measurable benefit, usable and reliable
software, reasonable risk, and acceptable payback.

Garcia Systems contributes prospecting, trust, discovery, analysis, value
engineering, technical translation, requirements, design, scoping, demos,
communication, delivery coordination, QA/acceptance, and relationship management.
This does **not** mean it personally performs every implementation task.

The engineering partner contributes suitable reusable components and engineering
capacity for implementation, integrations, tests, QA, DevOps, deployment, and
technical maintenance. It could conceptually be offshore, nearshore, domestic,
or mixed; this model neither names a company nor says one arrangement is better.

## 4. Value is not price

```text
VALUE  What the customer could economically gain
PRICE  What the customer pays
COST   What it takes to deliver
```

Value is a potential outcome, not a guarantee. **Customer price** is the amount
the customer pays. To the deal organization that receipt is **revenue**. Neither
number says what delivery consumes.

## 5. Price is not cost

**Delivery cost** means direct costs required to implement the solution. In this
introductory scenario, engineering and other direct engagement costs total $3,500.
Price is $8,000. Treating either as the other would conceal the deal economics.

## 6. Follow the $8,000

| Fictional allocation | Amount |
|---|---:|
| Engineering delivery cost | $3,000 |
| Other direct engagement costs/reserve | $500 |
| Gross contribution | $4,500 |
| **Customer price / revenue** | **$8,000** |

```text
gross contribution
= customer price - engineering delivery cost - other direct engagement costs
= $8,000 - $3,000 - $500 = $4,500
```

This is **gross contribution before indirect overhead**, not unqualified profit.
The model does not subtract general company overhead, taxes, owner compensation,
unrelated sales expense, or corporate administration. Deeper accounting is outside
this textbook's scope.

## 7. Customer economics

Potential first-year benefit is the assumed recoverable value:

```text
Potential first-year value:        $18,000
First-year customer cost:          -$8,000
                                   -------
Potential first-year net benefit:  $10,000
```

```text
customer net benefit = potential first-year economic benefit - first-year customer cost
ROI = (customer net benefit / customer investment) × 100
ROI = ($10,000 / $8,000) × 100 = 125%
```

ROI is undefined when investment is zero; the code returns `None` rather than
dividing by zero. This potential ROI is an output of fictional assumptions, not a
forecast or financial advice.

For a first payback approximation only:

```text
monthly economic benefit = $18,000 / 12 = $1,500
payback months = $8,000 / $1,500 ≈ 5.33 months
```

With zero benefit there is no payback result. Chapter 2 expands
pricing and payback; Chapter 0 does not model recurring economics.

## 8. Solutions-organization economics

Revenue is $8,000, total direct cost is $3,500, and gross contribution is $4,500.

```text
gross margin = gross contribution / revenue
gross margin = $4,500 / $8,000 = 56.25%
```

The code represents margin as undefined at zero revenue. The contribution must
support discovery, selling, design, coordination, responsibility, and risk, as
well as expenses this introductory calculation intentionally excludes.

## 9. Engineering-partner economics

The fictional $3,000 is only an illustrative allocation inside this scenario.
For an engagement to be viable, the partner must be able to implement and support
the agreed solution sustainably. Chapter 0 makes no assertion about real rates,
salaries, locations, capacity, scope, or the superiority of outsourcing.

## 10. What makes the deal viable?

```text
CUSTOMER: Does economic benefit justify the purchase?
        +
SOLUTIONS ORGANIZATION: Is discovery, selling, design, coordination,
responsibility, and risk adequately compensated?
        +
ENGINEERING PARTNER: Can implementation and support be sustainable?
        =
VIABLE ENGAGEMENT
```

Technical feasibility alone cannot answer these questions. Each participant needs
a credible economic reason to say yes.

## 11. Run the experiment

From the repository root, after installing as described in the README:

```bash
python examples/three_party_deal.py
```

The program loads string-encoded money from `data/james_river_kitchen.json` into
an immutable `DealScenario`. `Decimal` retains calculation precision. Currency,
percentages, and payback are rounded only at the CLI presentation boundary.

## 12. Change the assumptions

```bash
python examples/three_party_deal.py \
  --customer-price 10000 \
  --recoverable-value 22000 \
  --engineering-cost 4000 \
  --other-direct-costs 750
```

Try lower value, higher price, doubled engineering cost, or increased direct
costs. Negative amounts are rejected; zeros remain available to expose undefined
ROI, margin, and payback cases safely.

## 13. When the answer should be “do not build”

**Custom software is not automatically the economically correct answer.** The
purpose of solutions engineering is not to justify development; it is to determine
whether a credible case exists. A valid conclusion may be to use existing SaaS,
improve the process without software, run a smaller experiment, postpone the
project, or build nothing.

## 14. What Chapter 1 investigates next

Chapter 1 asks, “What Is the Business Problem Worth?” It decomposes the $30,000
current-state burden and makes each improvement assumption visible. Continue with
[`01-business-value.md`](01-business-value.md).

[Book home](../README.md) · [Next: Chapter 1](01-business-value.md)
