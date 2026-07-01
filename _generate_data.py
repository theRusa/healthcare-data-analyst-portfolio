"""
Synthetic healthcare data generator for 3 data-analyst portfolio projects.
All data is fabricated with NumPy. No real patients. Reproducible via SEED.
"""
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

SEED = 42
rng = np.random.default_rng(SEED)
BASE = "/sessions/stoic-beautiful-archimedes/mnt/Portfolio"

FIRST = ["James","Mary","John","Patricia","Robert","Jennifer","Michael","Linda","David","Elizabeth",
         "William","Barbara","Maria","Jose","Wei","Aisha","Chen","Fatima","Diego","Priya","Omar","Sofia"]
LAST = ["Smith","Johnson","Williams","Brown","Jones","Garcia","Miller","Davis","Rodriguez","Martinez",
        "Hernandez","Lopez","Gonzalez","Wilson","Anderson","Patel","Kim","Nguyen","Khan","Okafor"]

def names(n):
    return [f"{rng.choice(FIRST)} {rng.choice(LAST)}" for _ in range(n)]

# ============================================================
# PROJECT 1 — HOSPITAL READMISSIONS
# ============================================================
def project_readmissions():
    N_PAT = 4000
    pid = np.arange(10001, 10001 + N_PAT)
    gender = rng.choice(["Female","Male"], N_PAT, p=[0.52,0.48])
    age = np.clip(rng.normal(63, 17, N_PAT).round().astype(int), 18, 99)
    race = rng.choice(["White","Black","Hispanic","Asian","Other"], N_PAT, p=[0.58,0.16,0.14,0.08,0.04])
    insurance = rng.choice(["Medicare","Medicaid","Private","Self-Pay"], N_PAT, p=[0.46,0.18,0.30,0.06])
    patients = pd.DataFrame({
        "patient_id": pid, "patient_name": names(N_PAT), "gender": gender,
        "age": age, "race": race, "primary_insurance": insurance,
    })

    # Admissions — some patients admitted multiple times
    N_ADM = 9000
    a_pid = rng.choice(pid, N_ADM)
    dx = rng.choice(
        ["Heart Failure","Pneumonia","COPD","Acute MI","Sepsis","Diabetes","Stroke","Kidney Disease","Hip Fracture","Cellulitis"],
        N_ADM, p=[0.16,0.13,0.12,0.08,0.10,0.11,0.07,0.08,0.07,0.08])
    dept = rng.choice(["Cardiology","Pulmonology","Internal Medicine","Surgery","Nephrology","Neurology"], N_ADM)
    start = datetime(2024,1,1)
    adm_date = [start + timedelta(days=int(rng.integers(0,540)), hours=int(rng.integers(0,24))) for _ in range(N_ADM)]
    # LOS depends loosely on diagnosis severity
    sev = {"Sepsis":7,"Acute MI":6,"Stroke":6,"Heart Failure":5,"Hip Fracture":6,"Kidney Disease":5,
           "Pneumonia":4,"COPD":4,"Diabetes":3,"Cellulitis":3}
    los = np.array([max(1, int(rng.normal(sev[d], 2.2))) for d in dx])
    disch_date = [a + timedelta(days=int(l)) for a,l in zip(adm_date, los)]
    disch_disp = rng.choice(["Home","Home Health","SNF","Rehab","Expired","AMA"], N_ADM, p=[0.55,0.18,0.13,0.08,0.03,0.03])
    total_charges = (los * rng.normal(2800, 600, N_ADM) + rng.normal(4000,1500,N_ADM)).round(2)
    total_charges = np.clip(total_charges, 1200, None)

    adm = pd.DataFrame({
        "admission_id": np.arange(500001, 500001+N_ADM),
        "patient_id": a_pid,
        "admit_date": [d.strftime("%Y-%m-%d %H:%M") for d in adm_date],
        "discharge_date": [d.strftime("%Y-%m-%d %H:%M") for d in disch_date],
        "length_of_stay_days": los,
        "primary_diagnosis": dx,
        "department": dept,
        "discharge_disposition": disch_disp,
        "total_charges": total_charges,
        "_disch_dt": disch_date,
    }).sort_values(["patient_id","_disch_dt"]).reset_index(drop=True)

    # Compute 30-day readmission flag: next admission within 30 days of this discharge (same patient)
    adm["readmitted_30d"] = 0
    adm["_admit_dt"] = pd.to_datetime(adm["admit_date"])
    for p, grp in adm.groupby("patient_id"):
        idx = grp.index.tolist()
        for i in range(len(idx)-1):
            gap = (adm.loc[idx[i+1],"_admit_dt"] - adm.loc[idx[i],"_disch_dt"]).days
            if 0 <= gap <= 30 and adm.loc[idx[i],"discharge_disposition"] != "Expired":
                adm.loc[idx[i],"readmitted_30d"] = 1
    # Expired cannot be readmitted
    adm.loc[adm["discharge_disposition"]=="Expired","readmitted_30d"] = 0
    adm = adm.drop(columns=["_disch_dt","_admit_dt"])

    patients.to_csv(f"{BASE}/01_hospital_readmissions/data/patients.csv", index=False)
    adm.to_csv(f"{BASE}/01_hospital_readmissions/data/admissions.csv", index=False)
    return patients, adm

