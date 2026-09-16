import streamlit as st
import duckdb
import os
import pandas as pd
import plotly.express as px


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Food Delivery Product Intelligence",
    layout="wide"
)


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_DIR = os.path.dirname(
    os.path.dirname(
        os.path.dirname(__file__)
    )
)

DB_PATH = os.path.join(
    PROJECT_DIR,
    "data",
    "database",
    "analytics.duckdb"
)


# ============================================================
# DATA LOADER
# ============================================================

@st.cache_data
def load_data(query):

    conn = duckdb.connect(
        DB_PATH,
        read_only=True
    )

    df = conn.execute(query).fetchdf()

    conn.close()

    return df


# ============================================================
# HEADER
# ============================================================

st.title("🍔 Food Delivery Product Intelligence")

st.caption(
    "Synthetic dataset | Product analytics case study"
)


# ============================================================
# TABS
# ============================================================

tab1, tab2, tab3 = st.tabs(
    [
        "Executive Overview",
        "Product Funnel & RCA",
        "Retention & Segmentation"
    ]
)


# ============================================================
# TAB 1 — EXECUTIVE OVERVIEW
# ============================================================

with tab1:

    st.header("Executive Overview")

    col1, col2, col3, col4 = st.columns(4)

    # --------------------------------------------------------
    # TOTAL USERS
    # --------------------------------------------------------

    total_users = load_data(
        """
        SELECT COUNT(*) AS value
        FROM users
        """
    ).iloc[0, 0]

    # --------------------------------------------------------
    # ACTIVATED USERS
    # --------------------------------------------------------
    #
    # Activation is defined here as:
    # users with at least one completed order.
    # --------------------------------------------------------

    activated_users = load_data(
        """
        SELECT COUNT(DISTINCT user_id) AS value
        FROM orders
        WHERE status = 'completed'
        """
    ).iloc[0, 0]

    activation_rate = (
        activated_users / total_users * 100
        if total_users > 0
        else 0
    )

    # --------------------------------------------------------
    # COMPLETED GMV
    # --------------------------------------------------------

    completed_gmv = load_data(
        """
        SELECT
            COALESCE(
                SUM(order_value),
                0
            ) AS value
        FROM orders
        WHERE status = 'completed'
        """
    ).iloc[0, 0]

    # --------------------------------------------------------
    # AOV
    # --------------------------------------------------------

    avg_order = load_data(
        """
        SELECT
            COALESCE(
                AVG(order_value),
                0
            ) AS value
        FROM orders
        WHERE status = 'completed'
        """
    ).iloc[0, 0]

    # --------------------------------------------------------
    # KPI CARDS
    # --------------------------------------------------------

    col1.metric(
        "Total Users",
        f"{total_users:,}"
    )

    col2.metric(
        "Order Activation Rate",
        f"{activation_rate:.1f}%"
    )

    col3.metric(
        "Completed GMV",
        f"${completed_gmv:,.0f}"
    )

    col4.metric(
        "Average Order Value",
        f"${avg_order:.2f}"
    )

    st.caption(
        "Order activation = users with at least one completed order."
    )

    st.divider()

    # --------------------------------------------------------
    # DAILY COMPLETED ORDERS
    # --------------------------------------------------------

    st.subheader("Daily Completed Orders")

    daily_orders = load_data(
        """
        SELECT
            date_trunc(
                'day',
                order_timestamp
            ) AS dt,

            COUNT(*) AS orders

        FROM orders

        WHERE status = 'completed'

        GROUP BY 1

        ORDER BY 1
        """
    )

    fig = px.line(
        daily_orders,
        x="dt",
        y="orders",
        title="Daily Completed Orders"
    )

    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Completed Orders",
        hovermode="x unified"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# ============================================================
# TAB 2 — PRODUCT FUNNEL & RCA
# ============================================================

