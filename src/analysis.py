# %% [markdown]
# # What makes a client land interviews? (practice project, example data)
# All figures are made-up example data built to match the brief's totals. They are not real Vanta statistics.

# %% 1. Load and clean
import numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path
ROOT = Path.cwd() if (Path.cwd() / "data").exists() else Path.cwd().parent
raw = pd.read_csv(ROOT / "data/raw/clients_raw.csv")
print("raw rows:", len(raw))
df = raw.drop_duplicates().copy()                                   # 1 duplicated export row
print("after removing duplicates:", len(df))
df["signup_date"] = pd.to_datetime(df["signup_date"], format="mixed", dayfirst=True)   # mixed formats
df["channel"] = (df["channel"].str.strip().str.lower()
                 .replace({"referal": "referral"}).str.title().replace({"Linkedin": "LinkedIn"}))
df["target_role"] = df["target_role"].fillna("Unknown")
df.loc[df["days_active"] > 31, "days_active"] = np.nan              # impossible value
df.loc[df["days_since_last_activity"] < 0, "days_since_last_activity"] = np.nan   # entry error
df["apps_per_week"] = (df["applications_sent"] / 4.3).round(1)
df["interview_rate"] = np.where(df["applications_sent"] > 0, df["interviews"] / df["applications_sent"], np.nan)
df["got_interview"] = (df["interviews"] > 0).astype(int)
df.to_csv(ROOT / "data/clean/clients_clean.csv", index=False)
print(df[["applications_sent","rejections","no_reply","interviews"]].sum().to_dict())
print("missing values left:\n", df.isna().sum()[df.isna().sum() > 0])

# %% 2. Funnel
app = df[df.applications_sent > 0]
funnel = pd.Series({
    "Signed up": len(df),
    "Active": int(df.active.sum()),
    "Added a job": int((df.jobs_added > 0).sum()),
    "Built a CV": int((df.cvs_built > 0).sum()),
    "Sent an application": len(app),
    "Got a reply": int(((df.rejections + df.interviews) > 0).sum()),
    "Got an interview": int((df.interviews > 0).sum()),
})
print(funnel)
volume = pd.Series({"Jobs added": df.jobs_added.sum(), "CVs built": df.cvs_built.sum(),
                    "Applications": df.applications_sent.sum(),
                    "Replies": (df.rejections + df.interviews).sum(), "Interviews": df.interviews.sum()})
print(volume)
fig, ax = plt.subplots(figsize=(8, 4.2))
bars = ax.barh(funnel.index[::-1], funnel.values[::-1], color="#2f6f8f")
for b, v in zip(bars, funnel.values[::-1]):
    ax.text(v + 1, b.get_y() + b.get_height()/2, f"{v}  ({v/80:.0%})", va="center", fontsize=9)
ax.set_xlim(0, 95); ax.set_title("Client funnel, example month (80 sign-ups)", loc="left", fontsize=11)
ax.spines[["top","right"]].set_visible(False); plt.tight_layout()
plt.savefig(ROOT / "charts/01_client_funnel.png", dpi=160); plt.close()

# %% 3. Which habits go with interviews?
def rate_by(col, bins, labels, frame=app):
    g = frame.groupby(pd.cut(frame[col], bins=bins, labels=labels, right=False), observed=False)
    return pd.DataFrame({"clients": g.size(), "apps": g.applications_sent.sum(),
                         "interviews": g.interviews.sum(),
                         "interview_rate": (g.interviews.sum() / g.applications_sent.sum()).round(3),
                         "share_with_interview": g.got_interview.mean().round(2)})
fu = app.copy()
fu["followup_band"] = np.select(
    [fu.followup_rate.fillna(0) == 0, fu.avg_days_to_followup <= 4, fu.avg_days_to_followup <= 7],
    ["Never follows up", "Within 4 days", "5-7 days"], "8+ days")
by_fu = fu.groupby("followup_band").agg(clients=("client_id","count"), apps=("applications_sent","sum"),
            interviews=("interviews","sum"), share_with_interview=("got_interview","mean"))
by_fu["interview_rate"] = (by_fu.interviews / by_fu.apps).round(3)
by_fu = by_fu.loc[["Within 4 days","5-7 days","8+ days","Never follows up"]]
print("\nBy follow-up speed\n", by_fu)
by_vol = rate_by("apps_per_week", [0, 2, 4, 6, 100], ["<2 a week", "2-4", "4-6", "6+"])
print("\nBy weekly volume\n", by_vol)
by_cv = rate_by("avg_cv_match_score", [0, 60, 70, 80, 100], ["<60", "60-69", "70-79", "80+"])
print("\nBy CV match score\n", by_cv)