# ============================================================
# PROJECT 2 — ED THROUGHPUT
# ============================================================
def project_ed():
    N = 12000
    start = datetime(2025,1,1)
    arrive = [start + timedelta(minutes=int(rng.integers(0, 365*24*60))) for _ in range(N)]
    triage = rng.choice([1,2,3,4,5], N, p=[0.04,0.13,0.38,0.30,0.15])  # ESI level
    arr_mode = rng.choice(["Walk-in","Ambulance","Police","Transfer"], N, p=[0.68,0.24,0.03,0.05])
    # door-to-triage minutes
    d2t = np.clip(rng.gamma(2.0, 6.0, N), 1, None)
    # triage-to-provider depends on acuity and hour (busier evenings)
    hour = np.array([a.hour for a in arrive])
    busy = np.isin(hour, range(10,23)).astype(float)
    base_wait = np.where(triage<=2, 8, np.where(triage==3, 35, 70))
    t2p = np.clip(rng.gamma(2.0, base_wait/2.0) * (1+0.4*busy), 1, None)
    # length of stay in ED minutes
    los = np.clip(rng.gamma(3.0, np.where(triage<=2, 120, 70)/2.0) + t2p, 20, 1400)
    disposition = []
    for t in triage:
        if t <= 2:
            disposition.append(rng.choice(["Admitted","Transferred","Discharged"], p=[0.62,0.10,0.28]))
        elif t == 3:
            disposition.append(rng.choice(["Admitted","Discharged","Transferred"], p=[0.22,0.74,0.04]))
        else:
            disposition.append(rng.choice(["Discharged","LWBS","Admitted"], p=[0.93,0.05,0.02]))
    disposition = np.array(disposition)
    # LWBS visits have short LOS, no provider time
    lwbs = disposition=="LWBS"
    los = np.where(lwbs, np.clip(rng.gamma(2.0, 25, N),10,300), los)
    chief = rng.choice(["Chest Pain","Abdominal Pain","Shortness of Breath","Laceration","Fever",
                        "Headache","Fracture","Fall","Back Pain","Allergic Reaction"], N)
    age = np.clip(rng.normal(45,22,N).round().astype(int),0,99)
    gender = rng.choice(["Female","Male"], N, p=[0.51,0.49])

    df = pd.DataFrame({
        "visit_id": np.arange(700001, 700001+N),
        "arrival_datetime": [a.strftime("%Y-%m-%d %H:%M") for a in arrive],
        "arrival_hour": hour,
        "day_of_week": [a.strftime("%A") for a in arrive],
        "arrival_mode": arr_mode,
        "esi_triage_level": triage,
        "chief_complaint": chief,
        "patient_age": age,
        "patient_gender": gender,
        "door_to_triage_min": d2t.round(1),
        "triage_to_provider_min": np.where(lwbs, np.nan, t2p.round(1)),
        "ed_los_min": los.round(1),
        "disposition": disposition,
        "left_without_being_seen": lwbs.astype(int),
        "boarding_min": np.where(disposition=="Admitted", np.clip(rng.gamma(2.0,90,N),0,1000).round(1), 0),
    })
    df.to_csv(f"{BASE}/02_ed_throughput/data/ed_visits.csv", index=False)
    return df

