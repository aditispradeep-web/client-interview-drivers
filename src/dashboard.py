"""One-page dashboard image for the practice project (example data)."""
import numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
df = pd.read_csv(ROOT / "data/clean/clients_clean.csv")
app = df[df.applications_sent > 0].copy()

DARK, ACC, WARN, MUTED, BG, CARD = "#16263A", "#2F6F8F", "#B5651D", "#5B6B7A", "#F7F6F2", "#FFFFFF"
plt.rcParams.update({"font.family": "DejaVu Sans", "text.color": DARK, "axes.labelcolor": DARK,
                     "xtick.color": MUTED, "ytick.color": MUTED})
fig = plt.figure(figsize=(16, 9), dpi=150, facecolor=BG)
gs = fig.add_gridspec(3, 6, height_ratios=[0.55, 1.6, 1.6], hspace=0.55, wspace=0.75,
                      left=0.085, right=0.98, top=0.86, bottom=0.07)
fig.text(0.085, 0.95, "What makes a client land interviews?", fontsize=22, fontweight="bold")
fig.text(0.085, 0.905, "Example month · 80 clients · practice project with example data, not real Vanta statistics",
         fontsize=11, color=MUTED)

kpis = [("Sign-ups", f"{len(df)}"), ("Active", f"{int(df.active.sum())}"),
        ("Applications", f"{int(df.applications_sent.sum())}"), ("Interviews", f"{int(df.interviews.sum())}"),
        ("Interview rate", f"{df.interviews.sum()/df.applications_sent.sum():.0%}"),
        ("No reply", f"{df.no_reply.sum()/df.applications_sent.sum():.0%}")]
for i, (lab, val) in enumerate(kpis):
    ax = fig.add_subplot(gs[0, i]); ax.set_facecolor(CARD); ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values(): s.set_color("#DCE3E8")
    ax.text(0.08, 0.62, val, fontsize=24, fontweight="bold", color=ACC if lab != "No reply" else WARN, transform=ax.transAxes, va="center")
    ax.text(0.08, 0.2, lab, fontsize=11, color=MUTED, transform=ax.transAxes, va="center")

# Funnel
ax = fig.add_subplot(gs[1:, 0:2]); ax.set_facecolor(BG)
stages = ["Signed up", "Active", "Added a job", "Built a CV", "Applied", "Got a reply", "Interview"]
vals = [len(df), int(df.active.sum()), int((df.jobs_added > 0).sum()), int((df.cvs_built > 0).sum()),
        len(app), int(((df.rejections + df.interviews) > 0).sum()), int((df.interviews > 0).sum())]
cols = [WARN if s == "Active" else ACC for s in stages]
ax.barh(stages[::-1], vals[::-1], color=cols[::-1])
for y, v in enumerate(vals[::-1]): ax.text(v + 1, y, f"{v} ({v/80:.0%})", va="center", fontsize=10)
ax.set_xlim(0, 100); ax.set_xticks([]); ax.spines[["top", "right", "bottom"]].set_visible(False)
ax.set_title("Funnel: the biggest drop is before applying", loc="left", fontsize=12, fontweight="bold")

# Follow-up habit
band = np.select([app.followup_rate.fillna(0) == 0, app.avg_days_to_followup <= 4, app.avg_days_to_followup <= 7],
                 ["Never", "≤4 days", "5–7 days"], "8+ days")
fu = app.assign(b=band).groupby("b").agg(a=("applications_sent", "sum"), i=("interviews", "sum"), n=("client_id", "count"))
fu = fu.loc[["≤4 days", "5–7 days", "8+ days", "Never"]]; r = 100 * fu.i / fu.a
ax = fig.add_subplot(gs[1, 2:4]); ax.set_facecolor(BG)
ax.bar(fu.index, r, color=[ACC, ACC, ACC, WARN])
for x, (v, n) in enumerate(zip(r, fu.n)): ax.text(x, v + 0.3, f"{v:.1f}\n(n={n})", ha="center", fontsize=9)
ax.set_ylim(0, 16); ax.set_ylabel("Interviews per 100 apps", fontsize=9); ax.spines[["top", "right"]].set_visible(False)
ax.set_title("Follow-up speed", loc="left", fontsize=12, fontweight="bold")

# CV match
cvb = pd.cut(app.avg_cv_match_score, [0, 60, 70, 80, 101], labels=["<60", "60–69", "70–79", "80+"], right=False)
cv = app.assign(b=cvb).dropna(subset=["b"]).groupby("b", observed=False).agg(a=("applications_sent", "sum"), i=("interviews", "sum"), n=("client_id", "count"))
r2 = 100 * cv.i / cv.a
ax = fig.add_subplot(gs[1, 4:6]); ax.set_facecolor(BG)
ax.bar(cv.index.astype(str), r2, color=[WARN, ACC, ACC, ACC])
for x, (v, n) in enumerate(zip(r2, cv.n)): ax.text(x, v + 0.3, f"{v:.1f}\n(n={n})", ha="center", fontsize=9)
ax.set_ylim(0, 19); ax.spines[["top", "right"]].set_visible(False)
ax.set_title("CV match score", loc="left", fontsize=12, fontweight="bold")

# Volume
vb = pd.cut(app.apps_per_week, [0, 2, 4, 6, 100], labels=["<2/wk", "2–4", "4–6", "6+"], right=False)
vo = app.assign(b=vb).groupby("b", observed=False).agg(a=("applications_sent", "sum"), i=("interviews", "sum"), n=("client_id", "count"))
r3 = 100 * vo.i / vo.a
ax = fig.add_subplot(gs[2, 2:4]); ax.set_facecolor(BG)
ax.bar(vo.index.astype(str), r3, color=ACC)
for x, (v, n) in enumerate(zip(r3, vo.n)): ax.text(x, v + 0.3, f"{v:.1f}\n(n={n})", ha="center", fontsize=9)
ax.set_ylim(0, 16); ax.set_ylabel("Interviews per 100 apps", fontsize=9); ax.spines[["top", "right"]].set_visible(False)
ax.set_title("Volume barely changes the hit rate", loc="left", fontsize=12, fontweight="bold")

# Day-14 rule
act = df[df.active == 1]
flag = (act.apps_first_14d < 5) & (act.followed_up_first_14d == 0)
caught, quiet, flagged = int((flag & (act.went_quiet == 1)).sum()), int((act.went_quiet == 1).sum()), int(flag.sum())
ax = fig.add_subplot(gs[2, 4:6]); ax.set_facecolor(DARK); ax.set_xticks([]); ax.set_yticks([])
for s in ax.spines.values(): s.set_visible(False)
ax.text(0.05, 0.82, "Day-14 early-warning rule", color="#7FC4D6", fontsize=12, fontweight="bold", transform=ax.transAxes)
ax.text(0.05, 0.6, "Under 5 applications and no follow-up by day 14", color="#F7F6F2", fontsize=10.5, transform=ax.transAxes)
ax.text(0.05, 0.3, f"{caught} of {quiet}", color="#F7F6F2", fontsize=30, fontweight="bold", transform=ax.transAxes)
ax.text(0.05, 0.06, f"who went quiet were flagged\n({flagged} flagged in total)", color="#C9D6DF", fontsize=10, transform=ax.transAxes)

fig.savefig(ROOT / "dashboard/dashboard.png", facecolor=BG)
print("saved")