fig, axes = plt.subplots(1, 3, figsize=(12, 3.8), sharey=True)
for ax, tbl, title in zip(axes, [by_fu, by_vol, by_cv],
                          ["Follow-up speed", "Applications per week", "Avg CV match score"]):
    vals = tbl["interview_rate"].fillna(0) * 100
    ax.bar(tbl.index.astype(str), vals, color="#2f6f8f")
    for i, (v, n) in enumerate(zip(vals, tbl["clients"])):
        ax.text(i, v + 0.4, f"{v:.0f}%\n(n={n})", ha="center", fontsize=8)
    ax.set_title(title, fontsize=10); ax.tick_params(axis="x", labelsize=8, rotation=15)
    ax.spines[["top","right"]].set_visible(False)
axes[0].set_ylabel("Interviews per 100 applications")
fig.suptitle("Which habits go with interviews?", x=0.01, ha="left", fontsize=11)
plt.tight_layout(); plt.savefig(ROOT / "charts/02_habits_vs_interviews.png", dpi=160); plt.close()

corr = app[["apps_per_week","avg_cv_match_score","followup_rate","avg_days_to_followup","days_active","interview_rate"]].corr(method="spearman")["interview_rate"].round(2)
print("\nSpearman correlation with interview rate\n", corr.drop("interview_rate"))

# %% 4. Early-warning model: which active clients are at risk of going quiet?
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.metrics import roc_auc_score, confusion_matrix
act = df[df.active == 1].copy()
features = ["apps_first_14d", "logins_first_14d", "followed_up_first_14d", "replies_first_14d"]
X, y = act[features], act["went_quiet"].astype(int)
model = make_pipeline(StandardScaler(), LogisticRegression(class_weight="balanced", max_iter=1000))
cv = StratifiedKFold(5, shuffle=True, random_state=1)
p = cross_val_predict(model, X, y, cv=cv, method="predict_proba")[:, 1]
print("went quiet:", int(y.sum()), "of", len(y), "active clients")
print("cross-validated AUC:", round(roc_auc_score(y, p), 2))
pred = (p >= 0.5).astype(int)
print("confusion matrix [[stayed-not flagged, stayed-flagged],[quiet-not flagged, quiet-flagged]]\n", confusion_matrix(y, pred))
model.fit(X, y)
coefs = pd.Series(model[-1].coef_[0], index=features).sort_values()
print("\nstandardised coefficients (negative = protects against going quiet)\n", coefs.round(2))
act["risk_score"] = model.predict_proba(X)[:, 1].round(2)
# simple rule a coach could use without a model
act["rule_flag"] = ((act.apps_first_14d < 5) & (act.followed_up_first_14d == 0)).astype(int)
rule = pd.crosstab(act.rule_flag, act.went_quiet, margins=True)
print("\nsimple rule: fewer than 5 applications AND no follow-up in first 14 days\n", rule)
act.sort_values("risk_score", ascending=False)[["client_id"] + features + ["risk_score","rule_flag","went_quiet"]].head(10).to_csv(ROOT / "data/clean/at_risk_top10.csv", index=False)

fig, ax = plt.subplots(figsize=(6.5, 3.2))
labels = {"apps_first_14d": "Applications in first 14 days", "logins_first_14d": "Logins in first 14 days",
          "followed_up_first_14d": "Followed up in first 14 days", "replies_first_14d": "Replies in first 14 days"}
ax.barh([labels[i] for i in coefs.index], coefs.values, color=["#2f6f8f" if v < 0 else "#c0504d" for v in coefs.values])
ax.axvline(0, color="#333", lw=0.8)
ax.set_title("What lowers the risk of going quiet (model weights)", loc="left", fontsize=10)
ax.spines[["top","right"]].set_visible(False); plt.tight_layout()
plt.savefig(ROOT / "charts/03_at_risk_model.png", dpi=160); plt.close()

# %% 5. Numbers behind the recommendations
never_active = int((df.active == 0).sum()); active_no_apply = int(((df.active == 1) & (df.applications_sent == 0)).sum())
print({"never_active": never_active, "active_but_no_application": active_no_apply,
       "appliers_without_interview": int(((df.applications_sent > 0) & (df.interviews == 0)).sum()),
       "no_reply_share": round(df.no_reply.sum() / df.applications_sent.sum(), 2),
       "overall_interview_rate": round(df.interviews.sum() / df.applications_sent.sum(), 3)})
