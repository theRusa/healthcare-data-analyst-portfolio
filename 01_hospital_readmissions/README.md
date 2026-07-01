# Hospital Readmissions Analysis

![Dashboard](images/dashboard.png)

Analyzing 30-day hospital readmissions to identify which patients, diagnoses, and discharge pathways drive avoidable returns — the core metric behind CMS's Hospital Readmissions Reduction Program.

## Business question
Where are 30-day readmissions concentrated, and which levers (diagnosis, length of stay, discharge disposition, payer) would a quality team pull to reduce them?

## Dataset (synthetic)
`data/patients.csv` — 4,000 patients (demographics, insurance).
`data/admissions.csv` — 9,000 admissions with diagnosis, LOS, discharge disposition, charges, and a `readmitted_30d` flag derived from whether the same patient was re-admitted within 30 days of discharge.

All data is synthetic, generated with NumPy (`../_generate_data.py`, seed 42). No real patient data.

## Key findings
- **Overall 30-day readmission rate: ~12.0%** (excluding expired discharges), in line with real-world all-cause rates.
- **Highest-risk diagnoses:** Sepsis (~13.6%), Cellulitis (~12.9%), and Stroke (~12.7%) — natural targets for discharge-planning and follow-up programs.
- Readmission risk varies by **length of stay** and **discharge disposition** (SNF/home-health vs home), and by **age band and insurance**, surfacing an equity angle.
- A small set of **high-utilizer patients (3+ admissions)** account for an outsized share of charges — a ready-made care-management worklist.

## What's in this repo
- `sql/schema.sql` — table definitions and load commands.
- `sql/analysis.sql` — 8 analytical queries (overall rate, by diagnosis, by age/insurance, by LOS, by disposition, monthly trend, high utilizers, financial impact).
- `excel/readmissions_analysis.xlsx` — live workbook: KPI dashboard + by-diagnosis and by-LOS breakdowns with charts (all SUMIFS/COUNTIFS formulas, zero errors).
- `powerbi/powerbi_spec.md` — step-by-step Power BI build: data model, DAX measures, and a 3-page report layout.

## How to use
1. **SQL (DuckDB — fastest):** from this project folder, run `duckdb`, then `.read sql/load_duckdb.sql` followed by `.read sql/analysis.sql`. The loader reads the CSVs with relative paths, so no editing needed. (For PostgreSQL, use `schema.sql` to create/load the tables; the only dialect difference is the monthly-trend query, which is noted inline.)
2. **Excel:** open the workbook — the Dashboard tab recalculates from the raw `Admissions`/`Patients` tabs.
3. **Power BI:** follow `powerbi_spec.md` to rebuild the interactive version from the same CSVs.

## Skills demonstrated
Data modeling · analytical SQL (window functions, conditional aggregation) · KPI design · Excel formula modeling & charting · BI dashboard design · healthcare domain framing.
