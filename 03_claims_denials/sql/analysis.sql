-- ============================================================
-- Claims Denials / Revenue Cycle — Analysis Queries
-- ============================================================

-- 1. Headline revenue-cycle KPIs
SELECT
    COUNT(*)                                              AS total_claims,
    ROUND(SUM(billed_amount), 2)                          AS total_billed,
    ROUND(SUM(paid_amount), 2)                            AS total_collected,
    ROUND(100.0 * SUM(paid_amount)/SUM(billed_amount), 2) AS net_collection_rate_pct,
    ROUND(100.0 * SUM(is_denied)/COUNT(*), 2)             AS denial_rate_pct,
    ROUND(AVG(NULLIF(days_to_payment,0)), 1)              AS avg_days_to_payment
FROM claims;

-- 2. Denial rate and dollars by payer (who's hard to collect from?)
SELECT
    payer,
    COUNT(*)                                              AS claims,
    ROUND(100.0 * SUM(is_denied)/COUNT(*), 2)             AS denial_rate_pct,
    ROUND(SUM(billed_amount), 2)                          AS billed,
    ROUND(SUM(paid_amount), 2)                            AS collected,
    ROUND(100.0 * SUM(paid_amount)/SUM(billed_amount), 2) AS net_collection_rate_pct
FROM claims
GROUP BY payer
ORDER BY denial_rate_pct DESC;

-- 3. Denial reasons — the actionable breakdown for the RCM team
SELECT
    denial_reason,
    COUNT(*)                                              AS denied_claims,
    ROUND(SUM(billed_amount), 2)                          AS billed_at_risk,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2)    AS pct_of_denials
FROM claims
WHERE is_denied = 1
GROUP BY denial_reason
ORDER BY denied_claims DESC;

-- 4. Denial rate by department
SELECT
    department,
    COUNT(*)                                              AS claims,
    ROUND(100.0 * SUM(is_denied)/COUNT(*), 2)             AS denial_rate_pct,
    ROUND(SUM(billed_amount - paid_amount), 2)            AS revenue_gap
FROM claims
GROUP BY department
ORDER BY denial_rate_pct DESC;

-- 5. Appeal outcomes — is appealing worth it?
SELECT
    claim_status,
    COUNT(*)                                              AS claims,
    ROUND(SUM(billed_amount), 2)                          AS billed,
    ROUND(SUM(paid_amount), 2)                            AS recovered
FROM claims
WHERE is_denied = 1
GROUP BY claim_status
ORDER BY claims DESC;

-- 6. Monthly denial-rate trend
--    DuckDB syntax shown. PostgreSQL: use TO_CHAR(service_date, 'YYYY-MM').
SELECT
    strftime(service_date, '%Y-%m')                      AS service_month,
    COUNT(*)                                              AS claims,
    ROUND(100.0 * SUM(is_denied)/COUNT(*), 2)             AS denial_rate_pct,
    ROUND(SUM(paid_amount), 2)                            AS collected
FROM claims
GROUP BY 1
ORDER BY 1;

-- 7. Aged AR proxy: payment-speed buckets for paid claims
SELECT
    CASE
        WHEN days_to_payment <= 30  THEN '0-30 days'
        WHEN days_to_payment <= 60  THEN '31-60 days'
        WHEN days_to_payment <= 90  THEN '61-90 days'
        ELSE '90+ days'
    END                                                   AS payment_bucket,
    COUNT(*)                                              AS claims,
    ROUND(SUM(paid_amount), 2)                            AS collected
FROM claims
WHERE paid_amount > 0
GROUP BY payment_bucket
ORDER BY MIN(days_to_payment);

-- 8. Top write-off recovery opportunities: high-dollar denials never appealed
SELECT
    claim_id, payer, department, cpt_code, denial_reason,
    billed_amount
FROM claims
WHERE claim_status IN ('Denied','Written Off')
ORDER BY billed_amount DESC
LIMIT 50;
