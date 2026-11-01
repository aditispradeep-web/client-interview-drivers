# Business Requirements Document: client interview drivers

*Practice project with example data. Written in a format that can be pasted into Confluence.*

| | |
|---|---|
| **Sponsor** | Dylan Corrigan, Vanta (career coaching) |
| **Business analyst** | Aditi Seena Pradeep |
| **Status** | Analysis complete, awaiting review |
| **Data** | Example month: 80 clients, made-up figures matching the brief |

## 1. Background
Vanta helps job seekers track applications, tailor CVs and follow up. About 1 in 10 applications led to an interview in the example month, but results were uneven: 15 clients applied and never got an interview, and 5 active clients sent nothing.

## 2. Business objectives
1. Understand which client habits go with landing interviews.
2. Spot clients at risk of going quiet early enough for a coach to step in.
3. Recommend product or coaching changes that raise interviews per client.

## 3. Stakeholders
| Stakeholder | Interest |
|---|---|
| Founder / product owner | Which features to change first |
| Coaches | Who to contact and when |
| Clients | More interviews for the same effort |

## 4. Scope
**In scope:** client funnel, habit analysis, early-warning rule, dashboard, recommendations.
**Out of scope:** pricing, marketing acquisition, real client data (this round uses example data).

## 5. Current process (as-is)
Sign up → onboarding → add a job → build a tailored CV → apply → follow-up reminder → reply or no reply → interview. See `client_journey_process_map.png` for where clients drop off.

## 6. Requirements
| ID | Requirement | Priority | Jira |
|---|---|---|---|
| BR-1 | One clean, trusted row per client, matching source totals | Must | Story 2 |
| BR-2 | Funnel from sign-up to interview, with counts and % at each stage | Must | Story 3 |
| BR-3 | Interview rate by follow-up speed, volume and CV match score | Must | Story 4 |
| BR-4 | Early-warning flag using only the first 14 days of activity | Should | Story 5 |
| BR-5 | Self-service dashboard with channel and role filters | Should | Story 6 |
| BR-6 | Three prioritised recommendations, with limits stated | Must | Story 7 |

## 7. Findings summary
- Almost a third of sign-ups never sent a first application.
- Following up within 4 days: 12.8 interviews per 100 applications. Never following up: 2.5.
- CV match 80+: 15.3 per 100. Under 60: 2.9. Volume barely changed the hit rate.
- A day-14 rule (under 5 applications and no follow-up) caught 15 of the 16 clients who went quiet.

## 8. Recommendations (to-be)
1. First application within 48 hours of sign-up, with a day-3 nudge.
2. Follow-up prompt on day 4 with a ready-written note. A/B test it first.
3. Coach check-in at day 14 for flagged clients, and a CV match target of 70+.

## 9. Success measures
| Measure | Example baseline | Target to test |
|---|---|---|
| Sign-ups reaching a first application | 69% | 80% |
| Applications sent by clients who usually follow up within 4 days | 52% | 70% |
| Clients who go quiet | 16 of 60 active | Under 10 |

## 10. Assumptions and risks
- Example data. Patterns are hypotheses until checked on real data.
- These are correlations. Motivated clients may do everything better, so changes should be A/B tested.
- Small sample (80 clients).
