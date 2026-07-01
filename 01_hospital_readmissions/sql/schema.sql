-- ============================================================
-- Hospital Readmissions — Schema (PostgreSQL / standard SQL)
-- Load the two CSVs in /data into these tables.
-- ============================================================

DROP TABLE IF EXISTS admissions;
DROP TABLE IF EXISTS patients;

CREATE TABLE patients (
    patient_id        INTEGER PRIMARY KEY,
    patient_name      VARCHAR(100),
    gender            VARCHAR(10),
    age               INTEGER,
    race              VARCHAR(20),
    primary_insurance VARCHAR(20)
);

CREATE TABLE admissions (
    admission_id          INTEGER PRIMARY KEY,
    patient_id            INTEGER REFERENCES patients(patient_id),
    admit_date            TIMESTAMP,
    discharge_date        TIMESTAMP,
    length_of_stay_days   INTEGER,
    primary_diagnosis     VARCHAR(40),
    department            VARCHAR(40),
    discharge_disposition VARCHAR(20),
    total_charges         NUMERIC(12,2),
    readmitted_30d        SMALLINT      -- 1 if patient re-admitted within 30 days of this discharge
);

CREATE INDEX idx_adm_patient ON admissions(patient_id);
CREATE INDEX idx_adm_dx      ON admissions(primary_diagnosis);

-- Example load (psql):
--   \copy patients   FROM 'data/patients.csv'   CSV HEADER
--   \copy admissions FROM 'data/admissions.csv' CSV HEADER
