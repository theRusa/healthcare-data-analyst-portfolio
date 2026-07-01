"""Render a polished dashboard PNG per project for the README headers."""
import pandas as pd, numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import gridspec

BASE="/sessions/stoic-beautiful-archimedes/mnt/Portfolio"
NAVY="#1F3864"; BLUE="#2E5496"; LBLUE="#8FAADC"; ACCENT="#C00000"; GREY="#F2F2F2"
plt.rcParams.update({"font.family":"DejaVu Sans","font.size":10,"axes.edgecolor":"#BFBFBF",
                     "axes.linewidth":0.8,"axes.grid":True,"grid.color":"#E7E7E7","grid.linewidth":0.7})

def kpi(ax, label, value):
    ax.axis("off")
    ax.add_patch(plt.Rectangle((0,0),1,1,transform=ax.transAxes,facecolor=GREY,edgecolor="#D0D0D0",lw=1))
    ax.text(0.5,0.62,value,ha="center",va="center",fontsize=20,fontweight="bold",color=NAVY,transform=ax.transAxes)
    ax.text(0.5,0.24,label,ha="center",va="center",fontsize=9,color="#595959",transform=ax.transAxes)

def header(fig, title, sub):
    fig.text(0.012,0.965,title,fontsize=19,fontweight="bold",color=NAVY,ha="left")
    fig.text(0.012,0.935,sub,fontsize=10.5,color="#595959",ha="left")
    fig.text(0.988,0.95,"Synthetic data · portfolio demo",fontsize=8.5,color="#9A9A9A",ha="right")

# ---------- 1. READMISSIONS ----------
def dash_readmissions():
    adm=pd.read_csv(f"{BASE}/01_hospital_readmissions/data/admissions.csv")
    pat=pd.read_csv(f"{BASE}/01_hospital_readmissions/data/patients.csv")
    e=adm[adm.discharge_disposition!="Expired"]
    rate=e.readmitted_30d.mean()*100
    fig=plt.figure(figsize=(13,7.3)); fig.patch.set_facecolor("white")
    gs=gridspec.GridSpec(3,4,height_ratios=[0.85,1.5,1.5],hspace=0.55,wspace=0.42,
                         left=0.12,right=0.965,top=0.88,bottom=0.09)
    header(fig,"Hospital Readmissions — Executive Dashboard","30-day all-cause readmissions across 9,000 admissions")
    for i,(l,v) in enumerate([("Total Discharges",f"{len(e):,}"),("30-Day Readmissions",f"{int(e.readmitted_30d.sum()):,}"),
                              ("Readmission Rate",f"{rate:.1f}%"),("Avg Length of Stay",f"{adm.length_of_stay_days.mean():.1f}d")]):
        kpi(fig.add_subplot(gs[0,i]),l,v)
    # by diagnosis
    ax=fig.add_subplot(gs[1,:2])
    g=(e.groupby("primary_diagnosis").readmitted_30d.mean()*100).sort_values()
    cols=[ACCENT if v>=15 else BLUE for v in g.values]
    ax.barh(g.index,g.values,color=cols); ax.axvline(15,color=ACCENT,ls="--",lw=1)
    ax.set_title("Readmission Rate by Diagnosis (%)",fontsize=11,fontweight="bold",color=NAVY,loc="left")
    ax.text(15.1,0.2,"15% benchmark",color=ACCENT,fontsize=8)
    # by LOS band
    ax2=fig.add_subplot(gs[1,2:])
    bands=pd.cut(e.length_of_stay_days,[0,2,5,9,999],labels=["1-2d","3-5d","6-9d","10+d"])
    g2=(e.groupby(bands,observed=True).readmitted_30d.mean()*100)
    ax2.bar(g2.index.astype(str),g2.values,color=BLUE)
    ax2.set_title("Readmission Rate by Length of Stay (%)",fontsize=11,fontweight="bold",color=NAVY,loc="left")
    # monthly trend
    ax3=fig.add_subplot(gs[2,:2])
    e2=e.copy(); e2["m"]=pd.to_datetime(e2.discharge_date).dt.to_period("M").astype(str)
    t=(e2.groupby("m").readmitted_30d.mean()*100).iloc[:-1]  # drop final month (incomplete 30-day window)
    ax3.plot(range(len(t)),t.values,marker="o",color=NAVY,lw=2); ax3.axhline(15,color=ACCENT,ls="--",lw=1)
    ax3.set_xticks(range(0,len(t),3)); ax3.set_xticklabels(t.index[::3],rotation=45,ha="right",fontsize=8)
    ax3.set_title("Monthly Readmission Rate Trend (%)",fontsize=11,fontweight="bold",color=NAVY,loc="left")
    # by disposition
    ax4=fig.add_subplot(gs[2,2:])
    g4=(e.groupby("discharge_disposition").readmitted_30d.mean()*100).sort_values()
    ax4.barh(g4.index,g4.values,color=LBLUE)
    ax4.set_title("Readmission Rate by Discharge Disposition (%)",fontsize=11,fontweight="bold",color=NAVY,loc="left")
    fig.savefig(f"{BASE}/01_hospital_readmissions/images/dashboard.png",dpi=130,facecolor="white")
    plt.close(fig)

