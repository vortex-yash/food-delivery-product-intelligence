import duckdb
import os
import pytest
import pandas as pd

PROJECT_DIR = os.path.dirname(os.path.dirname(__file__))
DB_PATH = os.path.join(
    PROJECT_DIR,
    'data',
    'database',
    'analytics.duckdb'
)
SQL_DIR = os.path.join(
    PROJECT_DIR,
    'src',
    'sql'
)


@pytest.fixture(scope="module")
def conn():
    connection = duckdb.connect(DB_PATH, read_only=True)
    yield connection
    connection.close()


def load_sql(filename):
    filepath = os.path.join(SQL_DIR, filename)

    with open(filepath, 'r') as f:
        return f.read()


# ============================================================
# 1. DATA VALIDATION TESTS
# ============================================================

def test_tables_populated(conn):
    for table in [
        'users',
        'restaurants',
        'sessions',
        'events',
        'orders'
    ]:
        res = conn.execute(
            f"SELECT COUNT(*) FROM {table}"
        ).fetchone()[0]

        assert res > 0, f"{table} table is empty"


def test_sessions_validity(conn):
    # Session end must be after or equal to session start
    query = """
        SELECT COUNT(*)
        FROM sessions
        WHERE session_end < session_start
    """

    invalid_sessions = conn.execute(query).fetchone()[0]

    assert invalid_sessions == 0, (
        "Found sessions with end time before start time"
    )


def test_orders_validity(conn):
    # Order values must be positive
    query = """
        SELECT COUNT(*)
        FROM orders
        WHERE order_value <= 0
    """

    invalid_orders = conn.execute(query).fetchone()[0]

    assert invalid_orders == 0, (
        "Found orders with negative or zero value"
    )


# ============================================================
# 2. FUNNEL METRIC TESTS
# ============================================================

def test_events_funnel_logic_raw(conn):
    # Ensure checkout_success <= checkout_start
    # at the event level

    query = """
        SELECT
            SUM(
                CASE
                    WHEN event_name = 'checkout_start'
                    THEN 1
                    ELSE 0
                END
            ) AS starts,

            SUM(
                CASE
                    WHEN event_name = 'checkout_success'
                    THEN 1
                    ELSE 0
                END
            ) AS successes

        FROM events
    """

    starts, successes = conn.execute(query).fetchone()

    assert successes <= starts, (
        "More successes than starts globally"
    )


def test_funnel_sql_execution_and_math(conn):
    sql = load_sql('funnels.sql')
    df = conn.execute(sql).fetchdf()

    assert len(df) == 1, (
        "Funnel SQL should return exactly 1 global row"
    )

    row = df.iloc[0]

    # Check monotonic funnel decreasing behavior
    assert row['step_1_open'] >= row['step_2_search']

    assert row['step_2_search'] >= row['step_3_view']

    assert row['step_3_view'] >= row['step_4_cart']

    assert row['step_4_cart'] >= row['step_5_checkout']

    assert row['step_5_checkout'] >= row['step_6_success']

    # Check percentage limits
    assert 0 <= row['overall_conversion_pct'] <= 100


# ============================================================
# 3. RETENTION & COHORT TESTS
# ============================================================

def test_cohorts_sql_execution_and_logic(conn):
    sql = load_sql('cohorts.sql')
    df = conn.execute(sql).fetchdf()

    assert not df.empty, (
        "Cohorts SQL returned no data"
    )

    assert 'cohort_week' in df.columns

    assert 'retention_pct' in df.columns

    assert 'weeks_since_first_activity' in df.columns

    # Active users cannot exceed cohort size
    assert (
        df['active_users'] <= df['cohort_size']
    ).all(), (
        "Active users cannot exceed cohort size"
    )

    # Retention cannot exceed 100%
    assert (
        df['retention_pct'] <= 100.0
    ).all(), (
        "Retention percentage cannot exceed 100%"
    )

    # Weeks since first activity cannot be negative
    assert (
        df['weeks_since_first_activity'] >= 0
    ).all(), (
        "Weeks since first activity cannot be negative"
    )


# ============================================================
# 4. USER SEGMENTATION TESTS
# ============================================================

