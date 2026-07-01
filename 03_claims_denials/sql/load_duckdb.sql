-- ============================================================
-- DuckDB loader — Claims Denials
-- Run this FIRST (creates the table), then run analysis.sql.
--
-- Paths are RELATIVE to this project folder. Launch DuckDB from
-- inside 03_claims_denials/ so the data/ folder resolves:
--     cd 03_claims_denials
--     duckdb
--     .read sql/load_duckdb.sql
--     .read sql/analysis.sql
-- ============================================================

CREATE OR REPLACE TABLE claims AS
SELECT * FROM read_csv_auto('data/claims.csv');

SELECT COUNT(*) AS rows FROM claims;
