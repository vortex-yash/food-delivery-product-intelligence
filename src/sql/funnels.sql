-- funnels.sql
-- Calculate the sequential product funnel from app_open to checkout_success

WITH event_times AS (

    SELECT
        session_id,

        MIN(CASE WHEN event_name = 'app_open'
            THEN timestamp END) AS app_open_time,

        MIN(CASE WHEN event_name = 'search'
            THEN timestamp END) AS search_time,

        MIN(CASE WHEN event_name = 'view_restaurant'
            THEN timestamp END) AS view_time,

        MIN(CASE WHEN event_name = 'add_to_cart'
            THEN timestamp END) AS cart_time,

        MIN(CASE WHEN event_name = 'checkout_start'
            THEN timestamp END) AS checkout_time,

        MIN(CASE WHEN event_name = 'checkout_success'
            THEN timestamp END) AS success_time

    FROM events
    GROUP BY session_id
),

funnel_base AS (

    SELECT
        session_id,

        CASE
            WHEN app_open_time IS NOT NULL
            THEN 1 ELSE 0
        END AS opened_app,

        CASE
            WHEN app_open_time IS NOT NULL
             AND search_time IS NOT NULL
             AND search_time >= app_open_time
            THEN 1 ELSE 0
        END AS searched,

        CASE
            WHEN app_open_time IS NOT NULL
             AND search_time IS NOT NULL
             AND view_time IS NOT NULL
             AND search_time >= app_open_time
             AND view_time >= search_time
            THEN 1 ELSE 0
        END AS viewed_restaurant,

        CASE
            WHEN app_open_time IS NOT NULL
             AND search_time IS NOT NULL
             AND view_time IS NOT NULL
             AND cart_time IS NOT NULL
             AND search_time >= app_open_time
             AND view_time >= search_time
             AND cart_time >= view_time
            THEN 1 ELSE 0
        END AS added_to_cart,

        CASE
            WHEN app_open_time IS NOT NULL
             AND search_time IS NOT NULL
             AND view_time IS NOT NULL
             AND cart_time IS NOT NULL
             AND checkout_time IS NOT NULL
             AND search_time >= app_open_time
             AND view_time >= search_time
             AND cart_time >= view_time
             AND checkout_time >= cart_time
            THEN 1 ELSE 0
        END AS checkout_started,

        CASE
            WHEN app_open_time IS NOT NULL
             AND search_time IS NOT NULL
             AND view_time IS NOT NULL
             AND cart_time IS NOT NULL
             AND checkout_time IS NOT NULL
             AND success_time IS NOT NULL
             AND search_time >= app_open_time
             AND view_time >= search_time
             AND cart_time >= view_time
             AND checkout_time >= cart_time
             AND success_time >= checkout_time
            THEN 1 ELSE 0
        END AS checkout_succeeded

    FROM event_times
)

SELECT

    COUNT(*) AS total_sessions,

    SUM(opened_app) AS step_1_open,
    SUM(searched) AS step_2_search,
    SUM(viewed_restaurant) AS step_3_view,
    SUM(added_to_cart) AS step_4_cart,
    SUM(checkout_started) AS step_5_checkout,
    SUM(checkout_succeeded) AS step_6_success,

    ROUND(
        SUM(searched) * 100.0
        / NULLIF(SUM(opened_app), 0),
        2
    ) AS conv_search_pct,

    ROUND(
        SUM(viewed_restaurant) * 100.0
        / NULLIF(SUM(searched), 0),
        2
    ) AS conv_view_pct,

    ROUND(
        SUM(added_to_cart) * 100.0
        / NULLIF(SUM(viewed_restaurant), 0),
        2
    ) AS conv_cart_pct,

    ROUND(
        SUM(checkout_started) * 100.0
        / NULLIF(SUM(added_to_cart), 0),
        2
    ) AS conv_checkout_pct,

    ROUND(
        SUM(checkout_succeeded) * 100.0
        / NULLIF(SUM(checkout_started), 0),
        2
    ) AS conv_success_pct,

    ROUND(
        SUM(checkout_succeeded) * 100.0
        / NULLIF(SUM(opened_app), 0),
        2
    ) AS overall_conversion_pct

FROM funnel_base;