# ---------- 2. ED THROUGHPUT ----------
def dash_ed():
    ed=pd.read_csv(f"{BASE}/02_ed_throughput/data/ed_visits.csv")
    fig=plt.figure(figsize=(13,7.3)); fig.patch.set_facecolor("white")
    gs=gridspec.GridSpec(3,4,height_ratios=[0.85,1.5,1.5],hspace=0.6,wspace=0.3,
                         left=0.06,right=0.965,top=0.88,bottom=0.1)
    header(fig,"Emergency Department Throughput — Dashboard","Patient flow across 12,000 ED visits")
    los=ed.ed_los_min.mean()
    for i,(l,v) in enumerate([("Total Visits",f"{len(ed):,}"),("Avg ED LOS",f"{los:.0f} min"),
                              ("LWBS Rate",f"{ed.left_without_being_seen.mean()*100:.1f}%"),
                              ("% Under 4h",f"{(ed.ed_los_min<=240).mean()*100:.0f}%")]):
        kpi(fig.add_subplot(gs[0,i]),l,v)
    ax=fig.add_subplot(gs[1,:2])
    g=ed.groupby("arrival_hour").size()
    ax.fill_between(g.index,g.values,color=LBLUE,alpha=0.7); ax.plot(g.index,g.values,color=NAVY,lw=1.8)
    ax.set_title("Visit Volume by Hour of Day",fontsize=11,fontweight="bold",color=NAVY,loc="left"); ax.set_xlabel("Hour")
    ax2=fig.add_subplot(gs[1,2:])
    g2=ed.groupby("esi_triage_level").triage_to_provider_min.mean()
    ax2.bar(g2.index.astype(str),g2.values,color=[ACCENT if i<=2 else BLUE for i in g2.index])
    ax2.set_title("Avg Wait to Provider by ESI Level (min)",fontsize=11,fontweight="bold",color=NAVY,loc="left")
    ax2.set_xlabel("ESI triage level (1=most acute)")
    ax3=fig.add_subplot(gs[2,:2])
    order=["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
    g3=ed.groupby("day_of_week").size().reindex(order)
    ax3.bar(range(7),g3.values,color=BLUE); ax3.set_xticks(range(7)); ax3.set_xticklabels([d[:3] for d in order])
    ax3.set_title("Visit Volume by Day of Week",fontsize=11,fontweight="bold",color=NAVY,loc="left")
    ax4=fig.add_subplot(gs[2,2:])
    bins=pd.cut(ed.ed_los_min,[0,60,120,240,5000],labels=["0-60","61-120","121-240","240+"])
    g4=ed.groupby(bins,observed=True).size()
    ax4.bar(g4.index.astype(str),g4.values,color=LBLUE); ax4.axvline(2.5,color=ACCENT,ls="--",lw=1)
    ax4.set_title("ED Length-of-Stay Distribution (min)",fontsize=11,fontweight="bold",color=NAVY,loc="left")
    fig.savefig(f"{BASE}/02_ed_throughput/images/dashboard.png",dpi=130,facecolor="white")
    plt.close(fig)

# ---------- 3. CLAIMS DENIALS ----------
def dash_claims():
    cl=pd.read_csv(f"{BASE}/03_claims_denials/data/claims.csv")
    fig=plt.figure(figsize=(13,7.3)); fig.patch.set_facecolor("white")
    gs=gridspec.GridSpec(3,4,height_ratios=[0.85,1.5,1.5],hspace=0.6,wspace=0.5,
                         left=0.13,right=0.965,top=0.88,bottom=0.12)
    header(fig,"Claims Denials & Revenue Cycle — Dashboard","15,000 claims · denial and collection performance")
    ncr=cl.paid_amount.sum()/cl.billed_amount.sum()*100
    for i,(l,v) in enumerate([("Total Billed",f"${cl.billed_amount.sum()/1e6:.1f}M"),
                              ("Total Collected",f"${cl.paid_amount.sum()/1e6:.1f}M"),
                              ("Net Collection",f"{ncr:.0f}%"),("Denial Rate",f"{cl.is_denied.mean()*100:.1f}%")]):
        kpi(fig.add_subplot(gs[0,i]),l,v)
    ax=fig.add_subplot(gs[1,:2])
    g=(cl.groupby("payer").is_denied.mean()*100).sort_values()
    ax.barh(g.index,g.values,color=BLUE)
    ax.set_title("Denial Rate by Payer (%)",fontsize=11,fontweight="bold",color=NAVY,loc="left")
    ax2=fig.add_subplot(gs[1,2:])
    r=cl[cl.is_denied==1].denial_reason.value_counts().sort_values()
    ax2.barh(r.index,r.values,color=[ACCENT if i>=len(r)-2 else LBLUE for i in range(len(r))])
    ax2.set_title("Denials by Reason (count)",fontsize=11,fontweight="bold",color=NAVY,loc="left")
    ax3=fig.add_subplot(gs[2,:2])
    cl2=cl.copy(); cl2["m"]=pd.to_datetime(cl2.service_date).dt.to_period("M").astype(str)
    t=(cl2.groupby("m").is_denied.mean()*100)
    ax3.plot(range(len(t)),t.values,marker="o",color=NAVY,lw=2)
    ax3.set_xticks(range(0,len(t),2)); ax3.set_xticklabels(t.index[::2],rotation=45,ha="right",fontsize=8)
    ax3.set_title("Monthly Denial Rate Trend (%)",fontsize=11,fontweight="bold",color=NAVY,loc="left")
    ax4=fig.add_subplot(gs[2,2:])
    paid=cl[cl.paid_amount>0]
    buckets=pd.cut(paid.days_to_payment,[0,30,60,90,9999],labels=["0-30","31-60","61-90","90+"])
    g4=paid.groupby(buckets,observed=True).paid_amount.sum()/1e6
    ax4.bar(g4.index.astype(str),g4.values,color=LBLUE)
    ax4.set_title("Collected $ by Days-to-Payment (millions)",fontsize=11,fontweight="bold",color=NAVY,loc="left")
    fig.savefig(f"{BASE}/03_claims_denials/images/dashboard.png",dpi=130,facecolor="white")
    plt.close(fig)

import os
for p in ["01_hospital_readmissions","02_ed_throughput","03_claims_denials"]:
    os.makedirs(f"{BASE}/{p}/images",exist_ok=True)
dash_readmissions(); dash_ed(); dash_claims()
print("dashboards rendered")
