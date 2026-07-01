-- ============================================================
-- Emergency Department Throughput — Schema
-- ============================================================

DROP TABLE IF EXISTS ed_visits;

CREATE TABLE ed_visits (
    visit_id                 INTEGER PRIMARY KEY,
    arrival_datetime         TIMESTAMP,
    arrival_hour             INTEGER,
    day_of_week              VARCHAR(10),
    arrival_mode             VARCHAR(15),
    esi_triage_level         SMALLINT,      -- 1 (most acute) .. 5 (least)
    chief_complaint          VARCHAR(40),
    patient_age              INTEGER,
    patient_gender           VARCHAR(10),
    door_to_triage_min       NUMERIC(8,1),
    triage_to_provider_min   NUMERIC(8,1),  -- NULL for LWBS
    ed_los_min               NUMERIC(8,1),  -- arrival to departure
    disposition              VARCHAR(15),
    left_without_being_seen  SMALLINT,
    boarding_min             NUMERIC(8,1)   -- admit decision to floor bed (admitted only)
);

CREATE INDEX idx_ed_hour  ON ed_visits(arrival_hour);
CREATE INDEX idx_ed_esi   ON ed_visits(esi_triage_level);

-- Load (psql):
--   \copy ed_visits FROM 'data/ed_visits.csv' CSV HEADER
