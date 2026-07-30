"""
Master Data Cleaning & Database Loading Pipeline for Bluestock Mutual Fund Analytics
Implemented using pure Python standard libraries (csv, sqlite3, datetime) for maximum compatibility.
Generates Star Schema SQLite DB (bluestock_mf.db) and exports 10 cleaned CSVs in data/processed/.
"""

import os
import csv
import sqlite3
from datetime import datetime, timedelta

# Define Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(BASE_DIR, "data", "raw")
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")
DB_PATH = os.path.join(BASE_DIR, "bluestock_mf.db")
DATA_DB_PATH = os.path.join(BASE_DIR, "data", "bluestock_mf.db")
ROOT_SCHEMA_PATH = os.path.join(BASE_DIR, "schema.sql")
SQL_SCHEMA_PATH = os.path.join(BASE_DIR, "sql", "schema.sql")

os.makedirs(PROCESSED_DIR, exist_ok=True)


def parse_date(date_str: str) -> str:
    """Parses various date string formats into YYYY-MM-DD."""
    if not date_str or not date_str.strip():
        return ""
    date_str = date_str.strip()
    for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%m/%d/%Y", "%d/%m/%Y", "%Y/%m/%d", "%Y-%m"):
        try:
            dt = datetime.strptime(date_str, fmt)
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            pass
    return date_str


def parse_float(val: str, default: float = 0.0) -> float:
    """Safely converts string to float."""
    if val is None:
        return default
    val_str = str(val).strip()
    if not val_str or val_str.lower() in ("null", "none", "nan", "n/a", "na", ""):
        return default
    try:
        return float(val_str)
    except ValueError:
        return default


def parse_int(val: str, default: int = 0) -> int:
    """Safely converts string to int."""
    if val is None:
        return default
    val_str = str(val).strip()
    if not val_str or val_str.lower() in ("null", "none", "nan", "n/a", "na", ""):
        return default
    try:
        return int(float(val_str))
    except ValueError:
        return default


