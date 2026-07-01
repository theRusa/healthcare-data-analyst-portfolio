-- ============================================================
-- DuckDB loader — Hospital Readmissions
-- Run this FIRST (creates the tables), then run analysis.sql.
--
-- Paths are RELATIVE to this project folder. Launch DuckDB from
-- inside 01_hospital_readmissions/ so the data/ folder resolves:
--     cd 01_hospital_readmissions
--     duckdb
--     .read sql/load_duckdb.sql
--     .read sql/analysis.sql
-- ============================================================

CREATE OR REPLACE TABLE patients AS
SELECT * FROM read_csv_auto('data/patients.csv');

CREATE OR REPLACE TABLE admissions AS
SELECT * FROM read_csv_auto('data/admissions.csv');

-- quick check
SELECT 'patients' AS tbl, COUNT(*) AS rows FROM patients
UNION ALL
SELECT 'admissions', COUNT(*) FROM admissions;
