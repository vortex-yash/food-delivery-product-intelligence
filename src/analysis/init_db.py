import duckdb
import os

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
DATA_DIR = os.path.join(PROJECT_DIR, 'data', 'raw')
DB_DIR = os.path.join(PROJECT_DIR, 'data', 'database')
os.makedirs(DB_DIR, exist_ok=True)

DB_PATH = os.path.join(DB_DIR, 'analytics.duckdb')

def init_db():
    print(f"Initializing DuckDB at {DB_PATH}")
    # Connect to DuckDB (creates the file if it doesn't exist)
    conn = duckdb.connect(DB_PATH)
    
    # Create tables by loading CSV files directly
    # This is a fast and efficient way in DuckDB
    
    tables_to_load = ['users', 'restaurants', 'sessions', 'events', 'orders']
    
    for table in tables_to_load:
        csv_path = os.path.join(DATA_DIR, f"{table}.csv")
        if os.path.exists(csv_path):
            print(f"Loading {table}...")
            # Drop table if exists to allow re-runs
            conn.execute(f"DROP TABLE IF EXISTS {table}")
            # Create and load
            conn.execute(f"CREATE TABLE {table} AS SELECT * FROM read_csv_auto('{csv_path}')")
            
            # Print row count for validation
            count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            print(f" - {table} loaded with {count} rows.")
        else:
            print(f"WARNING: {csv_path} not found.")

    # Validate the RCA Anomaly
    print("\n--- Data Validation: Checking RCA Anomaly (Checkout Success Rate) ---")
    query = """
    WITH checkout_starts AS (
        SELECT u.platform, u.app_version, u.city, COUNT(*) as starts
        FROM events e
        JOIN sessions s ON e.session_id = s.session_id
        JOIN users u ON e.user_id = u.user_id
        WHERE e.event_name = 'checkout_start'
        GROUP BY 1, 2, 3
    ),
    checkout_successes AS (
        SELECT u.platform, u.app_version, u.city, COUNT(*) as successes
        FROM events e
        JOIN sessions s ON e.session_id = s.session_id
        JOIN users u ON e.user_id = u.user_id
        WHERE e.event_name = 'checkout_success'
        GROUP BY 1, 2, 3
    )
    SELECT 
        st.platform, 
        st.app_version, 
        st.city, 
        st.starts, 
        COALESCE(su.successes, 0) as successes,
        ROUND(COALESCE(su.successes, 0) * 100.0 / NULLIF(st.starts, 0), 2) as conversion_rate
    FROM checkout_starts st
    LEFT JOIN checkout_successes su 
        ON st.platform = su.platform 
        AND st.app_version = su.app_version
        AND st.city = su.city
    WHERE st.starts > 100
    ORDER BY conversion_rate ASC
    LIMIT 10;
    """
    
    results = conn.execute(query).fetchdf()
    print("Lowest Conversion Rates by Segment (expecting Android, v1.9, Chicago to be lowest):")
    print(results.to_string(index=False))
    
    conn.close()
    print("\nDatabase initialization and validation complete.")

if __name__ == "__main__":
    init_db()