def clean_fund_master():
    raw_file = os.path.join(RAW_DIR, "01_fund_master.csv")
    cleaned_rows = []
    seen = set()
    
    with open(raw_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            amfi_code = row["amfi_code"].strip()
            if amfi_code in seen:
                continue
            seen.add(amfi_code)
            
            cleaned_row = {
                "amfi_code": amfi_code,
                "fund_house": row["fund_house"].strip(),
                "scheme_name": row["scheme_name"].strip(),
                "category": row["category"].strip(),
                "sub_category": row["sub_category"].strip(),
                "plan": row["plan"].strip(),
                "launch_date": parse_date(row["launch_date"]),
                "benchmark": row["benchmark"].strip(),
                "expense_ratio_pct": parse_float(row["expense_ratio_pct"]),
                "exit_load_pct": parse_float(row["exit_load_pct"]),
                "min_sip_amount": parse_float(row["min_sip_amount"]),
                "min_lumpsum_amount": parse_float(row["min_lumpsum_amount"]),
                "fund_manager": row["fund_manager"].strip(),
                "risk_category": row["risk_category"].strip(),
                "sebi_category_code": row["sebi_category_code"].strip()
            }
            cleaned_rows.append(cleaned_row)
            
    return cleaned_rows


def clean_nav_history():
    raw_file = os.path.join(RAW_DIR, "02_nav_history.csv")
    by_fund = {}
    
    with open(raw_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            amfi_code = row["amfi_code"].strip()
            dt_str = parse_date(row["date"])
            nav = parse_float(row["nav"])
            repurchase = parse_float(row.get("repurchase_price", "0"))
            sale = parse_float(row.get("sale_price", "0"))
            
            if nav <= 0:
                continue
                
            dt = datetime.strptime(dt_str, "%Y-%m-%d").date()
            if amfi_code not in by_fund:
                by_fund[amfi_code] = {}
            by_fund[amfi_code][dt] = (nav, repurchase, sale)

    # Forward fill missing NAV for weekends / holidays per amfi_code
    all_cleaned = []
    for amfi_code, date_dict in by_fund.items():
        sorted_dates = sorted(date_dict.keys())
        if not sorted_dates:
            continue
        min_date = sorted_dates[0]
        max_date = sorted_dates[-1]
        
        curr_date = min_date
        last_val = date_dict[min_date]
        
        while curr_date <= max_date:
            if curr_date in date_dict:
                last_val = date_dict[curr_date]
            
            all_cleaned.append({
                "amfi_code": amfi_code,
                "date": curr_date.strftime("%Y-%m-%d"),
                "nav": last_val[0],
                "repurchase_price": last_val[1],
                "sale_price": last_val[2]
            })
            curr_date += timedelta(days=1)
            
    # Sort by amfi_code + date
    all_cleaned.sort(key=lambda x: (x["amfi_code"], x["date"]))
    return all_cleaned


def clean_investor_transactions():
    raw_file = os.path.join(RAW_DIR, "08_investor_transactions.csv")
    cleaned_rows = []
    tx_map = {
        "sip": "SIP", "SIP": "SIP", "Sip": "SIP",
        "lumpsum": "Lumpsum", "Lumpsum": "Lumpsum", "LUMPSUM": "Lumpsum",
        "redemption": "Redemption", "Redemption": "Redemption", "REDEMPTION": "Redemption"
    }
    kyc_map = {"Verified": "Verified", "Pending": "Pending", "VERIFIED": "Verified", "PENDING": "Pending"}
    
    seen = set()
    with open(raw_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for idx, row in enumerate(reader, 1):
            inv_id = row["investor_id"].strip()
            amfi_code = row["amfi_code"].strip()
            tx_dt = parse_date(row["transaction_date"])
            tx_type_raw = row["transaction_type"].strip()
            tx_type = tx_map.get(tx_type_raw, tx_type_raw.capitalize())
            amt = parse_float(row["amount_inr"])
            
            if amt <= 0:
                continue
                
            kyc = kyc_map.get(row["kyc_status"].strip(), "Pending")
            
            dedup_key = (inv_id, tx_dt, amfi_code, tx_type, amt, row["state"].strip())
            if dedup_key in seen:
                continue
            seen.add(dedup_key)
            
            cleaned_rows.append({
                "transaction_id": len(cleaned_rows) + 1,
                "investor_id": inv_id,
                "transaction_date": tx_dt,
                "amfi_code": amfi_code,
                "transaction_type": tx_type,
                "amount_inr": amt,
                "state": row["state"].strip(),
                "city": row["city"].strip(),
                "city_tier": row["city_tier"].strip(),
                "age_group": row["age_group"].strip(),
                "gender": row["gender"].strip(),
                "annual_income_lakh": parse_float(row["annual_income_lakh"]),
                "payment_mode": row["payment_mode"].strip(),
                "kyc_status": kyc
            })
            
    return cleaned_rows


def clean_scheme_performance():
    raw_file = os.path.join(RAW_DIR, "07_scheme_performance.csv")
    cleaned_rows = []
    seen = set()
    
    with open(raw_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            amfi_code = row["amfi_code"].strip()
            if amfi_code in seen:
                continue
            seen.add(amfi_code)
            
            er = parse_float(row["expense_ratio_pct"])
            if er < 0.10:
                er = 0.10
            elif er > 2.50:
                er = 2.50
                
            cleaned_rows.append({
                "amfi_code": amfi_code,
                "scheme_name": row["scheme_name"].strip(),
                "fund_house": row["fund_house"].strip(),
                "category": row["category"].strip(),
                "plan": row["plan"].strip(),
                "return_1yr_pct": parse_float(row["return_1yr_pct"]),
                "return_3yr_pct": parse_float(row["return_3yr_pct"]),
                "return_5yr_pct": parse_float(row["return_5yr_pct"]),
                "benchmark_3yr_pct": parse_float(row["benchmark_3yr_pct"]),
                "alpha": parse_float(row["alpha"]),
                "beta": parse_float(row["beta"]),
                "sharpe_ratio": parse_float(row["sharpe_ratio"]),
                "sortino_ratio": parse_float(row["sortino_ratio"]),
                "std_dev_ann_pct": parse_float(row["std_dev_ann_pct"]),
                "max_drawdown_pct": parse_float(row["max_drawdown_pct"]),
                "aum_crore": parse_float(row["aum_crore"]),
                "expense_ratio_pct": er,
                "morningstar_rating": parse_int(row["morningstar_rating"]),
                "risk_grade": row["risk_grade"].strip()
            })
            
    return cleaned_rows


def clean_aum_by_fund_house():
    raw_file = os.path.join(RAW_DIR, "03_aum_by_fund_house.csv")
    cleaned_rows = []
    seen = set()
    with open(raw_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            dt = parse_date(row["date"])
            fh = row["fund_house"].strip()
            key = (dt, fh)
            if key in seen:
                continue
            seen.add(key)
            cleaned_rows.append({
                "date": dt,
                "fund_house": fh,
                "aum_lakh_crore": parse_float(row["aum_lakh_crore"]),
                "aum_crore": parse_float(row["aum_crore"]),
                "num_schemes": parse_int(row["num_schemes"])
            })
    return cleaned_rows


def clean_monthly_sip_inflows():
    raw_file = os.path.join(RAW_DIR, "04_monthly_sip_inflows.csv")
    cleaned_rows = []
    seen = set()
    with open(raw_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            m = row["month"].strip()
            if m in seen:
                continue
            seen.add(m)
            cleaned_rows.append({
                "month": m,
                "sip_inflow_crore": parse_float(row["sip_inflow_crore"]),
                "active_sip_accounts_crore": parse_float(row["active_sip_accounts_crore"]),
                "new_sip_accounts_lakh": parse_float(row["new_sip_accounts_lakh"]),
                "sip_aum_lakh_crore": parse_float(row["sip_aum_lakh_crore"]),
                "yoy_growth_pct": parse_float(row["yoy_growth_pct"])
            })
    return cleaned_rows


def clean_category_inflows():
    raw_file = os.path.join(RAW_DIR, "05_category_inflows.csv")
    cleaned_rows = []
    seen = set()
    with open(raw_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            m = row["month"].strip()
            cat = row["category"].strip()
            key = (m, cat)
            if key in seen:
                continue
            seen.add(key)
            cleaned_rows.append({
                "month": m,
                "category": cat,
                "net_inflow_crore": parse_float(row["net_inflow_crore"])
            })
    return cleaned_rows


def clean_industry_folio_count():
    raw_file = os.path.join(RAW_DIR, "06_industry_folio_count.csv")
    cleaned_rows = []
    seen = set()
    with open(raw_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            m = row["month"].strip()
            if m in seen:
                continue
            seen.add(m)
            cleaned_rows.append({
                "month": m,
                "total_folios_crore": parse_float(row["total_folios_crore"]),
                "equity_folios_crore": parse_float(row["equity_folios_crore"]),
                "debt_folios_crore": parse_float(row["debt_folios_crore"]),
                "hybrid_folios_crore": parse_float(row["hybrid_folios_crore"]),
                "others_folios_crore": parse_float(row["others_folios_crore"])
            })
    return cleaned_rows


def clean_portfolio_holdings():
    raw_file = os.path.join(RAW_DIR, "09_portfolio_holdings.csv")
    cleaned_rows = []
    seen = set()
    with open(raw_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            amfi = row["amfi_code"].strip()
            stock_sym = row["stock_symbol"].strip()
            dt = parse_date(row["portfolio_date"])
            key = (amfi, stock_sym, dt)
            if key in seen:
                continue
            seen.add(key)
            cleaned_rows.append({
                "holding_id": len(cleaned_rows) + 1,
                "amfi_code": amfi,
                "stock_symbol": stock_sym,
                "stock_name": row["stock_name"].strip(),
                "sector": row["sector"].strip(),
                "weight_pct": parse_float(row["weight_pct"]),
                "market_value_cr": parse_float(row["market_value_cr"]),
                "current_price_inr": parse_float(row["current_price_inr"]),
                "portfolio_date": dt
            })
    return cleaned_rows


def clean_benchmark_indices():
    raw_file = os.path.join(RAW_DIR, "10_benchmark_indices.csv")
    cleaned_rows = []
    seen = set()
    with open(raw_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            dt = parse_date(row["date"])
            idx_name = row["index_name"].strip()
            key = (dt, idx_name)
            if key in seen:
                continue
            seen.add(key)
            cleaned_rows.append({
                "date": dt,
                "index_name": idx_name,
                "close_value": parse_float(row["close_value"])
            })
    return cleaned_rows


def generate_dim_date(start_str="2022-01-01", end_str="2026-12-31"):
    start_dt = datetime.strptime(start_str, "%Y-%m-%d").date()
    end_dt = datetime.strptime(end_str, "%Y-%m-%d").date()
    
    rows = []
    curr = start_dt
    while curr <= end_dt:
        dt_str = curr.strftime("%Y-%m-%d")
        quarter = (curr.month - 1) // 3 + 1
        is_weekend = 1 if curr.weekday() in (5, 6) else 0
        rows.append({
            "date": dt_str,
            "year": curr.year,
            "quarter": quarter,
            "month": curr.month,
            "month_name": curr.strftime("%B"),
            "day": curr.day,
            "day_of_week": curr.strftime("%A"),
            "is_weekend": is_weekend
        })
        curr += timedelta(days=1)
    return rows


def write_csv(filepath, rows):
    if not rows:
        return
    fieldnames = list(rows[0].keys())
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def load_table_into_sqlite(conn, table_name, rows):
    if not rows:
        return
    columns = list(rows[0].keys())
    placeholders = ", ".join(["?"] * len(columns))
    col_names = ", ".join(columns)
    sql = f"INSERT INTO {table_name} ({col_names}) VALUES ({placeholders})"
    
    data_tuples = [tuple(r[col] for col in columns) for r in rows]
    conn.executemany(sql, data_tuples)


def main():
    print("=== Starting Pure Python Data Cleaning & Ingestion Pipeline ===")
    
    # 1. Clean Datasets
    print("\n--- Cleaning CSV Datasets ---")
    fund_master = clean_fund_master()
    nav_history = clean_nav_history()
    transactions = clean_investor_transactions()
    performance = clean_scheme_performance()
    aum = clean_aum_by_fund_house()
    sip_inflows = clean_monthly_sip_inflows()
    category_inflows = clean_category_inflows()
    industry_folios = clean_industry_folio_count()
    holdings = clean_portfolio_holdings()
    benchmark = clean_benchmark_indices()
    dim_date = generate_dim_date()

    datasets = {
        "fund_master.csv": fund_master,
        "nav_history.csv": nav_history,
        "aum_by_fund_house.csv": aum,
        "monthly_sip_inflows.csv": sip_inflows,
        "category_inflows.csv": category_inflows,
        "industry_folio_count.csv": industry_folios,
        "scheme_performance.csv": performance,
        "investor_transactions.csv": transactions,
        "portfolio_holdings.csv": holdings,
        "benchmark_indices.csv": benchmark,
    }

    # 2. Export Cleaned CSVs
    print("\n--- Exporting 10 Cleaned CSVs to data/processed/ ---")
    for fname, rows in datasets.items():
        out_path = os.path.join(PROCESSED_DIR, fname)
        write_csv(out_path, rows)
        print(f" Saved {fname}: {len(rows)} rows")

    # 3. Create SQLite Database
    db_paths = [DB_PATH, DATA_DB_PATH]
    schema_file = ROOT_SCHEMA_PATH if os.path.exists(ROOT_SCHEMA_PATH) else SQL_SCHEMA_PATH
    
    with open(schema_file, "r", encoding="utf-8") as f:
        schema_sql = f.read()

    table_data_map = {
        "dim_fund": fund_master,
        "dim_date": dim_date,
        "fact_nav": nav_history,
        "fact_transactions": transactions,
        "fact_performance": performance,
        "fact_aum": aum,
        "fact_monthly_sip_inflows": sip_inflows,
        "fact_category_inflows": category_inflows,
        "fact_industry_folios": industry_folios,
        "fact_portfolio_holdings": holdings,
        "fact_benchmark_indices": benchmark
    }

    for db_p in db_paths:
        print(f"\n--- Initializing & Loading SQLite DB at {db_p} ---")
        if os.path.exists(db_p):
            os.remove(db_p)
            
        conn = sqlite3.connect(db_p)
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.executescript(schema_sql)
        
        for table_name, rows in table_data_map.items():
            load_table_into_sqlite(conn, table_name, rows)
            print(f" Loaded table '{table_name}': {len(rows)} rows")
            
        conn.commit()

        # 4. Verify Row Counts
        print(f"\n--- Verifying Row Counts in {os.path.basename(db_p)} ---")
        cursor = conn.cursor()
        for table_name, rows in table_data_map.items():
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            db_cnt = cursor.fetchone()[0]
            csv_cnt = len(rows)
            match = "MATCH" if db_cnt == csv_cnt else "MISMATCH"
            print(f" Table '{table_name}': DB Count = {db_cnt}, Cleaned CSV Count = {csv_cnt} -> {match}")
            
        conn.close()

    print("\n Data pipeline execution finished with clean success!")


if __name__ == "__main__":
    main()
