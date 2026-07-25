"""
Data Loader Module for Mutual Fund Analytics.
Handles raw data generation/loading, cleaning, and preprocessing.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Tuple


def generate_synthetic_fund_data(days: int = 730) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Generates synthetic daily NAV dataset for demonstration and benchmarking.
    
    Args:
        days (int): Number of historical days to simulate (default 2 years / 730 days).
        
    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: DataFrames for Fund NAVs and Benchmark indices.
    """
    np.random.seed(42)
    end_date = datetime.today()
    start_date = end_date - timedelta(days=days)
    date_range = pd.date_range(start=start_date, end=end_date, freq='B') # Business days
    
    funds = {
        "Bluechip Equity Fund": {"start_nav": 100.0, "mu": 0.0005, "sigma": 0.011, "category": "Large Cap"},
        "Emerging Midcap Opportunities": {"start_nav": 50.0, "mu": 0.0007, "sigma": 0.016, "category": "Mid Cap"},
        "Smallcap Growth Fund": {"start_nav": 30.0, "mu": 0.0009, "sigma": 0.021, "category": "Small Cap"},
        "Balanced Hybrid Fund": {"start_nav": 40.0, "mu": 0.0004, "sigma": 0.007, "category": "Hybrid"},
    }
    
    nav_records = []
    
    for fund_name, params in funds.items():
        daily_returns = np.random.normal(params["mu"], params["sigma"], len(date_range))
        nav_values = params["start_nav"] * np.cumprod(1 + daily_returns)
        
        for date, nav in zip(date_range, nav_values):
            nav_records.append({
                "date": date.strftime("%Y-%m-%d"),
                "fund_name": fund_name,
                "category": params["category"],
                "nav": round(float(nav), 4)
            })
            
    df_funds = pd.DataFrame(nav_records)
    
    # Generate Benchmark Index (e.g. Nifty 50)
    benchmark_returns = np.random.normal(0.00045, 0.010, len(date_range))
    benchmark_values = 15000.0 * np.cumprod(1 + benchmark_returns)
    
    df_benchmark = pd.DataFrame({
        "date": date_range.strftime("%Y-%m-%d"),
        "index_name": "Benchmark Index (Nifty 50)",
        "close_price": np.round(benchmark_values, 2)
    })
    
    return df_funds, df_benchmark


def preprocess_nav_data(df_funds: pd.DataFrame) -> pd.DataFrame:
    """
    Cleans and pivots NAV data into wide format for daily returns calculations.
    """
    df_funds['date'] = pd.to_datetime(df_funds['date'])
    pivoted_df = df_funds.pivot(index='date', columns='fund_name', values='nav')
    pivoted_df = pivoted_df.ffill().bfill()
    return pivoted_df


if __name__ == "__main__":
    df_funds, df_bench = generate_synthetic_fund_data()
    print(f"Generated {len(df_funds)} fund records and {len(df_bench)} benchmark records.")
