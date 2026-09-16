-- cohorts.sql
-- Weekly retention based on each user's first active week

WITH first_activity AS (
    SELECT
        user_id,
        date_trunc('week', MIN(session_start)) AS cohort_week
    FROM sessions
    GROUP BY user_id
),

user_activity AS (
    SELECT DISTINCT
        user_id,
        date_trunc('week', session_start) AS activity_week
    FROM sessions
),

cohort_activity AS (
    SELECT
        f.user_id,
        f.cohort_week,
        a.activity_week,
        date_diff(
            'week',
            f.cohort_week,
            a.activity_week
        ) AS weeks_since_first_activity
    FROM first_activity f
    JOIN user_activity a
        ON f.user_id = a.user_id
    WHERE a.activity_week >= f.cohort_week
),

cohort_sizes AS (
    SELECT
        cohort_week,
        COUNT(DISTINCT user_id) AS cohort_size
    FROM first_activity
    GROUP BY cohort_week
),

retention_data AS (
    SELECT
        ca.cohort_week,
        cs.cohort_size,
        ca.weeks_since_first_activity,
        COUNT(DISTINCT ca.user_id) AS active_users
    FROM cohort_activity ca
    JOIN cohort_sizes cs
        ON ca.cohort_week = cs.cohort_week
    GROUP BY
        ca.cohort_week,
        cs.cohort_size,
        ca.weeks_since_first_activity
)

SELECT
    cohort_week,
    cohort_size,
    weeks_since_first_activity AS weeks_since_first_activity,
    active_users,
    ROUND(
        active_users * 100.0 / cohort_size,
        2
    ) AS retention_pct
FROM retention_data
ORDER BY
    cohort_week,
    weeks_since_first_activity;