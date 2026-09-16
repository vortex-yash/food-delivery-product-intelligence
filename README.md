# Food Delivery Product Intelligence — Product Analytics Case Study
> **Note:** This is an independent product analytics case study built using a synthetic food-delivery marketplace dataset. It is not based on Eternal's internal data, systems, or proprietary information.
A portfolio-grade Product Analytics project designed to demonstrate advanced SQL, Python, and Product Analytics skills.

## Architecture
- **Data Engine**: DuckDB (Local analytical database)
- **Data Generation**: Python (pandas, numpy) generating 60k+ users, 380k+ sessions, 1.3M+ events, and 94k+ orders.
- **Analysis**: SQL (CTEs, window functions, conditional aggregation) + Python (pandas)
- **Testing**: `pytest`
- **Dashboard**: Streamlit + Plotly

## Quickstart (Windows)

1. **Activate Virtual Environment** (If not already created, run `python -m venv .venv`):
   ```powershell
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

2. **Generate Data & Initialize DB**:
   ```powershell
   python src\generator\generate_data.py
   python src\analysis\init_db.py
   ```

3. **Run Analytics & Tests**:
   ```powershell
   python src\analysis\run_sql.py
   python src\analysis\metric_tree.py
   python src\automation\monitor.py
   pytest tests\
   ```

4. **Launch Dashboard**:
   ```powershell
   streamlit run src\dashboard\app.py
   ```

## Project Structure
- `data/`: Raw CSVs and `analytics.duckdb`
- `src/`: Core Python and SQL scripts
- `tests/`: Data quality and logic validation
- `docs/`: Extensive documentation (Findings, Exec Summary, Metrics)