with tab2:

    st.header("Product Funnel")

    # --------------------------------------------------------
    # FUNNEL QUERY
    # --------------------------------------------------------

    funnel_query = """

    WITH session_events AS (

        SELECT

            session_id,

            MAX(
                CASE
                    WHEN event_name = 'app_open'
                    THEN 1
                    ELSE 0
                END
            ) AS opened_app,

            MAX(
                CASE
                    WHEN event_name = 'search'
                    THEN 1
                    ELSE 0
                END
            ) AS searched,

            MAX(
                CASE
                    WHEN event_name = 'view_restaurant'
                    THEN 1
                    ELSE 0
                END
            ) AS viewed_restaurant,

            MAX(
                CASE
                    WHEN event_name = 'add_to_cart'
                    THEN 1
                    ELSE 0
                END
            ) AS added_to_cart,

            MAX(
                CASE
                    WHEN event_name = 'checkout_start'
                    THEN 1
                    ELSE 0
                END
            ) AS checkout_started,

            MAX(
                CASE
                    WHEN event_name = 'checkout_success'
                    THEN 1
                    ELSE 0
                END
            ) AS checkout_succeeded

        FROM events

        GROUP BY session_id
    ),

    funnel AS (

        SELECT

            SUM(opened_app) AS app_open,

            SUM(searched) AS search,

            SUM(viewed_restaurant) AS view_restaurant,

            SUM(added_to_cart) AS add_to_cart,

            SUM(checkout_started) AS checkout_start,

            SUM(checkout_succeeded) AS checkout_success

        FROM session_events
    )

    SELECT
        'App Open' AS stage,
        app_open AS users,
        1 AS stage_order
    FROM funnel

    UNION ALL

    SELECT
        'Search',
        search,
        2
    FROM funnel

    UNION ALL

    SELECT
        'View Restaurant',
        view_restaurant,
        3
    FROM funnel

    UNION ALL

    SELECT
        'Add to Cart',
        add_to_cart,
        4
    FROM funnel

    UNION ALL

    SELECT
        'Checkout Start',
        checkout_start,
        5
    FROM funnel

    UNION ALL

    SELECT
        'Checkout Success',
        checkout_success,
        6
    FROM funnel

    ORDER BY stage_order

    """

    funnel_df = load_data(
        funnel_query
    )

    # --------------------------------------------------------
    # FUNNEL CHART
    # --------------------------------------------------------

    st.subheader(
        "Session-Level Product Funnel"
    )

    fig_funnel = px.funnel(
        funnel_df,
        x="users",
        y="stage",
        title="Session-Level Product Funnel"
    )

    fig_funnel.update_layout(
        xaxis_title="Sessions",
        yaxis_title=""
    )

    st.plotly_chart(
        fig_funnel,
        use_container_width=True
    )

    # --------------------------------------------------------
    # FUNNEL CONVERSION TABLE
    # --------------------------------------------------------

    funnel_display = funnel_df.copy()

    funnel_display["users"] = (
        funnel_display["users"]
        .astype(int)
    )

    funnel_display["conversion_from_previous"] = (
        funnel_display["users"]
        .div(
            funnel_display["users"].shift(1)
        )
        * 100
    )

    funnel_display.loc[
        funnel_display.index[0],
        "conversion_from_previous"
    ] = 100

    funnel_display["overall_conversion"] = (
        funnel_display["users"]
        / funnel_display["users"].iloc[0]
        * 100
    )

    funnel_display = funnel_display[
        [
            "stage",
            "users",
            "conversion_from_previous",
            "overall_conversion"
        ]
    ]

    funnel_display.columns = [
        "Stage",
        "Sessions",
        "Step Conversion (%)",
        "Overall Conversion (%)"
    ]

    st.dataframe(
        funnel_display.style.format(
            {
                "Sessions": "{:,.0f}",
                "Step Conversion (%)": "{:.2f}%",
                "Overall Conversion (%)": "{:.2f}%"
            }
        ),
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    # ========================================================
    # ROOT CAUSE ANALYSIS
    # ========================================================

    st.header(
        "Root Cause Analysis — Checkout"
    )

    st.write(
        "Checkout success is segmented by platform, "
        "app version, and city to identify localized "
        "conversion deterioration."
    )

    # --------------------------------------------------------
    # RCA QUERY
    # --------------------------------------------------------

    rca_query = """

    WITH checkout_sessions AS (

        SELECT

            e.session_id,

            u.platform,

            u.app_version,

            u.city,

            MAX(
                CASE
                    WHEN e.event_name = 'checkout_start'
                    THEN 1
                    ELSE 0
                END
            ) AS checkout_started,

            MAX(
                CASE
                    WHEN e.event_name = 'checkout_success'
                    THEN 1
                    ELSE 0
                END
            ) AS checkout_succeeded

        FROM events e

        JOIN sessions s
            ON e.session_id = s.session_id

        JOIN users u
            ON s.user_id = u.user_id

        WHERE e.event_name IN (
            'checkout_start',
            'checkout_success'
        )

        GROUP BY
            e.session_id,
            u.platform,
            u.app_version,
            u.city
    )

    SELECT

        platform,

        app_version,

        city,

        COUNT(*) AS checkout_attempts,

        SUM(
            checkout_succeeded
        ) AS successful_checkouts,

        ROUND(
            SUM(checkout_succeeded)
            * 100.0
            / NULLIF(
                SUM(checkout_started),
                0
            ),
            2
        ) AS checkout_success_rate

    FROM checkout_sessions

    WHERE checkout_started = 1

    GROUP BY
        platform,
        app_version,
        city

    HAVING COUNT(*) > 100

    ORDER BY checkout_success_rate ASC

    """

    rca_df = load_data(
        rca_query
    )

    # --------------------------------------------------------
    # RCA DISPLAY TABLE
    # --------------------------------------------------------

    if not rca_df.empty:

        rca_display = rca_df.copy()

        rca_display.columns = [
            "Platform",
            "App Version",
            "City",
            "Checkout Attempts",
            "Successful Checkouts",
            "Success Rate (%)"
        ]

        st.dataframe(
            rca_display.style.format(
                {
                    "Checkout Attempts": "{:,.0f}",
                    "Successful Checkouts": "{:,.0f}",
                    "Success Rate (%)": "{:.2f}%"
                }
            ),
            use_container_width=True,
            hide_index=True
        )

        # ----------------------------------------------------
        # LOWEST SEGMENT
        # ----------------------------------------------------

        lowest = rca_df.iloc[0]

        # ----------------------------------------------------
        # COMPARISON:
        # Android v1.9 Chicago
        # vs Android v1.8 Chicago
        # ----------------------------------------------------

        anomaly_rate = float(
            lowest["checkout_success_rate"]
        )

        baseline_query = """

        SELECT
            checkout_success_rate

        FROM (
            SELECT

                platform,

                app_version,

                city,

                ROUND(
                    SUM(checkout_succeeded)
                    * 100.0
                    / NULLIF(
                        SUM(checkout_started),
                        0
                    ),
                    2
                ) AS checkout_success_rate

            FROM (

                SELECT

                    e.session_id,

                    u.platform,

                    u.app_version,

                    u.city,

                    MAX(
                        CASE
                            WHEN e.event_name =
                                'checkout_start'
                            THEN 1
                            ELSE 0
                        END
                    ) AS checkout_started,

                    MAX(
                        CASE
                            WHEN e.event_name =
                                'checkout_success'
                            THEN 1
                            ELSE 0
                        END
                    ) AS checkout_succeeded

                FROM events e

                JOIN sessions s
                    ON e.session_id =
                       s.session_id

                JOIN users u
                    ON s.user_id =
                       u.user_id

                WHERE e.event_name IN (
                    'checkout_start',
                    'checkout_success'
                )

                GROUP BY
                    e.session_id,
                    u.platform,
                    u.app_version,
                    u.city
            )

            WHERE checkout_started = 1

            GROUP BY
                platform,
                app_version,
                city

            HAVING COUNT(*) > 100
        )

        WHERE platform = 'Android'
          AND app_version = 'v1.8'
          AND city = 'Chicago'

        """

        baseline_df = load_data(
            baseline_query
        )

        if not baseline_df.empty:

            baseline_rate = float(
                baseline_df.iloc[0, 0]
            )

            gap = (
                baseline_rate
                - anomaly_rate
            )

            col1, col2, col3 = st.columns(3)

            col1.metric(
                "Android v1.9 Chicago",
                f"{anomaly_rate:.2f}%"
            )

            col2.metric(
                "Android v1.8 Chicago",
                f"{baseline_rate:.2f}%"
            )

            col3.metric(
                "Conversion Gap",
                f"{gap:.2f} pp"
            )

            st.info(
                f"Localized checkout deterioration detected: "
                f"Android v1.9 users in Chicago show "
                f"{anomaly_rate:.2f}% checkout success versus "
                f"{baseline_rate:.2f}% for Android v1.8 in Chicago "
                f"({gap:.2f} percentage points lower)."
            )

        else:

            st.info(
                f"Lowest observed segment: "
                f"{lowest['platform']} "
                f"{lowest['app_version']} in "
                f"{lowest['city']} — "
                f"{lowest['checkout_success_rate']:.2f}% "
                f"checkout success across "
                f"{int(lowest['checkout_attempts']):,} attempts."
            )


# ============================================================
# TAB 3 — RETENTION & SEGMENTATION
# ============================================================

with tab3:

    st.header(
        "Retention & User Segmentation"
    )

    # ========================================================
    # WEEKLY COHORT RETENTION
    # ========================================================

    st.subheader(
        "Weekly Cohort Retention"
    )

    st.caption(
        "Cohorts are defined by each user's first active week. "
        "Week 0 therefore represents 100% of the cohort."
    )

    # --------------------------------------------------------
    # CORRECTED COHORT QUERY
    # --------------------------------------------------------

    cohort_query = """

    WITH first_activity AS (

        SELECT

            user_id,

            date_trunc(
                'week',
                MIN(session_start)
            ) AS cohort_week

        FROM sessions

        GROUP BY user_id
    ),

    user_activity AS (

        SELECT DISTINCT

            user_id,

            date_trunc(
                'week',
                session_start
            ) AS activity_week

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

            COUNT(DISTINCT user_id)
                AS cohort_size

        FROM first_activity

        GROUP BY cohort_week
    ),

    retention_data AS (

        SELECT

            ca.cohort_week,

            cs.cohort_size,

            ca.weeks_since_first_activity,

            COUNT(
                DISTINCT ca.user_id
            ) AS active_users

        FROM cohort_activity ca

        JOIN cohort_sizes cs
            ON ca.cohort_week =
               cs.cohort_week

        GROUP BY

            ca.cohort_week,

            cs.cohort_size,

            ca.weeks_since_first_activity
    )

    SELECT

        cohort_week,

        cohort_size,

        weeks_since_first_activity,

        active_users,

        ROUND(
            active_users * 100.0
            / cohort_size,
            2
        ) AS retention_pct

    FROM retention_data

    WHERE weeks_since_first_activity
          BETWEEN 0 AND 12

    ORDER BY
        cohort_week,
        weeks_since_first_activity

    """

    cohort_df = load_data(
        cohort_query
    )

    # --------------------------------------------------------
    # RETENTION TABLE
    # --------------------------------------------------------

    if not cohort_df.empty:

        retention_pivot = cohort_df.pivot(
            index="cohort_week",
            columns="weeks_since_first_activity",
            values="retention_pct"
        )

        retention_pivot.columns = [
            f"Week {int(col)}"
            for col in retention_pivot.columns
        ]

        retention_pivot.index = (
            pd.to_datetime(
                retention_pivot.index
            ).strftime("%Y-%m-%d")
        )

        st.dataframe(
            retention_pivot.style.format(
                "{:.1f}%"
            ),
            use_container_width=True
        )

    st.divider()

    # ========================================================
    # USER SPEND SEGMENTATION
    # ========================================================

    st.subheader(
        "User Spend Segmentation by Acquisition Channel"
    )

    st.caption(
        "Spend is total completed order value per user; "
        "it is used as a behavioral value measure, not formal LTV."
    )

    # --------------------------------------------------------
    # SEGMENTATION QUERY
    # --------------------------------------------------------

    seg_query = """

    WITH user_spend AS (

        SELECT

            u.user_id,

            u.acquisition_channel,

            SUM(
                CASE
                    WHEN o.status = 'completed'
                    THEN COALESCE(
                        o.order_value,
                        0
                    )
                    ELSE 0
                END
            ) AS total_completed_spend

        FROM users u

        LEFT JOIN orders o
            ON u.user_id = o.user_id

        GROUP BY

            u.user_id,

            u.acquisition_channel
    ),

    segmented AS (

        SELECT

            *,

            CASE

                WHEN total_completed_spend > 500
                    THEN 'High Value'

                WHEN total_completed_spend > 150
                    THEN 'Medium Value'

                ELSE 'Low Value'

            END AS spend_segment

        FROM user_spend
    )

    SELECT

        acquisition_channel,

        spend_segment,

        COUNT(*) AS users

    FROM segmented

    GROUP BY

        acquisition_channel,

        spend_segment

    ORDER BY

        acquisition_channel,

        spend_segment

    """

    seg_df = load_data(
        seg_query
    )

    if not seg_df.empty:

        # ----------------------------------------------------
        # FRIENDLY DISPLAY
        # ----------------------------------------------------

        seg_display = seg_df.copy()

        seg_display.columns = [
            "Acquisition Channel",
            "Spend Segment",
            "Users"
        ]

        st.dataframe(
            seg_display.style.format(
                {
                    "Users": "{:,.0f}"
                }
            ),
            use_container_width=True,
            hide_index=True
        )

        # ----------------------------------------------------
        # BAR CHART
        # ----------------------------------------------------

        seg_chart = px.bar(
            seg_df,
            x="acquisition_channel",
            y="users",
            color="spend_segment",
            barmode="group",
            title=(
                "Users by Spend Segment "
                "and Acquisition Channel"
            ),
            labels={
                "acquisition_channel":
                    "Acquisition Channel",
                "users":
                    "Users",
                "spend_segment":
                    "Spend Segment"
            }
        )

        seg_chart.update_layout(
            xaxis_title="Acquisition Channel",
            yaxis_title="Users",
            legend_title="Spend Segment"
        )

        st.plotly_chart(
            seg_chart,
            use_container_width=True
        )