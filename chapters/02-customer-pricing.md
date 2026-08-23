# Chapter 2 — What Should the Customer Pay?

> **Learning-model disclaimer:** James River Kitchen, every alternative, and every
> financial figure in this chapter are fictional. They are editable assumptions,
> not restaurant data, financial advice, engineering quotes, market rates, or
> evidence of actual willingness to pay.

## 1. Value does not determine price automatically

Chapter 1 estimated a credible *potential recoverable value*. Chapter 2 asks what
happens to the buyer's economics at different prices. It does not turn value into
a quote:

```text
CUSTOMER VALUE       How much economic benefit may be created
        ↓
CUSTOMER PRICE       What the customer pays
        ↓
DELIVERY ECONOMICS   What implementation and support cost
```

Neither `customer value = customer price` nor `delivery cost = customer price`.
A viable deal eventually has to work for every participant, but this chapter
examines the customer side. In particular:

```text
A $20,000 project may be inexpensive relative to a $100,000 problem
and extremely expensive relative to a $5,000 problem.
```

## 2. Four ways to think about pricing

No method is universally correct.

1. **Hourly pricing:** `billable hours × billing rate`. Time and materials can fit
   uncertain scope, but the customer bears more scope uncertainty. Effort may not
   correlate with value, and incentives can drift when effort dominates outcome.
2. **Cost-based pricing:** `estimated direct delivery cost + required contribution`.
   This is a useful internal floor or sanity check. It does not prove sufficient
   customer value: a vendor-profitable project can still be irrational to buy.
   Chapter 3 will examine delivery cost rather than doing so here.
3. **Fixed-project pricing:** one price for defined scope. Its credibility depends
   on scope clarity, assumptions, exclusions, change risk, and delivery risk. This
   is not contract language.
4. **Value-informed pricing:** credible economic benefit informs a feasible range.
   A $100,000 annual problem may support different economics from a $5,000 one.
   There is no rule to “charge 10% of value,” or any other universal percentage.

## 3. Start with credible customer value

Chapter 1's fictional model produced $18,000 per year of *potential recoverable
value* after applying process-improvement assumptions. This chapter uses that
number directly as annual economic benefit. It does not add an adoption percentage,
because another percentage would obscure rather than clarify this small example.
Thus the visible assumption is that the modeled $18,000 is realized each year.
In a real assessment, evidence may justify a separate adoption/realization
adjustment; that is distinct from Chapter 1's process-improvement assumptions.

## 4. First-year customer cost

The model makes both price components visible:

```text
first-year customer cost
= implementation price + (12 × monthly recurring fee)
```

At the fictional defaults, `$8,000 + (12 × $350) = $12,200`. A scenario without
a recurring obligation uses zero.

## 5. Recurring fees change the economics

The $18,000 annual benefit is $1,500 per month. A fictional $350 managed-service
fee leaves `$1,500 - $350 = $1,150` of monthly net economic benefit. Recurring
fees therefore affect both total cost and payback; they cannot be ignored simply
because the implementation price is unchanged.

## 6. Net benefit

For the chosen positive-integer horizon:

```text
total benefit = annual economic benefit × analysis years
total customer cost = implementation price
                    + (monthly recurring fee × 12 × analysis years)
net customer benefit = total benefit - total customer cost
```

The default one-year net benefit is `$18,000 - $12,200 = $5,800`. The model uses
simple undiscounted amounts; it intentionally does not model NPV, IRR, WACC,
inflation, financing, or indefinite extrapolation.

## 7. ROI

This textbook defines ROI for the selected horizon as:

```text
ROI = (net customer benefit / customer investment) × 100
customer investment = implementation price + recurring fees in the horizon
```

The default is `$5,800 / $12,200 = 47.54%` after display rounding. This is an
educational measure, not a standard threshold. When total investment is zero,
ROI is **undefined**, not infinite.

## 8. Payback

With a stable monthly benefit:

```text
monthly net economic benefit = monthly economic benefit - monthly recurring fee
payback months = implementation price / monthly net economic benefit
```

The default payback is `$8,000 / $1,150 ≈ 6.96 months`, rather than Chapter 0's
simpler calculation that had no recurring fee. This calculation only works when
monthly net benefit is positive. If it is zero or negative, the program reports
**no payback under the modeled assumptions** instead of dividing by zero.

## 9. Compare several prices

