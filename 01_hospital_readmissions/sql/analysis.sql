-- ============================================================
-- Hospital Readmissions — Analysis Queries
-- Question set a hospital quality team would actually ask.
-- ============================================================

-- 1. Overall 30-day readmission rate (the headline KPI)
SELECT
    COUNT(*)                                            AS total_eligible_discharges,
    SUM(readmitted_30d)                                 AS readmissions,
    ROUND(100.0 * SUM(readmitted_30d) / COUNT(*), 2)    AS readmission_rate_pct
FROM admissions
WHERE discharge_disposition <> 'Expired';

-- 2. Readmission rate by primary diagnosis (which conditions drive returns?)
SELECT
    primary_diagnosis,
    COUNT(*)                                            AS discharges,
    SUM(readmitted_30d)                                 AS readmissions,
    ROUND(100.0 * SUM(readmitted_30d) / COUNT(*), 2)    AS readmission_rate_pct,
    ROUND(AVG(length_of_stay_days), 1)                  AS avg_los_days
FROM admissions
WHERE discharge_disposition <> 'Expired'
GROUP BY primary_diagnosis
ORDER BY readmission_rate_pct DESC;

-- 3. Readmission rate by age band and insurance (equity / payer lens)
SELECT
    CASE
        WHEN p.age < 40 THEN '18-39'
        WHEN p.age < 55 THEN '40-54'
        WHEN p.age < 70 THEN '55-69'
        ELSE '70+'
    END                                                 AS age_band,
    p.primary_insurance,
    COUNT(*)                                            AS discharges,
    ROUND(100.0 * SUM(a.readmitted_30d) / COUNT(*), 2)  AS readmission_rate_pct
FROM admissions a
JOIN patients p ON p.patient_id = a.patient_id
WHERE a.discharge_disposition <> 'Expired'
GROUP BY age_band, p.primary_insurance
ORDER BY age_band, readmission_rate_pct DESC;

-- 4. Does length of stay correlate with readmission?
SELECT
    CASE
        WHEN length_of_stay_days <= 2 THEN '1-2 days'
        WHEN length_of_stay_days <= 5 THEN '3-5 days'
        WHEN length_of_stay_days <= 9 THEN '6-9 days'
        ELSE '10+ days'
    END                                                 AS los_band,
    COUNT(*)                                            AS discharges,
    ROUND(100.0 * SUM(readmitted_30d) / COUNT(*), 2)    AS readmission_rate_pct
FROM admissions
WHERE discharge_disposition <> 'Expired'
GROUP BY los_band
ORDER BY MIN(length_of_stay_days);

-- 5. Discharge disposition vs readmission (do SNF/Home-Health discharges return more?)
SELECT
    discharge_disposition,
    COUNT(*)                                            AS discharges,
    ROUND(100.0 * SUM(readmitted_30d) / COUNT(*), 2)    AS readmission_rate_pct
FROM admissions
WHERE discharge_disposition <> 'Expired'
GROUP BY discharge_disposition
ORDER BY readmission_rate_pct DESC;

-- 6. Monthly trend of readmission rate (is it improving?)
--    DuckDB syntax shown. PostgreSQL: use TO_CHAR(discharge_date, 'YYYY-MM').
SELECT
    strftime(discharge_date, '%Y-%m')                  AS discharge_month,
    COUNT(*)                                            AS discharges,
    ROUND(100.0 * SUM(readmitted_30d) / COUNT(*), 2)    AS readmission_rate_pct
FROM admissions
WHERE discharge_disposition <> 'Expired'
GROUP BY 1
ORDER BY 1;

-- 7. High-utilizer patients (3+ admissions) — care-management target list
SELECT
    p.patient_id, p.patient_name, p.age, p.primary_insurance,
    COUNT(*)                                            AS admission_count,
    SUM(a.readmitted_30d)                               AS readmissions,
    ROUND(SUM(a.total_charges), 2)                      AS total_charges
FROM admissions a
JOIN patients p ON p.patient_id = a.patient_id
GROUP BY p.patient_id, p.patient_name, p.age, p.primary_insurance
HAVING COUNT(*) >= 3
ORDER BY admission_count DESC, total_charges DESC
LIMIT 50;

-- 8. Estimated financial impact of readmissions
SELECT
    SUM(readmitted_30d)                                 AS readmissions,
    ROUND(AVG(total_charges), 2)                        AS avg_charge_per_admission,
    ROUND(SUM(readmitted_30d) * AVG(total_charges), 2)  AS est_readmission_charges
FROM admissions
WHERE discharge_disposition <> 'Expired';
