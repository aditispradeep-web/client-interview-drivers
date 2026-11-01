"""
Generate the EXAMPLE data set for the practice project
"What makes a client land interviews".

These are made-up figures built to match the totals in the project brief.
They are NOT real Vanta statistics.

Brief totals for the example month:
  80 clients signed up, 60 active
  800 jobs added, 797 tailored CVs built
  797 applications sent, by 55 clients
  200 rejections, 517 no reply, 80 interviews across 40 clients
"""
import numpy as np
import pandas as pd
from pathlib import Path

rng = np.random.default_rng(27)
N = 80
ROOT = Path(__file__).resolve().parents[1]

def largest_remainder(weights, total, floor=None, cap=None):
    """Split an integer total in proportion to weights, respecting optional per-row floor and cap."""
    w = np.asarray(weights, float)
    n = len(w)
    floor = np.zeros(n, int) if floor is None else np.asarray(floor, int)
    cap = np.full(n, 10**9) if cap is None else np.asarray(cap, int)
    out = floor.copy()
    remaining = total - out.sum()
    for _ in range(200):
        if remaining <= 0:
            break
        room = cap - out
        ww = np.where(room > 0, w, 0)
        if ww.sum() == 0:
            break
        raw = ww / ww.sum() * remaining
        add = np.minimum(np.floor(raw).astype(int), room)
        if add.sum() == 0:
            order = np.argsort(-(raw - np.floor(raw)) * (room > 0))
            for i in order[:remaining]:
                if room[i] > 0:
                    add[i] += 1
        out += add
        remaining = total - out.sum()
    assert out.sum() == total, (out.sum(), total)
    return out

ids = [f"C{i:03d}" for i in range(1, N + 1)]
signup_day = rng.integers(1, 15, N)                      # signed up in the first half of the month
channel = rng.choice(["LinkedIn", "Referral", "Google", "University"], N, p=[0.4, 0.25, 0.2, 0.15])
target_role = rng.choice(["Data Analyst", "Business Analyst", "Software Engineer", "Marketing", "Finance"], N,
                         p=[0.3, 0.25, 0.2, 0.15, 0.1])

# --- who is active, who applies -------------------------------------------------
order = rng.permutation(N)
inactive = set(order[:20])                               # 20 signed up but never active
active_idx = [i for i in range(N) if i not in inactive]
non_appliers = set(rng.choice(active_idx, 5, replace=False))   # 5 active clients sent nothing
appliers = [i for i in active_idx if i not in non_appliers]    # 55

# habits for appliers (latent "engagement" drives volume, follow-up and CV quality)
eng = rng.normal(0, 1, N)
apps_w = np.exp(0.55 * eng + rng.normal(0, 0.45, N))
apps = np.zeros(N, int)
apps[appliers] = largest_remainder(apps_w[appliers], 797, floor=np.ones(55, int))
# one outlier: a client who bulk-applied
big = appliers[int(np.argmax(apps[appliers]))]

followup_rate = np.clip(0.45 + 0.18 * eng + rng.normal(0, 0.18, N), 0, 1)
followup_days = np.clip(np.round(6 - 1.6 * eng + rng.normal(0, 2.0, N)), 1, 20)
cv_match = np.clip(np.round(68 + 7 * eng + rng.normal(0, 7, N)), 40, 98)
days_active = np.clip(np.round(9 + 4 * eng + rng.normal(0, 3, N)), 1, 30)
# the bulk applier: lots of volume, weak follow-up and lower CV match
followup_rate[big], followup_days[big], cv_match[big] = 0.05, 14, 52
nevers = [i for i in appliers if followup_rate[i] < 0.08]
for i in nevers:
    followup_rate[i] = 0.0

# --- interviews: 80 across 40 clients ---------------------------------------------
quality = (1 / (1 + np.exp(-(0.05 * (cv_match - 68) + 2.2 * (followup_rate - 0.45) - 0.12 * (followup_days - 6)))))
p_int = quality * np.sqrt(np.maximum(apps, 1))
cand = np.array(appliers)
probs = p_int[cand] / p_int[cand].sum()
interviewed = set(rng.choice(cand, 40, replace=False, p=probs))
interviews = np.zeros(N, int)
iv = sorted(interviewed)
interviews[iv] = largest_remainder(apps[iv] * quality[iv] ** 2, 80, floor=np.ones(40, int),
                                   cap=np.maximum(apps[iv] - 1, 1))

# --- rejections (200) and no reply (517) ---------------------------------------------
rest = apps - interviews
rej = np.zeros(N, int)
rej[appliers] = largest_remainder(rest[appliers] * (0.6 + quality[appliers]), 200, cap=rest[appliers])
no_reply = apps - interviews - rej
assert (no_reply >= 0).all() and no_reply.sum() == 517

# --- jobs added and CVs built ---------------------------------------------------------
jobs = apps.copy()
cvs = apps.copy()
na = sorted(non_appliers)
jobs[na[:3]] = 1                                        # 3 non-appliers saved a job but never sent anything
assert jobs.sum() == 800 and cvs.sum() == 797

