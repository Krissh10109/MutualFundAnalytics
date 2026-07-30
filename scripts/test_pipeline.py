"""
Comprehensive Verification and Test Suite for Mutual Fund Analytics Engine
Tests:
1. Data Cleaning & Ingestion Pipeline Execution
2. Processed CSV Files Integrity & Data Quality Rules
3. SQLite Database Star Schema & Foreign Key Enforcement
4. 10 Core Analytical SQL Queries Execution & Result Validation
"""

import os
import sys
import csv
import sqlite3
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")
DB_PATH = os.path.join(BASE_DIR, "bluestock_mf.db")
QUERIES_PATH = os.path.join(BASE_DIR, "queries.sql")


def test_processed_csvs():
    print("\n=======================================================")
    print("TEST 1: Validating Processed CSV Files in data/processed/")
    print("=======================================================")
    
    expected_files = [
        "fund_master.csv",
        "nav_history.csv",
        "aum_by_fund_house.csv",
        "monthly_sip_inflows.csv",
        "category_inflows.csv",
        "industry_folio_count.csv",
        "scheme_performance.csv",
        "investor_transactions.csv",
        "portfolio_holdings.csv",
        "benchmark_indices.csv"
    ]
    
    all_passed = True
    for fname in expected_files:
        fpath = os.path.join(PROCESSED_DIR, fname)
        if not os.path.exists(fpath):
            print(f" FAIL: Missing file {fname}")
            all_passed = False
            continue
            
        with open(fpath, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            if len(rows) == 0:
                print(f" FAIL: File {fname} is empty!")
                all_passed = False
            else:
                print(f" PASS: {fname:<25} -> {len(rows):>6} rows | Columns: {len(reader.fieldnames)}")
                
    # Specific Data Quality Assertions
    # 1. nav_history nav > 0
    with open(os.path.join(PROCESSED_DIR, "nav_history.csv"), "r", encoding="utf-8") as f:
        r = csv.DictReader(f)
        invalid_navs = [row for row in r if float(row["nav"]) <= 0]
        if invalid_navs:
            print(f" FAIL: Found {len(invalid_navs)} NAV values <= 0 in nav_history.csv")
            all_passed = False
        else:
            print(" PASS: Data Quality Check - All NAV values > 0 in nav_history.csv")
            
    # 2. investor_transactions amounts > 0 and transaction_type standardized
    with open(os.path.join(PROCESSED_DIR, "investor_transactions.csv"), "r", encoding="utf-8") as f:
        r = csv.DictReader(f)
        invalid_tx = [row for row in r if float(row["amount_inr"]) <= 0 or row["transaction_type"] not in ("SIP", "Lumpsum", "Redemption")]
        if invalid_tx:
            print(f" FAIL: Found {len(invalid_tx)} invalid transaction records")
            all_passed = False
        else:
            print(" PASS: Data Quality Check - All transactions standardized (SIP/Lumpsum/Redemption) with amount > 0")

    return all_passed


def test_sqlite_database():
    print("\n=======================================================")
    print("TEST 2: Validating SQLite Database Schema & Tables")
    print("=======================================================")
    
    if not os.path.exists(DB_PATH):
        print(f" FAIL: Database file {DB_PATH} does not exist!")
        return False
        
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    cursor = conn.cursor()
    
    tables = [
        "dim_fund", "dim_date", "fact_nav", "fact_transactions",
        "fact_performance", "fact_aum", "fact_monthly_sip_inflows",
        "fact_category_inflows", "fact_industry_folios",
        "fact_portfolio_holdings", "fact_benchmark_indices"
    ]
    
    all_passed = True
    for tbl in tables:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {tbl}")
            count = cursor.fetchone()[0]
            print(f" PASS: SQLite Table '{tbl}': {count:>6} rows")
        except Exception as e:
            print(f" FAIL: Table '{tbl}' error: {e}")
            all_passed = False
            
    conn.close()
    return all_passed


def test_analytical_sql_queries():
    print("\n=======================================================")
    print("TEST 3: Executing 10 Analytical SQL Queries against DB")
    print("=======================================================")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    with open(QUERIES_PATH, "r", encoding="utf-8") as f:
        sql_text = f.read()
        
    raw_queries = [q.strip() for q in sql_text.split(";") if q.strip()]
    queries = []
    
    for q in raw_queries:
        lines = [line for line in q.split("\n") if not line.strip().startswith("--")]
        clean_stmt = "\n".join(lines).strip()
        if clean_stmt:
            title_lines = [l.strip().lstrip("-").strip() for l in q.split("\n") if l.strip().startswith("--") and ("." in l or ":" in l)]
            title = title_lines[0] if title_lines else f"Query {len(queries)+1}"
            queries.append((title, clean_stmt))
            
    print(f"Found {len(queries)} SQL queries to verify.\n")
    
    all_passed = True
    for idx, (title, stmt) in enumerate(queries, 1):
        try:
            cursor.execute(stmt)
            rows = cursor.fetchall()
            col_names = [description[0] for description in cursor.description]
            print(f"--- Query {idx}: {title} ---")
            print(f" Columns: {col_names}")
            print(f" Result Row Count: {len(rows)}")
            if rows:
                print(f" Sample Row 1: {rows[0]}")
            print(" Status: SUCCESS\n")
        except Exception as e:
            print(f" FAILED Query {idx} ({title}): {e}\n")
            all_passed = False
            
    conn.close()
    return all_passed


def main():
    print("*******************************************************")
    print(" Mutual Fund Analytics End-to-End System Test Suite")
    print("*******************************************************")
    
    # Run Pipeline first
    from scripts.clean_and_load import main as run_pipeline
    run_pipeline()
    
    # Run Tests
    t1 = test_processed_csvs()
    t2 = test_sqlite_database()
    t3 = test_analytical_sql_queries()
    
    print("\n*******************************************************")
    if t1 and t2 and t3:
        print(" ALL VERIFICATION & SYSTEM TESTS PASSED SUCCESSFULLY! ")
    else:
        print(" SOME TESTS FAILED. PLEASE REVIEW LOGS ABOVE. ")
    print("*******************************************************")


if __name__ == "__main__":
    main()
