# Power BI dashboard: build guide (about 45 minutes)

Data: `data/clean/clients_clean.csv` (80 rows, one per client). Example data only.

## 1. Load
Get data → Text/CSV → `clients_clean.csv` → Transform data.
In Power Query, check the types: `signup_date` is Date, and the count columns are Whole number. Rename the query to **Clients**, then Close & Apply.

## 2. Measures (Modelling → New measure)

```
Signed Up = COUNTROWS(Clients)
Active Clients = CALCULATE(COUNTROWS(Clients), Clients[active] = 1)
Clients Added Job = CALCULATE(COUNTROWS(Clients), Clients[jobs_added] > 0)
Clients Built CV = CALCULATE(COUNTROWS(Clients), Clients[cvs_built] > 0)
Clients Applied = CALCULATE(COUNTROWS(Clients), Clients[applications_sent] > 0)
Clients Replied = CALCULATE(COUNTROWS(Clients), Clients[rejections] + Clients[interviews] > 0)
Clients Interviewed = CALCULATE(COUNTROWS(Clients), Clients[interviews] > 0)

Applications = SUM(Clients[applications_sent])
Interviews = SUM(Clients[interviews])
Interview Rate = DIVIDE([Interviews], [Applications])
No Reply Share = DIVIDE(SUM(Clients[no_reply]), [Applications])
Went Quiet = CALCULATE(COUNTROWS(Clients), Clients[went_quiet] = 1)
```

## 3. Calculated columns (for slicing)

```
Follow-up Band =
SWITCH(TRUE(),
    ISBLANK(Clients[followup_rate]), "No applications",
    Clients[followup_rate] = 0, "Never follows up",
    Clients[avg_days_to_followup] <= 4, "Within 4 days",
    Clients[avg_days_to_followup] <= 7, "5-7 days",
    "8+ days")

CV Match Band =
SWITCH(TRUE(),
    ISBLANK(Clients[avg_cv_match_score]), "No score",
    Clients[avg_cv_match_score] < 60, "<60",
    Clients[avg_cv_match_score] < 70, "60-69",
    Clients[avg_cv_match_score] < 80, "70-79",
    "80+")

At Risk (Day 14 Rule) = IF(Clients[active] = 1 && Clients[apps_first_14d] < 5 && Clients[followed_up_first_14d] = 0, "At risk", "OK")
```

## 4. Page layout (one page)

1. **KPI cards:** Signed Up, Active Clients, Applications, Interviews, Interview Rate, No Reply Share.
2. **Funnel visual:** use a small table with Stage and Value (one row per stage measure above). Alternatively, a bar chart sorted from the top stage down.
3. **Clustered column chart:** Follow-up Band on the axis, Interview Rate as the value. Sort it Within 4 days, 5-7 days, 8+ days, Never.
4. **Clustered column chart:** CV Match Band against Interview Rate.
5. **Table "Clients to check in with":** client_id, apps_first_14d, logins_first_14d, followed_up_first_14d, filtered to At Risk = "At risk" and went_quiet not blank.
6. **Slicers:** channel, target_role.

Title the page "What makes a client land interviews (example data)" so nobody mistakes it for real figures.

## 5. What to say when presenting
Start with the funnel, then the follow-up chart, then the at-risk table. Each one leads to one of the three recommendations.
