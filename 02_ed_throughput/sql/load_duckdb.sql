-- ============================================================
-- DuckDB loader — ED Throughput
-- Run this FIRST (creates the table), then run analysis.sql.
--
-- Paths are RELATIVE to this project folder. Launch DuckDB from
-- inside 02_ed_throughput/ so the data/ folder resolves:
--     cd 02_ed_throughput
--     duckdb
--     .read sql/load_duckdb.sql
--     .read sql/analysis.sql
-- ============================================================

CREATE OR REPLACE TABLE ed_visits AS
SELECT * FROM read_csv_auto('data/ed_visits.csv');

SELECT COUNT(*) AS rows FROM ed_visits;
