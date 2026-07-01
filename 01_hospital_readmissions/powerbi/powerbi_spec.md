# Power BI Build Spec — Hospital Readmissions

A step-by-step guide to recreate this dashboard in Power BI Desktop from the CSVs in `/data`.

## 1. Get Data
`Home → Get Data → Text/CSV` and load both files:
- `patients.csv`
- `admissions.csv`

In Power Query, confirm types: `admit_date` / `discharge_date` = Date/Time, `total_charges` = Decimal, `readmitted_30d` & `length_of_stay_days` = Whole Number.

## 2. Data Model (star-ish schema)
- **Dim:** `patients` (`patient_id` primary key)
- **Fact:** `admissions` (`patient_id` foreign key)
- Relationship: `patients[patient_id]  1 ──< *  admissions[patient_id]` (single direction, cross-filter from patients to admissions).
- Add a **Date table** (`Calendar`) and relate `Calendar[Date]` to `admissions[discharge_date]` (date portion) for time intelligence.

```
Calendar = ADDCOLUMNS(
    CALENDAR(DATE(2024,1,1), DATE(2025,12,31)),
    "Year", YEAR([Date]),
    "Month", FORMAT([Date],"YYYY-MM"),
    "MonthName", FORMAT([Date],"MMM")
)
```

## 3. Core DAX Measures
```DAX
Total Discharges =
CALCULATE(COUNTROWS(admissions), admissions[discharge_disposition] <> "Expired")

Readmissions = SUM(admissions[readmitted_30d])

Readmission Rate =
DIVIDE([Readmissions], [Total Discharges])

Avg Length of Stay = AVERAGE(admissions[length_of_stay_days])

Avg Charge per Admission = AVERAGE(admissions[total_charges])

Est. Readmission Charges = [Readmissions] * [Avg Charge per Admission]

Readmission Rate MoM =
VAR Curr = [Readmission Rate]
VAR Prev = CALCULATE([Readmission Rate], DATEADD(Calendar[Date], -1, MONTH))
RETURN Curr - Prev
```
Format `Readmission Rate` as percentage (1 decimal); `Avg Charge` and `Est. Readmission Charges` as currency.

## 4. Report Pages

### Page 1 — Executive Overview
- **KPI cards (top row):** Total Discharges · Readmissions · Readmission Rate · Avg LOS · Est. Readmission Charges.
- **Line chart:** `Readmission Rate` by `Calendar[Month]` with a constant line at the 15% national benchmark.
- **Clustered bar:** `Readmission Rate` by `primary_diagnosis` (sorted descending).
- **Slicers:** `primary_insurance`, `department`, `Calendar[Year]`.

### Page 2 — Clinical Drill-down
- **Matrix:** rows = `primary_diagnosis`, columns = LOS band, values = `Readmission Rate` (conditional-format heat map).
- **Bar:** `Readmission Rate` by `discharge_disposition`.
- **Scatter:** `Avg Length of Stay` (x) vs `Readmission Rate` (y), one point per diagnosis, bubble size = Total Discharges.

### Page 3 — Population / Equity
- **Clustered column:** `Readmission Rate` by age band, broken out by `primary_insurance`.
- **Table:** high-utilizer patients (filter `Total Admissions >= 3`) — patient, age, insurance, admissions, total charges.
- Decomposition tree on `Readmission Rate` split by diagnosis → insurance → age band.

## 5. Suggested Theme
Navy `#1F3864` primary, light blue `#D9E1F2` accents, red `#C00000` for above-benchmark conditional formatting. Use these to flag any diagnosis above the 15% line.
