# Power BI Build Spec — Emergency Department Throughput

Recreate this operations dashboard in Power BI Desktop from `/data/ed_visits.csv`.

## 1. Get Data
`Get Data → Text/CSV → ed_visits.csv`. In Power Query set types: `arrival_datetime` = Date/Time, the `*_min` columns = Decimal, `esi_triage_level` / `arrival_hour` / `left_without_being_seen` = Whole Number. Note `triage_to_provider_min` contains blanks for LWBS visits — leave as null (DAX averages ignore blanks).

## 2. Data Model
Single fact table `ed_visits`. Add a `Calendar` date table related to `arrival_datetime` for daily/weekly trends, plus two small helper tables you can create with **Enter Data**:
- `ESI Lookup` (1–5 with labels "1 - Resuscitation" … "5 - Non-urgent")
- `Shift Lookup` (Day / Evening / Overnight) — or derive shift as a calculated column:

```DAX
Shift =
SWITCH(TRUE(),
    ed_visits[arrival_hour] >= 7 && ed_visits[arrival_hour] <= 14, "Day (07-14)",
    ed_visits[arrival_hour] >= 15 && ed_visits[arrival_hour] <= 22, "Evening (15-22)",
    "Overnight (23-06)")
```

## 3. Core DAX Measures
```DAX
Total Visits = COUNTROWS(ed_visits)

Avg Door to Triage = AVERAGE(ed_visits[door_to_triage_min])

Avg Wait to Provider = AVERAGE(ed_visits[triage_to_provider_min])

Median Wait to Provider = MEDIAN(ed_visits[triage_to_provider_min])

Avg ED LOS = AVERAGE(ed_visits[ed_los_min])

LWBS Rate = DIVIDE(SUM(ed_visits[left_without_being_seen]), [Total Visits])

Admit Rate =
DIVIDE(CALCULATE([Total Visits], ed_visits[disposition]="Admitted"), [Total Visits])

Avg Boarding (min) =
CALCULATE(AVERAGE(ed_visits[boarding_min]), ed_visits[disposition]="Admitted")

% LOS Under 4h =
DIVIDE(CALCULATE([Total Visits], ed_visits[ed_los_min] <= 240), [Total Visits])
```
Format rates as %; minute measures as whole/1-decimal numbers.

## 4. Report Pages

### Page 1 — Operations Overview
- **KPI cards:** Total Visits · Avg Wait to Provider · Avg ED LOS · LWBS Rate · % LOS Under 4h.
- **Line/area chart:** Total Visits by `arrival_hour` (0–23) — shows the daily demand curve.
- **Clustered column:** Avg Wait to Provider by `esi_triage_level` (target lines: ESI 1–2 should be < 15 min).
- **Slicers:** `day_of_week`, `arrival_mode`, Shift.

### Page 2 — Wait Time & Acuity
- **Matrix:** rows = `esi_triage_level`, values = Avg Wait, Median Wait, Avg ED LOS, Total Visits.
- **Heat map (matrix conditional format):** rows = `day_of_week`, columns = Shift, values = Avg ED LOS.
- **Histogram-style column:** count of visits bucketed by ED LOS (use a binned column: 0–60, 61–120, 121–240, 240+).

### Page 3 — Bottlenecks (LWBS & Boarding)
- **Column:** LWBS Rate by Shift and by `esi_triage_level`.
- **Card + gauge:** Avg Boarding vs a 240-min target; count of patients boarded > 4h.
- **Table:** chief complaints by Total Visits and Avg ED LOS, sorted by volume.

## 5. Interpretation hooks for the portfolio writeup
Call out: the evening volume peak vs staffing, the relationship between long waits and LWBS, and boarding time as the hidden driver of crowding. These are the conversations an ED operations manager actually has.
