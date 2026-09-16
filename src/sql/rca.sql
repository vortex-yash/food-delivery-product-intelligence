-- rca.sql
-- Root Cause Analysis to isolate the exact dimension causing the drop in checkout success.
-- We segment by Platform, App Version, and City to locate the anomaly.

WITH checkout_funnel AS (
    SELECT 
        u.platform,
        u.app_version,
        u.city,
        e.session_id,
        MAX(CASE WHEN e.event_name = 'checkout_start' THEN 1 ELSE 0 END) as started,
        MAX(CASE WHEN e.event_name = 'checkout_success' THEN 1 ELSE 0 END) as succeeded
    FROM events e
    JOIN sessions s ON e.session_id = s.session_id
    JOIN users u ON e.user_id = u.user_id
    WHERE e.event_name IN ('checkout_start', 'checkout_success')
    GROUP BY u.platform, u.app_version, u.city, e.session_id
)
SELECT 
    platform,
    app_version,
    city,
    COUNT(session_id) as checkout_attempts,
    SUM(succeeded) as successful_checkouts,
    ROUND(SUM(succeeded) * 100.0 / COUNT(session_id), 2) as conversion_rate
FROM checkout_funnel
GROUP BY platform, app_version, city
HAVING COUNT(session_id) > 100
ORDER BY conversion_rate ASC;
