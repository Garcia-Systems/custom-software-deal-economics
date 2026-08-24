# Chapter 6 — Recurring Revenue, Support, and Maintenance

[Previous: Chapter 5](05-reuse-economics.md) · [Book home](../README.md) · [Next: Chapter 7](07-scaling-capstone.md)

> **Core question:** Do recurring fees cover recurring direct costs and support
> workload without hiding implementation economics?

> **Disclaimer:** James River Kitchen and every number in this chapter are
> fictional educational assumptions—not managed-service rates, infrastructure
> prices, support benchmarks, staffing guidance, or a quote.

## 1. Go-live is not the end

Live software creates obligations: hosting, monitoring, maintenance, bug fixes,
security patches, backups, certificate renewal, vendor/API changes, customer
support, engineering support, and account management. A recurring fee can help
fund those responsibilities; it does not remove operational risk.

```text
RECURRING REVENUE != FREE MONEY
```

Chapter 5 reduced marginal implementation cost through reuse. Chapter 6 adds
recurring revenue, recurring cost, and support capacity to implementation scale.
A reusable onboarding platform can coexist with an unsustainable support model.

## 2. Separate implementation revenue from recurring revenue

The fictional implementation price is **$8,000 once**, consistent with the
single-deal, reuse, and capstone scenarios. The managed-service fee
is **$350 per active customer per month**. At ten customers, implementation
revenue is $80,000 one-time cumulative revenue; $3,500 is monthly recurring
revenue. Only the latter belongs in MRR and ARR.

## 3. Calculate MRR

```text
MRR = monthly recurring fee x active customers
$350 x 10 = $3,500 MRR
```

The model assumes a stated count of active customers.

## 4. Calculate ARR

```text
ARR = MRR x 12
$3,500 x 12 = $42,000 ARR
```

ARR contains no implementation revenue. This model does not simulate start dates.

## 5. Recurring revenue has recurring cost

The visible per-customer monthly build-up is:

```text
Hosting / infrastructure       $40
Monitoring / operations        $20
Support: 0.75 hours x $120     $90
                               ----
Recurring direct cost         $150
```

All components are fictional. Support labor is calculated only from effort and
rate; it is not hidden in hosting or monitoring, so it cannot be double-counted.

## 6. Hosting and monitoring

The compact model groups infrastructure in hosting and ongoing operational
visibility in monitoring. Actual services can have fixed, variable, and stepped
costs; these simple per-customer inputs are not real infrastructure pricing.

## 7. Support labor

```text
monthly support hours = customers x support hours/customer/month
monthly support labor cost = monthly support hours x hourly cost
```

At ten customers, the assumptions produce 7.5 hours and $900 of monthly labor.
Customer count, unstable integrations, upstream API changes, customizations,
poor observability, manual deployments, and data quality can all raise workload.
The executable model deliberately represents them with one average input.

## 8. Recurring gross contribution

```text
monthly direct recurring cost = direct cost/customer x customers
monthly recurring gross contribution = MRR - monthly direct recurring cost
annual recurring gross contribution = monthly contribution x 12
```

At ten customers, monthly cost is $1,500, monthly gross contribution is $2,000,
and annual gross contribution is $24,000. “Gross contribution” is intentional:
it is before indirect overhead and broader company expenses, not profit.

## 9. Recurring gross margin

```text
recurring gross margin = monthly recurring gross contribution / MRR
```

The default is about 57.14%. With zero MRR the ratio is undefined (`None`), so
the code never divides by zero. Equal MRR does not imply equal economic quality:
a fictional business with $20,000 MRR and $5,000 direct cost retains far more
gross contribution than one with $20,000 MRR and $18,000 direct cost.

## 10. Support hours scale too

At the checkpoint counts 1, 5, 10, 25, 50, and 100, both MRR and average support
hours grow linearly. One customer requires 0.75 modeled hours; 100 require 75.
Real support is not perfectly linear: one upstream incident can affect many
customers simultaneously. An average is an assumption, not a guarantee.

## 11. Financial capacity versus operational capacity

```text
FINANCIAL CAPACITY: Does recurring revenue exceed direct recurring cost?
OPERATIONAL CAPACITY: Can the team perform the required support work?
```

A model can pass one and fail the other. Capacity utilization is required support
hours divided by available support hours. At zero available capacity, zero work
has zero utilization; positive work has infinite utilization and exceeds capacity.

## 12. When support capacity breaks

At 0.75 hours/customer and 80 available hours, `floor(80 / 0.75)` gives a maximum
of 106 customers within capacity. This is only a mathematical threshold under
fictional inputs—not a staffing benchmark. With two hours/customer, 50 customers
require 100 hours and exceed capacity even though the default financial model
still produces positive contribution.

## 13. More customers can increase losses

If the fee is equal to or below the $150 direct cost, contribution/customer is
zero or negative. A $100 fee loses $50/customer/month: more customers enlarge
the loss. Aggregate revenue growth cannot repair negative unit economics.

## 14. Run the experiment

```bash
python examples/recurring_revenue.py
python examples/recurring_revenue.py --monthly-fee 150
python examples/recurring_revenue.py --monthly-fee 100
python examples/recurring_revenue.py --support-hours-per-customer 1.5
python examples/recurring_revenue.py --support-hours-per-customer 0.4
python examples/recurring_revenue.py --support-capacity 160
python examples/recurring_revenue.py --monthly-fee 450 \
  --support-hours-per-customer 1.25 --support-rate 100 --support-capacity 120
```

These experiments show, respectively: fee sensitivity; compounding negative
economics; doubled workload and labor cost; a reliability assumption that lowers
cost and workload; a larger threshold; and combined overrides. Reliability does
not improve automatically. Added capacity generally has a cost even though this
model does not model salaried headcount. Compare the 1- and 100-customer rows to
see both revenue and workload grow approximately with customer count.

## 15. Reliability changes the model

Lower average support effort improves financial and operational capacity. Better
observability, deployment automation, and robust integrations may influence it,
but the model makes no promise that a software change will achieve the input.

## 16. Important simplifications

The model excludes churn, failed renewals, late payments, expansions,
contractions, cohorts, start dates, stochastic incidents, staffing schedules,
payroll, and stepped infrastructure costs. Charging a fee does not eliminate
security, maintenance, or availability risk. Capacity is one simple signal, not
a staffing optimizer.

## 17. Connection to Chapter 7

Chapter 6 stops at recurring economics and support capacity. It does **not**
implement the capstone.

> What happens when implementation economics, platform recovery, recurring
> revenue, support workload, solutions-engineering effort, and delivery capacity
> are all combined at 1, 5, 10, 25, 50, and 100 customers?

That is Chapter 7.

[Previous: Chapter 5](05-reuse-economics.md) · [Book home](../README.md) · [Next: Chapter 7](07-scaling-capstone.md)