# --- early signals (first 14 days after sign-up) and going quiet ------------------------
apps_first14 = np.where(apps > 0, np.minimum(apps, np.round(apps * rng.uniform(0.35, 0.7, N))).astype(int), 0)
apps_first14 = np.where((apps > 0) & (apps_first14 == 0), 1, apps_first14)
logins_first14 = np.clip(np.round(4 + 2.2 * eng + rng.normal(0, 1.5, N)), 0, 14).astype(int)
replies_first14 = np.minimum(np.round((rej + interviews) * rng.uniform(0.2, 0.5, N)), apps_first14).astype(int)
followed_up_first14 = ((followup_rate > 0.25) & (followup_days <= 7) & (apps_first14 > 0)).astype(int)

quiet_score = (-0.35 * apps_first14 - 0.45 * logins_first14 - 1.1 * followed_up_first14
               - 0.6 * (replies_first14 > 0) + 1.6 * (interviews == 0) + rng.normal(0, 0.9, N))
went_quiet = np.zeros(N, int)
act = np.array(active_idx)
went_quiet[act[np.argsort(-quiet_score[act])[:16]]] = 1   # 16 of 60 active clients went quiet
last_active_day = np.where(went_quiet == 1, rng.integers(5, 16, N), rng.integers(24, 31, N))
days_since_last = (31 - last_active_day).astype(float)

# inactive clients: nothing at all
for i in inactive:
    for arr in (followup_rate, followup_days, cv_match, days_active):
        arr[i] = np.nan
    logins_first14[i] = rng.integers(0, 2)
    apps_first14[i] = replies_first14[i] = followed_up_first14[i] = 0
    days_since_last[i] = np.nan
for i in non_appliers:
    followup_rate[i] = followup_days[i] = cv_match[i] = np.nan
    days_active[i] = float(rng.integers(1, 4))
for i in appliers:
    if followup_rate[i] == 0:
        followup_days[i] = np.nan                       # never followed up

weeks = 4.3
df = pd.DataFrame({
    "client_id": ids,
    "signup_date": [f"2026-10-{d:02d}" for d in signup_day],
    "channel": channel,
    "target_role": target_role,
    "active": [0 if i in inactive else 1 for i in range(N)],
    "jobs_added": jobs,
    "cvs_built": cvs,
    "applications_sent": apps,
    "apps_per_week": np.round(apps / weeks, 1),
    "avg_cv_match_score": cv_match,
    "followup_rate": np.round(followup_rate, 2),
    "avg_days_to_followup": followup_days,
    "days_active": days_active,
    "apps_first_14d": apps_first14,
    "logins_first_14d": logins_first14,
    "followed_up_first_14d": followed_up_first14,
    "replies_first_14d": replies_first14,
    "rejections": rej,
    "no_reply": no_reply,
    "interviews": interviews,
    "days_since_last_activity": days_since_last,
    "went_quiet": np.where(np.array([i in inactive for i in range(N)]), np.nan, went_quiet),
})
# (clean reference copy not saved; the analysis starts from the raw file)

# --- make it messy, like real exports ---------------------------------------------------
raw = df.copy()
raw["signup_date"] = raw["signup_date"].astype(object)
for i in rng.choice(N, 12, replace=False):                 # mixed date formats
    y, m, d = raw.at[i, "signup_date"].split("-")
    raw.at[i, "signup_date"] = f"{d}/{m}/{y}"
for i in rng.choice(N, 9, replace=False):                  # inconsistent channel labels
    raw.at[i, "channel"] = rng.choice(["linkedin", "Linkedin ", "LINKEDIN", "referal", "google "])
gaps = rng.choice(appliers, 5, replace=False)              # missing CV match scores
raw.loc[gaps, "avg_cv_match_score"] = np.nan
raw.loc[rng.choice(appliers, 3, replace=False), "days_active"] = np.nan
err = appliers[3]
raw.at[err, "days_active"] = 45                            # impossible value (month has 31 days)
err2 = appliers[7]
raw.at[err2, "days_since_last_activity"] = -2              # negative gap, data entry error
raw.at[appliers[11], "target_role"] = None
dup = raw.iloc[[16]].copy()                                # duplicated export row
raw = pd.concat([raw.iloc[:40], dup, raw.iloc[40:]], ignore_index=True)
raw = raw.drop(columns=["apps_per_week"])                  # derived later in cleaning
raw.to_csv(ROOT / "data" / "raw" / "clients_raw.csv", index=False)

print("rows raw:", len(raw), "| totals:", dict(signed_up=N, active=int(df.active.sum()),
      jobs=int(df.jobs_added.sum()), cvs=int(df.cvs_built.sum()), apps=int(df.applications_sent.sum()),
      appliers=int((df.applications_sent > 0).sum()), rejections=int(df.rejections.sum()),
      no_reply=int(df.no_reply.sum()), interviews=int(df.interviews.sum()),
      interviewed_clients=int((df.interviews > 0).sum()), went_quiet=int(np.nansum(df.went_quiet))))
