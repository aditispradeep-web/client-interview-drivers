-- What makes a client land interviews? SQL version of the analysis (SQLite / works in most SQL dialects)
-- Table: clients (one row per client, loaded from data/clean/clients_clean.csv). Example data only.

-- 1. Client funnel
SELECT 'Signed up' AS stage, COUNT(*) AS clients FROM clients
UNION ALL SELECT 'Active', SUM(active) FROM clients
UNION ALL SELECT 'Added a job', SUM(jobs_added > 0) FROM clients
UNION ALL SELECT 'Built a CV', SUM(cvs_built > 0) FROM clients
UNION ALL SELECT 'Sent an application', SUM(applications_sent > 0) FROM clients
UNION ALL SELECT 'Got a reply', SUM(rejections + interviews > 0) FROM clients
UNION ALL SELECT 'Got an interview', SUM(interviews > 0) FROM clients;

-- 2. Interviews per 100 applications by follow-up speed
SELECT CASE
         WHEN COALESCE(followup_rate, 0) = 0 THEN '4. Never follows up'
         WHEN avg_days_to_followup <= 4 THEN '1. Within 4 days'
         WHEN avg_days_to_followup <= 7 THEN '2. 5-7 days'
         ELSE '3. 8+ days' END                                   AS followup_band,
       COUNT(*)                                                  AS clients,
       SUM(applications_sent)                                    AS applications,
       SUM(interviews)                                           AS interviews,
       ROUND(100.0 * SUM(interviews) / SUM(applications_sent), 1) AS interviews_per_100,
       SUM(interviews > 0)                                       AS clients_with_interview
FROM clients
WHERE applications_sent > 0
GROUP BY followup_band
ORDER BY followup_band;

-- 3. Interviews per 100 applications by CV match score (clients without a score excluded)
SELECT CASE WHEN avg_cv_match_score < 60 THEN '1. <60'
            WHEN avg_cv_match_score < 70 THEN '2. 60-69'
            WHEN avg_cv_match_score < 80 THEN '3. 70-79'
            ELSE '4. 80+' END                                    AS cv_band,
       COUNT(*) AS clients,
       ROUND(100.0 * SUM(interviews) / SUM(applications_sent), 1) AS interviews_per_100
FROM clients
WHERE applications_sent > 0 AND avg_cv_match_score IS NOT NULL
GROUP BY cv_band ORDER BY cv_band;

-- 4. Day-14 early-warning rule: fewer than 5 applications and no follow-up in the first 14 days
SELECT (apps_first_14d < 5 AND followed_up_first_14d = 0) AS flagged,
       COUNT(*)                                          AS active_clients,
       SUM(went_quiet = 1)                               AS went_quiet
FROM clients
WHERE active = 1
GROUP BY flagged;

-- 5. Clients a coach should contact now
SELECT client_id, apps_first_14d, logins_first_14d, followed_up_first_14d, replies_first_14d
FROM clients
WHERE active = 1 AND apps_first_14d < 5 AND followed_up_first_14d = 0
ORDER BY apps_first_14d, logins_first_14d;