Run `python examples/customer_pricing.py`. With the same fictional $18,000 benefit
and $350 monthly fee, its first-year comparison is:

| Implementation | First-year cost | Net benefit | ROI | Payback | Positive first year? |
|---:|---:|---:|---:|---:|:---:|
| $3,000 | $7,200 | $10,800 | 150.00% | 2.61 months | yes |
| $8,000 | $12,200 | $5,800 | 47.54% | 6.96 months | yes |
| $15,000 | $19,200 | -$1,200 | -6.25% | 13.04 months | no |
| $25,000 | $29,200 | -$11,200 | -38.36% | 21.74 months | no |

These results do not identify a “correct” price. Scope, risk, delivery cost,
alternatives, budget, complexity, strategic importance, procurement constraints,
and recurring obligations still matter. Lower price is not automatically better.

## 10. A price can be profitable and still be bad for the customer

Cost-based reasoning might show positive vendor contribution while customer net
benefit is negative. Knowing cost does not prove value. Likewise, mathematical
maximum and commercially sensible price differ: charging the full $18,000 annual
value would leave no first-year benefit even *before* recurring fees, adoption
risk, disruption, or uncertainty. Economic value is not automatically the price
ceiling a customer will rationally accept. A credible deal normally leaves
meaningful value with the buyer, but there is no universal required buyer share.

A customer's willingness to pay is not proof of value.

## 11. A price can be attractive and still be impossible to deliver

Strong ROI does not say whether implementation and support are sustainable.

A strong value case is not proof that the vendor can deliver profitably.

That second question belongs to Chapter 3. This chapter does not add staffing,
engineering-hour, QA, DevOps, reuse, offshore-rate, or margin-allocation models.

## 12. Compare against alternatives

Custom development competes with the next-best realistic alternative, not an
empty spreadsheet. A fictional discussion might include:

| Option | Up-front | Monthly | Expected benefit |
|---|---:|---:|---|
| Do nothing | $0 | $0 | none |
| Existing SaaS | $1,000 | $500 | somewhat lower |
| Process improvement | small | small | narrower |
| Small automation | moderate | small | highest-value step only |
| Custom software | $8,000 | $350 | modeled $18,000/year |

These illustrative descriptions are not product or market claims. The cheapest
option is not automatically best, and custom is not automatically best. Compare
cost, attainable benefit, fit, risk, and obligations on consistent assumptions.

## 13. Budget is not the same as value

Economic justification asks whether benefits justify investment. Available budget
asks whether spending is approved and fundable. A high-ROI project can exceed the
approved budget; an available budget can fund a weak project. Procurement does
not replace the value case, and this model does not simulate procurement workflows.

## 14. Run the experiment

The JSON values are strings so money parses exactly as `Decimal`. Try:

```bash
python examples/customer_pricing.py \
  --implementation-price 10000 \
  --monthly-fee 250 \
  --annual-benefit 22000 \
  --years 2
```

Then conduct six experiments:

1. **Price:** compare $3,000, $8,000, $15,000, and $25,000 at the same value.
2. **Lower value:** halve annual benefit and observe prices becoming less attractive.
3. **Higher value:** raise credible benefit and observe the changed economics.
4. **Recurring fee:** try $0, $200, $350, and $750 per month; inspect first-year
   cost, ROI, monthly net benefit, and payback.
5. **No payback:** set the fee equal to or above monthly gross benefit.
6. **Longer horizon:** compare `--years 1` and `--years 3`; recurring fees
   accumulate every month while implementation is counted once.

## 15. When the answer should be “too expensive”

Consider a fictional weak case:

```text
Recoverable annual value: $6,000
Proposed implementation: $15,000
```

Even before a recurring fee, first-year net benefit is -$9,000 and simple payback
is 30 months. Under these assumptions the custom project is economically weak;
the modeled price consumes more than the first year's value and exposes the buyer
to uncertainty. Sensible responses to investigate include existing software,
simplifying scope, automating only the highest-value part, deferring, or not
building. This is a scenario diagnosis, not a universal payback rule.

## 16. Connection to Chapter 3

This textbook produces a **pricing model**, not a real customer quote. A quote
would also require actual scope, integrations, data quality, security requirements,
delivery risk, acceptance criteria, support obligations, legal terms, procurement,
schedule, and engineering cost. Those are intentionally absent. Chapter 3 will
ask whether a customer-attractive price can support viable delivery economics;
Chapters 3–7 remain future work.
