import duckdb
import os
import pandas as pd
import numpy as np

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
DB_PATH = os.path.join(PROJECT_DIR, 'data', 'database', 'analytics.duckdb')

def monitor_kpis():
    conn = duckdb.connect(DB_PATH)
    
    # Analyze daily checkout success rate
    query = """
    WITH daily_checkouts AS (
        SELECT 
            date_trunc('day', timestamp) as dt,
            SUM(CASE WHEN event_name = 'checkout_start' THEN 1 ELSE 0 END) as starts,
            SUM(CASE WHEN event_name = 'checkout_success' THEN 1 ELSE 0 END) as successes
        FROM events
        WHERE event_name IN ('checkout_start', 'checkout_success')
        GROUP BY 1
    )
    SELECT 
        dt, 
        starts, 
        successes, 
        ROUND(successes * 100.0 / NULLIF(starts, 0), 2) as success_rate 
    FROM daily_checkouts
    ORDER BY dt
    """
    
    df = conn.execute(query).fetchdf()
    
    # Anomaly Detection (Z-Score on success rate)
    mean_rate = df['success_rate'].mean()
    std_rate = df['success_rate'].std()
    
    df['z_score'] = (df['success_rate'] - mean_rate) / std_rate
    anomalies = df[df['z_score'].abs() > 2.0]
    
    print("--- AUTOMATED KPI MONITORING ---")
    print(f"Analyzed {len(df)} days of checkout data.")
    print(f"Average Checkout Success Rate: {mean_rate:.2f}% (StdDev: {std_rate:.2f}%)")
    
    if not anomalies.empty:
        print("\n[WARNING] Anomalies Detected in Checkout Success Rate!")
        print(anomalies[['dt', 'success_rate', 'z_score']].to_string(index=False))
    else:
        print("\n[OK] No major anomalies detected at the global daily level.")
        print("Note: Localized RCA anomalies may still exist in sub-segments.")
        
    conn.close()

if __name__ == "__main__":
    monitor_kpis()