def test_segmentation_sql_execution_and_logic(conn):
    sql = load_sql('segmentation.sql')
    df = conn.execute(sql).fetchdf()

    assert not df.empty, (
        "Segmentation SQL returned no data"
    )

    # Validate the current behavioral spend segments
    assert set(
        df['spend_segment'].unique()
    ).issubset({
        'High Value',
        'Medium Value',
        'Low Value'
    }), (
        "Unexpected spend segment found"
    )

    # Check aggregate constraints
    assert (
        df['num_users'] > 0
    ).all(), (
        "Segment user count must be positive"
    )

    assert (
        df['total_orders'] >= 0
    ).all(), (
        "Total orders cannot be negative"
    )


# ============================================================
# 5. RCA & ANOMALY TESTS
# ============================================================

def test_rca_sql_execution(conn):
    sql = load_sql('rca.sql')
    df = conn.execute(sql).fetchdf()

    assert not df.empty, (
        "RCA SQL returned no data"
    )

    assert 'conversion_rate' in df.columns


def test_rca_anomaly_presence_and_magnitude(conn):
    sql = load_sql('rca.sql')
    df = conn.execute(sql).fetchdf()

    # Intentionally injected anomaly
    anomaly = df[
        (df['platform'] == 'Android') &
        (df['app_version'] == 'v1.9') &
        (df['city'] == 'Chicago')
    ]

    # Comparison baseline
    baseline = df[
        (df['platform'] == 'Android') &
        (df['app_version'] == 'v1.8') &
        (df['city'] == 'Chicago')
    ]

    assert not anomaly.empty, (
        "Anomaly segment missing from RCA output"
    )

    assert not baseline.empty, (
        "Baseline segment missing from RCA output"
    )

    anomaly_conv = anomaly[
        'conversion_rate'
    ].values[0]

    baseline_conv = baseline[
        'conversion_rate'
    ].values[0]

    diff = baseline_conv - anomaly_conv

    # Expected approximately 11.7 percentage-point drop
    # Allow 10–13 percentage points for robustness
    assert 10.0 <= diff <= 13.0, (
        f"RCA magnitude {diff} outside expected bounds "
        "(10-13 percentage points)"
    )


# ============================================================
# 6. AUTOMATION / METRIC MONITORING TESTS
# ============================================================

def test_monitor_query_sanity(conn):
    # Ensure the KPI monitoring logic runs at the
    # session level and produces valid daily variation.

    query = """
        WITH checkout_sessions AS (
            SELECT
                session_id,
                date_trunc('day', MIN(timestamp)) AS dt,

                MAX(
                    CASE
                        WHEN event_name = 'checkout_start'
                        THEN 1
                        ELSE 0
                    END
                ) AS started,

                MAX(
                    CASE
                        WHEN event_name = 'checkout_success'
                        THEN 1
                        ELSE 0
                    END
                ) AS succeeded

            FROM events

            WHERE event_name IN (
                'checkout_start',
                'checkout_success'
            )

            GROUP BY session_id
        ),

        daily_checkouts AS (
            SELECT
                dt,
                SUM(started) AS starts,

                SUM(
                    CASE
                        WHEN started = 1
                         AND succeeded = 1
                        THEN 1
                        ELSE 0
                    END
                ) AS successes

            FROM checkout_sessions

            WHERE started = 1

            GROUP BY dt
        )

        SELECT
            dt,

            ROUND(
                successes * 100.0
                / NULLIF(starts, 0),
                2
            ) AS success_rate

        FROM daily_checkouts

        ORDER BY dt
    """

    df = conn.execute(query).fetchdf()

    assert not df.empty, (
        "KPI monitoring query returned no data"
    )

    # Synthetic data should contain natural variation
    assert df['success_rate'].std() > 0, (
        "Success rate has no variance"
    )

    # Calculate z-score internally
    mean_rate = df['success_rate'].mean()

    std_rate = df['success_rate'].std()

    df['z_score'] = (
        (df['success_rate'] - mean_rate)
        / std_rate
    )

    assert not df['z_score'].isna().all(), (
        "Z-scores calculated to NaN"
    )