# ============================================================
# PROJECT 3 — CLAIMS DENIALS / REVENUE CYCLE
# ============================================================
def project_claims():
    N = 15000
    start = datetime(2025,1,1)
    payers = ["Medicare","Medicaid","Aetna","UnitedHealth","BlueCross","Cigna","Humana","Self-Pay"]
    payer = rng.choice(payers, N, p=[0.24,0.14,0.12,0.13,0.14,0.09,0.08,0.06])
    dept = rng.choice(["Cardiology","Orthopedics","Radiology","Emergency","Oncology","Primary Care","Surgery","Lab"], N)
    cpt = rng.choice(["99213","99285","93000","70450","80053","27447","99214","71046","36415","99223"], N)
    svc_date = [start + timedelta(days=int(rng.integers(0,365))) for _ in range(N)]
    submit_lag = rng.integers(1,21,N)
    submit_date = [s+timedelta(days=int(l)) for s,l in zip(svc_date, submit_lag)]
    billed = np.clip(rng.lognormal(6.6,0.7,N),60,None).round(2)

    # Denial probability varies by payer and department
    payer_risk = {"Medicaid":0.22,"Self-Pay":0.30,"Humana":0.16,"Aetna":0.14,"Cigna":0.15,
                  "UnitedHealth":0.13,"BlueCross":0.12,"Medicare":0.10}
    pr = np.array([payer_risk[p] for p in payer])
    pr = np.clip(pr + np.where(dept=="Radiology",0.05,0) + np.where(dept=="Emergency",0.04,0), 0.03, 0.5)
    denied = rng.random(N) < pr

    denial_reasons = ["Prior Auth Missing","Coding Error","Not Medically Necessary",
                      "Eligibility/Coverage","Duplicate Claim","Timely Filing","Missing Documentation"]
    reason = np.where(denied, rng.choice(denial_reasons, N,
                       p=[0.24,0.18,0.14,0.15,0.08,0.09,0.12]), "")
    # status
    status = np.where(denied,
                rng.choice(["Denied","Appealed-Paid","Appealed-Denied","Written Off"], N, p=[0.40,0.30,0.15,0.15]),
                rng.choice(["Paid","Paid"], N))
    # allowed/paid amounts
    allowed_ratio = np.clip(rng.normal(0.62,0.12,N),0.2,0.95)
    paid = np.where(np.isin(status,["Paid","Appealed-Paid"]), (billed*allowed_ratio).round(2), 0.0)
    # days to payment for paid claims
    pay_days = np.where(paid>0, np.clip(rng.gamma(3.0,12,N),5,180).round().astype(int), 0)
    paid_date = [ (sd+timedelta(days=int(d))).strftime("%Y-%m-%d") if d>0 else "" for sd,d in zip(submit_date, pay_days)]

    df = pd.DataFrame({
        "claim_id": np.arange(900001, 900001+N),
        "service_date": [d.strftime("%Y-%m-%d") for d in svc_date],
        "submit_date": [d.strftime("%Y-%m-%d") for d in submit_date],
        "paid_date": paid_date,
        "payer": payer,
        "department": dept,
        "cpt_code": cpt,
        "billed_amount": billed,
        "paid_amount": paid,
        "claim_status": status,
        "is_denied": denied.astype(int),
        "denial_reason": reason,
        "days_to_payment": pay_days,
    })
    df.to_csv(f"{BASE}/03_claims_denials/data/claims.csv", index=False)
    return df

p, a = project_readmissions()
e = project_ed()
c = project_claims()

print("READMISSIONS: patients", p.shape, "admissions", a.shape, "30d rate", round(a.readmitted_30d.mean()*100,1),"%")
print("ED: visits", e.shape, "LWBS rate", round(e.left_without_being_seen.mean()*100,1),"%")
print("CLAIMS: rows", c.shape, "denial rate", round(c.is_denied.mean()*100,1),"%",
      "net collected $", round(c.paid_amount.sum()/1e6,1),"M of billed $", round(c.billed_amount.sum()/1e6,1),"M")
