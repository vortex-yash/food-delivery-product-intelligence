import duckdb
import os
import pandas as pd
import numpy as np

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
DB_PATH = os.path.join(
    PROJECT_DIR,
    'data',
    'database',
    'analytics.duckdb'
)


def monitor_kpis():
    conn = duckdb.connect(DB_PATH)

    # Analyze daily checkout success rate at the session level.
    # Only days with at least 20 checkout starts are monitored
    # to reduce false alarms caused by low-volume days.
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
        starts,
        successes,

        ROUND(
            successes * 100.0
            / NULLIF(starts, 0),
            2
        ) AS success_rate

    FROM daily_checkouts

    WHERE starts >= 20

    ORDER BY dt
    """

    df = conn.execute(query).fetchdf()

    # Anomaly Detection (Z-Score on daily checkout success rate)
    mean_rate = df['success_rate'].mean()
    std_rate = df['success_rate'].std()

    df['z_score'] = (
        (df['success_rate'] - mean_rate)
        / std_rate
    )

    anomalies = df[df['z_score'].abs() > 2.0]

    print("--- AUTOMATED KPI MONITORING ---")
    print(
        f"Analyzed {len(df)} qualifying days "
        "of checkout data."
    )
    print(
        "Minimum checkout starts per monitored day: 20"
    )
    print(
        f"Average Checkout Success Rate: "
        f"{mean_rate:.2f}% "
        f"(StdDev: {std_rate:.2f}%)"
    )

    if not anomalies.empty:
        print(
            "\n[WARNING] Anomalies Detected "
            "in Checkout Success Rate!"
        )

        print(
            anomalies[
                ['dt', 'starts', 'success_rate', 'z_score']
            ].to_string(index=False)
        )

    else:
        print(
            "\n[OK] No major anomalies detected "
            "at the global daily level."
        )

        print(
            "Note: Localized RCA anomalies may still "
            "exist in sub-segments."
        )

    conn.close()


if __name__ == "__main__":
    monitor_kpis()