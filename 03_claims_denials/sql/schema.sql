-- ============================================================
-- Claims Denials / Revenue Cycle — Schema
-- ============================================================

DROP TABLE IF EXISTS claims;

CREATE TABLE claims (
    claim_id        INTEGER PRIMARY KEY,
    service_date    DATE,
    submit_date     DATE,
    paid_date       DATE,            -- NULL/empty if unpaid
    payer           VARCHAR(20),
    department      VARCHAR(20),
    cpt_code        VARCHAR(10),
    billed_amount   NUMERIC(12,2),
    paid_amount     NUMERIC(12,2),
    claim_status    VARCHAR(20),     -- Paid, Denied, Appealed-Paid, Appealed-Denied, Written Off
    is_denied       SMALLINT,
    denial_reason   VARCHAR(40),     -- blank when not denied
    days_to_payment INTEGER
);

CREATE INDEX idx_claims_payer  ON claims(payer);
CREATE INDEX idx_claims_status ON claims(claim_status);

-- Load (psql):
--   \copy claims FROM 'data/claims.csv' CSV HEADER
