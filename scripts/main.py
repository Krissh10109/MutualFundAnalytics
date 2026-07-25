"""
Main Processing Script for Mutual Fund Analytics Engine.
Runs end-to-end dataset generation, preprocessing, metric calculation, and report logging.
"""

import sys
import os
import pandas as pd

# Add root directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.data_loader import generate_synthetic_fund_data, preprocess_nav_data
from scripts.metrics_calculator import evaluate_fund_performance


def run_pipeline():
    print("=" * 60)
    print("Starting Mutual Fund Analytics Pipeline...")
    print("=" * 60)
    
    # 1. Load Data
    print("Generating / Fetching NAV records & Benchmark indices...")
    df_funds, df_benchmark = generate_synthetic_fund_data(days=730)
    
    # Save raw data
    raw_path_funds = os.path.join("data", "raw", "raw_fund_navs.csv")
    raw_path_bench = os.path.join("data", "raw", "raw_benchmark.csv")
    df_funds.to_csv(raw_path_funds, index=False)
    df_benchmark.to_csv(raw_path_bench, index=False)
    print(f"[OK] Raw datasets saved to:\n   - {raw_path_funds}\n   - {raw_path_bench}")
    
    # 2. Preprocess Data
    print("\nPreprocessing NAV daily time series...")
    pivot_nav = preprocess_nav_data(df_funds)
    
    bench_series = df_benchmark.set_index(pd.to_datetime(df_benchmark['date']))['close_price']
    
    # Save processed data
    proc_path = os.path.join("data", "processed", "processed_nav_matrix.csv")
    pivot_nav.to_csv(proc_path)
    print(f"[OK] Processed NAV matrix saved to: {proc_path}")
    
    # 3. Calculate Performance & Risk Metrics
    print("\nComputing Performance & Risk Metrics for all Mutual Funds...\n")
    results = []
    
    for fund_name in pivot_nav.columns:
        nav_series = pivot_nav[fund_name]
        metrics = evaluate_fund_performance(nav_series, bench_series)
        metrics["Fund Name"] = fund_name
        results.append(metrics)
        
    df_results = pd.DataFrame(results)
    # Reorder columns to put Fund Name first
    cols = ["Fund Name"] + [c for c in df_results.columns if c != "Fund Name"]
    df_results = df_results[cols]
    
    print(df_results.to_string(index=False))
    
    # Save report
    report_csv = os.path.join("reports", "performance_metrics_summary.csv")
    df_results.to_csv(report_csv, index=False)
    print(f"\n[OK] Summary metrics exported to: {report_csv}")
    print("=" * 60)
    print("Analytics Pipeline Execution Completed Successfully!")
    print("=" * 60)


if __name__ == "__main__":
    run_pipeline()
