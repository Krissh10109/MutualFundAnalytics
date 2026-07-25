"""
Quantitative Risk & Financial Metrics Calculator for Mutual Funds.
Calculates CAGR, Sharpe Ratio, Sortino Ratio, Volatility, Beta, Alpha, and Max Drawdown.
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, Tuple


def calculate_cagr(start_val: float, end_val: float, years: float) -> float:
    """Calculates Compound Annual Growth Rate (CAGR)."""
    if start_val <= 0 or years <= 0:
        return 0.0
    return ((end_val / start_val) ** (1 / years)) - 1


def calculate_volatility(daily_returns: pd.Series, annualize_factor: int = 252) -> float:
    """Calculates annualized volatility (standard deviation)."""
    return daily_returns.std() * np.sqrt(annualize_factor)


def calculate_sharpe_ratio(daily_returns: pd.Series, risk_free_rate: float = 0.06, annualize_factor: int = 252) -> float:
    """Calculates annualized Sharpe Ratio."""
    annualized_return = (1 + daily_returns.mean()) ** annualize_factor - 1
    annualized_vol = calculate_volatility(daily_returns, annualize_factor)
    if annualized_vol == 0:
        return 0.0
    return (annualized_return - risk_free_rate) / annualized_vol


def calculate_sortino_ratio(daily_returns: pd.Series, risk_free_rate: float = 0.06, annualize_factor: int = 252) -> float:
    """Calculates annualized Sortino Ratio focusing on downside risk."""
    annualized_return = (1 + daily_returns.mean()) ** annualize_factor - 1
    downside_returns = daily_returns[daily_returns < 0]
    downside_std = downside_returns.std() * np.sqrt(annualize_factor)
    if downside_std == 0:
        return 0.0
    return (annualized_return - risk_free_rate) / downside_std


def calculate_max_drawdown(nav_series: pd.Series) -> float:
    """Calculates Maximum Drawdown (peak-to-trough drop)."""
    cumulative_max = nav_series.cummax()
    drawdowns = (nav_series - cumulative_max) / cumulative_max
    return float(drawdowns.min())


def calculate_beta_alpha(fund_returns: pd.Series, benchmark_returns: pd.Series, risk_free_rate: float = 0.06) -> Tuple[float, float]:
    """Calculates Beta and Jensen's Alpha against a benchmark."""
    aligned_df = pd.concat([fund_returns, benchmark_returns], axis=1).dropna()
    aligned_df.columns = ['fund', 'benchmark']
    
    covariance = aligned_df['fund'].cov(aligned_df['benchmark'])
    benchmark_variance = aligned_df['benchmark'].var()
    
    if benchmark_variance == 0:
        return 1.0, 0.0
        
    beta = covariance / benchmark_variance
    
    ann_fund_return = (1 + aligned_df['fund'].mean()) ** 252 - 1
    ann_bench_return = (1 + aligned_df['benchmark'].mean()) ** 252 - 1
    
    alpha = ann_fund_return - (risk_free_rate + beta * (ann_bench_return - risk_free_rate))
    return float(beta), float(alpha)


def evaluate_fund_performance(nav_series: pd.Series, benchmark_series: pd.Series = None) -> Dict[str, Any]:
    """
    Evaluates complete quantitative performance summary for a fund.
    """
    daily_returns = nav_series.pct_change().dropna()
    start_val = nav_series.iloc[0]
    end_val = nav_series.iloc[-1]
    years = len(nav_series) / 252.0
    
    cagr = calculate_cagr(start_val, end_val, years)
    volatility = calculate_volatility(daily_returns)
    sharpe = calculate_sharpe_ratio(daily_returns)
    sortino = calculate_sortino_ratio(daily_returns)
    max_dd = calculate_max_drawdown(nav_series)
    
    beta, alpha = None, None
    if benchmark_series is not None:
        bench_returns = benchmark_series.pct_change().dropna()
        beta, alpha = calculate_beta_alpha(daily_returns, bench_returns)
        
    return {
        "Start NAV": round(float(start_val), 2),
        "Current NAV": round(float(end_val), 2),
        "CAGR (%)": round(cagr * 100, 2),
        "Volatility (%)": round(volatility * 100, 2),
        "Sharpe Ratio": round(sharpe, 2),
        "Sortino Ratio": round(sortino, 2),
        "Max Drawdown (%)": round(max_dd * 100, 2),
        "Beta": round(beta, 2) if beta is not None else "N/A",
        "Alpha (%)": round(alpha * 100, 2) if alpha is not None else "N/A",
    }
