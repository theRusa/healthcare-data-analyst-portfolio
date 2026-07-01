-- ============================================================
-- Emergency Department Throughput — Analysis Queries
-- ============================================================

-- 1. Headline operational KPIs
SELECT
    COUNT(*)                                              AS total_visits,
    ROUND(AVG(door_to_triage_min), 1)                     AS avg_door_to_triage_min,
    ROUND(AVG(triage_to_provider_min), 1)                 AS avg_wait_to_provider_min,
    ROUND(AVG(ed_los_min), 1)                             AS avg_ed_los_min,
    ROUND(100.0 * SUM(left_without_being_seen)/COUNT(*),2) AS lwbs_rate_pct,
    ROUND(100.0 * SUM(CASE WHEN disposition='Admitted' THEN 1 ELSE 0 END)/COUNT(*),2) AS admit_rate_pct
FROM ed_visits;

-- 2. Wait-to-provider by triage acuity (ESI) — are sick patients seen fast?
SELECT
    esi_triage_level,
    COUNT(*)                                              AS visits,
    ROUND(AVG(triage_to_provider_min), 1)                 AS avg_wait_min,
    ROUND(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY triage_to_provider_min), 1)  AS median_wait_min,
    ROUND(PERCENTILE_CONT(0.9) WITHIN GROUP (ORDER BY triage_to_provider_min), 1)  AS p90_wait_min
FROM ed_visits
WHERE triage_to_provider_min IS NOT NULL
GROUP BY esi_triage_level
ORDER BY esi_triage_level;

-- 3. Volume and wait by hour of day — staffing signal
SELECT
    arrival_hour,
    COUNT(*)                                              AS visits,
    ROUND(AVG(triage_to_provider_min), 1)                 AS avg_wait_min,
    ROUND(AVG(ed_los_min), 1)                             AS avg_los_min
FROM ed_visits
GROUP BY arrival_hour
ORDER BY arrival_hour;

-- 4. Volume by day of week
SELECT
    day_of_week,
    COUNT(*)                                              AS visits,
    ROUND(AVG(ed_los_min), 1)                             AS avg_los_min,
    ROUND(100.0 * SUM(left_without_being_seen)/COUNT(*),2) AS lwbs_rate_pct
FROM ed_visits
GROUP BY day_of_week
ORDER BY visits DESC;

-- 5. LWBS analysis — when do we lose patients? (long waits => walkouts)
SELECT
    CASE WHEN arrival_hour BETWEEN 7 AND 14 THEN 'Day (07-14)'
         WHEN arrival_hour BETWEEN 15 AND 22 THEN 'Evening (15-22)'
         ELSE 'Overnight (23-06)' END                     AS shift,
    COUNT(*)                                              AS visits,
    SUM(left_without_being_seen)                          AS lwbs_count,
    ROUND(100.0 * SUM(left_without_being_seen)/COUNT(*),2) AS lwbs_rate_pct
FROM ed_visits
GROUP BY shift
ORDER BY lwbs_rate_pct DESC;

-- 6. Boarding burden — admitted patients waiting for an inpatient bed
SELECT
    ROUND(AVG(boarding_min), 1)                           AS avg_boarding_min,
    ROUND(PERCENTILE_CONT(0.9) WITHIN GROUP (ORDER BY boarding_min),1) AS p90_boarding_min,
    SUM(CASE WHEN boarding_min > 240 THEN 1 ELSE 0 END)   AS boarded_over_4h
FROM ed_visits
WHERE disposition = 'Admitted';

-- 7. Throughput target compliance: % of visits with LOS under 4 hours (240 min)
SELECT
    disposition,
    COUNT(*)                                              AS visits,
    ROUND(100.0 * SUM(CASE WHEN ed_los_min <= 240 THEN 1 ELSE 0 END)/COUNT(*),2) AS pct_under_4h
FROM ed_visits
GROUP BY disposition
ORDER BY visits DESC;

-- 8. Top chief complaints by volume and average LOS
SELECT
    chief_complaint,
    COUNT(*)                                              AS visits,
    ROUND(AVG(ed_los_min),1)                              AS avg_los_min
FROM ed_visits
GROUP BY chief_complaint
ORDER BY visits DESC;
