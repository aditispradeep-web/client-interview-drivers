# Project backlog (Jira)

Planned in Jira as one epic with 6 user stories and 2 tasks across two sprints. Import `backlog_jira_import.csv` with Jira's CSV importer (map Issue Id and Parent Id to keep the epic link).

## Epic: Understand why some clients get interviews

Practice project (example data). Goal: find which job-search habits go with interviews and flag clients at risk of going quiet.

## Story: As a coach, I want one clean row per client so that I can trust the analysis
*Sprint 1 · 3 points · priority High*

Acceptance criteria:
- 80 rows, one per client, no duplicates
- Dates in one format; channel labels standardised
- Impossible values (31+ active days, negative gaps) set to missing, not guessed
- Totals match the brief: 797 applications, 200 rejections, 517 no reply, 80 interviews

## Story: As a manager, I want a funnel from sign-up to interview so that I can see where clients drop off
*Sprint 1 · 3 points · priority High*

Acceptance criteria:
- Stages: signed up, active, added a job, built a CV, applied, got a reply, got an interview
- Counts and % of sign-ups shown for each stage
- Volume view: jobs, CVs, applications, replies, interviews

## Story: As a coach, I want to see which habits go with interviews so that I know what to encourage
*Sprint 1 · 5 points · priority High*

Acceptance criteria:
- Interviews per 100 applications by follow-up speed, weekly volume and CV match score
- Client counts shown for every group
- Missing values excluded from that cut only, and noted

## Story: As a coach, I want an early warning for clients likely to go quiet so that I can check in before they drop out
*Sprint 2 · 5 points · priority Medium*

Acceptance criteria:
- Uses only signals from the first 14 days
- Model is explainable (weights shown) and cross-validated
- A simple rule a coach can apply without the model, with how many it catches and how many false alarms

## Story: As a manager, I want a Power BI dashboard so that I can explore the findings myself
*Sprint 2 · 3 points · priority Medium*

Acceptance criteria:
- KPI cards: sign-ups, active, applications, interviews, interview rate, no-reply share
- Funnel, follow-up and CV match charts
- At-risk client table with slicers for channel and target role
- Page title says the data is example data

## Story: As Vanta, I want three recommendations so that I know what to change first
*Sprint 2 · 2 points · priority High*

Acceptance criteria:
- Each recommendation linked to one finding
- Limits stated: example data, small sample, correlation not causation
- Next step proposed (A/B test of the day-4 follow-up prompt)

## Task: Present findings to Dylan and capture feedback
*Sprint 2 · 1 points · priority Medium*

Acceptance criteria:
- 9-slide deck: problem, data, findings, recommendations, limits
- Feedback logged as new backlog items

## Task: Publish to GitHub and LinkedIn as a practice project
*Sprint 2 · 1 points · priority Low*

Acceptance criteria:
- README states it is example data
- Repo link added to CV Projects section and LinkedIn
