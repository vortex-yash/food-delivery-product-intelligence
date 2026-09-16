-- segmentation.sql

-- Segment users based on their total completed order spend

WITH user_spend AS (

    SELECT
        u.user_id,
        u.city,
        u.acquisition_channel,

        COUNT(o.order_id) AS total_orders,

        SUM(COALESCE(o.order_value, 0)) AS total_spend,

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
        CASE
            WHEN total_spend > 500 THEN 'High Value'
            WHEN total_spend > 150 THEN 'Medium Value'
            ELSE 'Low Value'
        END AS spend_segment

    FROM user_spend
)

SELECT

    spend_segment,

    acquisition_channel,

    COUNT(user_id) AS num_users,

    ROUND(AVG(total_spend), 2) AS avg_total_spend,

    SUM(total_orders) AS total_orders

FROM user_segments

GROUP BY
    spend_segment,
    acquisition_channel

ORDER BY
    spend_segment,
    num_users DESC;