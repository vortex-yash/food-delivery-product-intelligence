import duckdb
import os

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
DB_PATH = os.path.join(PROJECT_DIR, "data", "database", "analytics.duckdb")


def calculate_metric_tree():
    conn = duckdb.connect(DB_PATH)

    # 1. Acquisition
    total_users = conn.execute("""
        SELECT COUNT(*)
        FROM users
    """).fetchone()[0]

    # 2. Activation
    activated_users = conn.execute("""
        SELECT COUNT(DISTINCT user_id)
        FROM orders
        WHERE status = 'completed'
    """).fetchone()[0]

    # 3. Repeat Purchase / Engagement
    repeat_purchase_rate = conn.execute("""
        SELECT
            COUNT(*) FILTER (
                WHERE completed_orders >= 2
            ) * 100.0 / COUNT(*)
        FROM (
            SELECT
                user_id,
                COUNT(*) AS completed_orders
            FROM orders
            WHERE status = 'completed'
            GROUP BY user_id
        )
    """).fetchone()[0]

    # 4. Monetization
    monetization = conn.execute("""
        SELECT
            ROUND(AVG(order_value), 2),
            ROUND(SUM(order_value), 2)
        FROM orders
        WHERE status = 'completed'
    """).fetchone()

    avg_order_value = monetization[0]
    total_gmv = monetization[1]

    print("--- GROWTH METRIC TREE ---")
    print(f"Acquisition (Total Users): {total_users}")

    print(
        f"Activation (Users with ≥1 Completed Order): "
        f"{activated_users} "
        f"({round(activated_users * 100 / total_users, 2)}%)"
    )

    print(
        f"Repeat Purchase Rate (Users with ≥2 Completed Orders): "
        f"{round(repeat_purchase_rate, 2)}%"
    )

    print(f"Monetization (Average Order Value): ${avg_order_value}")
    print(f"Monetization (Total GMV): ${total_gmv}")

    print("--------------------------")

    conn.close()


if __name__ == "__main__":
    calculate_metric_tree()