-- Segment users into approximately equal-sized groups
-- based on total completed-order spend

WITH user_spend AS (
    SELECT
        u.user_id,
        u.city,
        u.acquisition_channel,
        COUNT(o.order_id) AS total_orders,
        SUM(COALESCE(o.order_value, 0)) AS total_completed_spend,
        MAX(o.order_timestamp) AS last_order_date
    FROM users u
    LEFT JOIN orders o
        ON u.user_id = o.user_id
        AND o.status = 'completed'
    GROUP BY
        u.user_id,
        u.city,
        u.acquisition_channel
),

user_segments AS (
    SELECT
        *,
        NTILE(3) OVER (
            ORDER BY total_completed_spend
        ) AS spend_tertile
    FROM user_spend
)

SELECT
    CASE
        WHEN spend_tertile = 1 THEN 'Low Value'
        WHEN spend_tertile = 2 THEN 'Medium Value'
        WHEN spend_tertile = 3 THEN 'High Value'
    END AS spend_segment,
    acquisition_channel,
    COUNT(user_id) AS num_users,
    ROUND(AVG(total_completed_spend), 2) AS avg_total_spend,
    SUM(total_orders) AS total_orders
FROM user_segments
GROUP BY
    spend_tertile,
    acquisition_channel
ORDER BY
    spend_tertile,
    num_users DESC;