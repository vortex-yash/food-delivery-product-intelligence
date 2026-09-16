import duckdb
import os
import pandas as pd

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
DB_PATH = os.path.join(PROJECT_DIR, 'data', 'database', 'analytics.duckdb')
SQL_DIR = os.path.join(PROJECT_DIR, 'src', 'sql')

def run_all_sql():
    print(f"Connecting to DuckDB at {DB_PATH}")
    conn = duckdb.connect(DB_PATH)
    
    sql_files = ['funnels.sql', 'cohorts.sql', 'segmentation.sql', 'rca.sql']
    
    for filename in sql_files:
        filepath = os.path.join(SQL_DIR, filename)
        if os.path.exists(filepath):
            print(f"\n--- Executing {filename} ---")
            with open(filepath, 'r') as f:
                query = f.read()
            
            try:
                # fetchdf returns a pandas dataframe
                results = conn.execute(query).fetchdf()
                print(f"Query returned {len(results)} rows.")
                print("First 5 rows:")
                print(results.head())
            except Exception as e:
                print(f"ERROR executing {filename}: {e}")
        else:
            print(f"WARNING: {filepath} not found.")

    conn.close()

if __name__ == "__main__":
    run_all_sql()
