# Power BI Build Spec — Claims Denials & Revenue Cycle

Recreate this revenue-cycle dashboard in Power BI Desktop from `/data/claims.csv`.

## 1. Get Data
`Get Data → Text/CSV → claims.csv`. Types: `service_date` / `submit_date` / `paid_date` = Date (paid_date has blanks for unpaid claims), `billed_amount` / `paid_amount` = Decimal, `is_denied` / `days_to_payment` = Whole Number.

## 2. Data Model
Single fact table `claims`. Add a `Calendar` table related to `claims[service_date]`. Optionally build small lookup tables for `payer` and `denial_reason` if you want clean slicers, but the model works flat.

## 3. Core DAX Measures
```DAX
Total Claims = COUNTROWS(claims)

Total Billed = SUM(claims[billed_amount])

Total Collected = SUM(claims[paid_amount])

Net Collection Rate = DIVIDE([Total Collected], [Total Billed])

Denied Claims = SUM(claims[is_denied])

Denial Rate = DIVIDE([Denied Claims], [Total Claims])

Revenue Gap = [Total Billed] - [Total Collected]

Avg Days to Payment =
AVERAGEX(FILTER(claims, claims[days_to_payment] > 0), claims[days_to_payment])

Recovered via Appeal =
CALCULATE([Total Collected], claims[claim_status] = "Appealed-Paid")
```
Format currency measures as $ (no decimals); rates as % (1 decimal).

## 4. Report Pages

### Page 1 — Revenue Cycle Overview
- **KPI cards:** Total Billed · Total Collected · Net Collection Rate · Denial Rate · Revenue Gap.
- **Line chart:** Denial Rate by month (`Calendar`), with Total Collected as a secondary axis column.
- **Bar:** Denial Rate by `payer` (sorted descending).
- **Slicers:** `payer`, `department`, `Calendar[Quarter]`.

### Page 2 — Denial Analysis (the actionable page)
- **Pareto:** `denial_reason` by Denied Claims, with a cumulative % line — shows which few reasons drive most denials (Prior Auth, Coding, Documentation).
- **Stacked bar:** Denied Claims by `department` and `denial_reason`.
- **Matrix:** rows = `payer`, columns = `denial_reason`, values = Denied Claims (heat-map conditional format).

### Page 3 — Collections & AR
- **Funnel / waterfall:** Total Billed → Denials → Write-offs → Total Collected.
- **Column:** Collected by aging bucket (0–30, 31–60, 61–90, 90+ days from `days_to_payment`).
- **Card:** Recovered via Appeal + appeal-success rate.
- **Table:** top 50 high-dollar `Denied`/`Written Off` claims = recovery worklist.

## 5. Interpretation hooks for the portfolio writeup
The story: a ~16% denial rate and ~55% net collection rate means real money on the table. Prior-auth and coding denials are *preventable* at the front end; the Pareto and the appeal-recovery numbers turn the dashboard into a prioritized action list rather than just a scorecard.
