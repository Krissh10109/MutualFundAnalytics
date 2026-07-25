import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as gg
import os
import sys

# Add project root directory to path for modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.data_loader import generate_synthetic_fund_data, preprocess_nav_data
from scripts.metrics_calculator import evaluate_fund_performance

# ---------------------------------------------------------
# Page Configuration & Custom CSS Styling
# ---------------------------------------------------------
st.set_page_config(
    page_title="MutualFundAnalytics | Bluestock",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Glassmorphic dark styling & modern typography
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }
    
    .main-title {
        font-size: 2.4rem;
        font-weight: 700;
        background: linear-gradient(135deg, #00F2FE 0%, #4FACFE 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0px;
    }
    
    .sub-title {
        color: #94A3B8;
        font-size: 1.05rem;
        margin-bottom: 2rem;
    }
    
    .metric-card {
        background: rgba(30, 41, 59, 0.7);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 18px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
        backdrop-filter: blur(8px);
        margin-bottom: 12px;
    }
    
    .metric-label {
        font-size: 0.85rem;
        color: #94A3B8;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .metric-value {
        font-size: 1.6rem;
        font-weight: 700;
        color: #F8FAFC;
    }
    
    .metric-delta {
        font-size: 0.85rem;
        font-weight: 600;
    }
    
    .delta-positive { color: #10B981; }
    .delta-negative { color: #EF4444; }
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------
# Load Data
# ---------------------------------------------------------
@st.cache_data
def get_dashboard_data():
    df_funds, df_bench = generate_synthetic_fund_data(days=730)
    pivot_nav = preprocess_nav_data(df_funds)
    bench_series = df_bench.set_index(pd.to_datetime(df_bench['date']))['close_price']
    return df_funds, pivot_nav, bench_series

df_funds_raw, pivot_nav, bench_series = get_dashboard_data()

# ---------------------------------------------------------
# Header Section
# ---------------------------------------------------------
st.markdown('<div class="main-title">Mutual Fund Analytics Dashboard</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Quantitative Performance, Risk Diagnostics & Benchmark Comparison | Powered by Bluestock</div>', unsafe_allow_html=True)

# ---------------------------------------------------------
# Sidebar Controls
# ---------------------------------------------------------
st.sidebar.image("https://img.icons8.com/isometric/100/line-chart.png", width=64)
st.sidebar.title("Analytics Controls")

selected_funds = st.sidebar.multiselect(
    "Select Funds to Compare:",
    options=list(pivot_nav.columns),
    default=list(pivot_nav.columns)
)

benchmark_compare = st.sidebar.checkbox("Include Benchmark (Nifty 50)", value=True)

time_frame = st.sidebar.radio(
    "Select Time Period:",
    options=["6 Months", "1 Year", "2 Years", "All Time"],
    index=3
)

# Filter date range based on radio
end_date = pivot_nav.index.max()
if time_frame == "6 Months":
    start_date = end_date - pd.DateOffset(months=6)
elif time_frame == "1 Year":
    start_date = end_date - pd.DateOffset(years=1)
elif time_frame == "2 Years":
    start_date = end_date - pd.DateOffset(years=2)
else:
    start_date = pivot_nav.index.min()

filtered_nav = pivot_nav.loc[start_date:end_date, selected_funds] if selected_funds else pivot_nav.loc[start_date:end_date]
filtered_bench = bench_series.loc[start_date:end_date]

# Normalize growth to 100 for indexing
normalized_nav = filtered_nav.div(filtered_nav.iloc[0]) * 100
normalized_bench = (filtered_bench / filtered_bench.iloc[0]) * 100

# ---------------------------------------------------------
# High-Level Metrics Summary Row
# ---------------------------------------------------------
st.subheader("📌 Key Fund Performance Summary")

if selected_funds:
    cols = st.columns(len(selected_funds))
    for idx, fund in enumerate(selected_funds):
        m = evaluate_fund_performance(filtered_nav[fund], filtered_bench)
        with cols[idx]:
            cagr = m["CAGR (%)"]
            sharpe = m["Sharpe Ratio"]
            beta = m["Beta"]
            
            delta_class = "delta-positive" if cagr >= 0 else "delta-negative"
            delta_sign = "+" if cagr >= 0 else ""
            
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">{fund}</div>
                <div class="metric-value">₹{m['Current NAV']:,.2f}</div>
                <div class="metric-delta {delta_class}">CAGR: {delta_sign}{cagr}%</div>
                <hr style="border:0.5px solid rgba(255,255,255,0.1); margin: 8px 0;">
                <div style="font-size:0.8rem; color:#94A3B8;">
                    Sharpe: <b>{sharpe}</b> | Beta: <b>{beta}</b>
                </div>
            </div>
            """, unsafe_allow_html=True)
else:
    st.info("Please select at least one mutual fund from the sidebar to view performance metrics.")

# ---------------------------------------------------------
# Growth Chart Section
# ---------------------------------------------------------
st.markdown("---")
st.subheader("📈 Rebased NAV Growth & Cumulative Return (Base 100)")

fig_growth = px.line(
    normalized_nav,
    labels={"value": "Rebased Index (Base 100)", "date": "Date", "variable": "Fund / Benchmark"},
    template="plotly_dark"
)

if benchmark_compare:
    fig_growth.add_scatter(
        x=normalized_bench.index,
        y=normalized_bench.values,
        mode='lines',
        name='Benchmark Index (Nifty 50)',
        line=dict(color='#F59E0B', dash='dash', width=2)
    )

fig_growth.update_layout(
    height=450,
    margin=dict(l=20, r=20, t=30, b=20),
    hovermode="x unified",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
)

st.plotly_chart(fig_growth, use_container_width=True)

# ---------------------------------------------------------
# Risk vs Return Matrix & Drawdown Analysis
# ---------------------------------------------------------
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("🎯 Risk vs. Return Matrix")
    metrics_list = []
    for fund in selected_funds:
        m = evaluate_fund_performance(filtered_nav[fund], filtered_bench)
        m["Fund"] = fund
        metrics_list.append(m)
        
    if metrics_list:
        df_m = pd.DataFrame(metrics_list)
        fig_scatter = px.scatter(
            df_m,
            x="Volatility (%)",
            y="CAGR (%)",
            size="Sharpe Ratio",
            color="Fund",
            text="Fund",
            labels={"Volatility (%)": "Annualized Risk / Volatility (%)", "CAGR (%)": "Expected Return / CAGR (%)"},
            template="plotly_dark"
        )
        fig_scatter.update_traces(textposition='top center', marker=dict(sizeref=0.1))
        fig_scatter.update_layout(height=380, showlegend=False)
        st.plotly_chart(fig_scatter, use_container_width=True)

with col_right:
    st.subheader("📉 Historical Drawdown Profile")
    if selected_funds:
        drawdown_df = pd.DataFrame()
        for fund in selected_funds:
            series = filtered_nav[fund]
            cum_max = series.cummax()
            drawdown_df[fund] = ((series - cum_max) / cum_max) * 100
            
        fig_dd = px.line(
            drawdown_df,
            labels={"value": "Drawdown (%)", "date": "Date"},
            template="plotly_dark"
        )
        fig_dd.update_layout(height=380, margin=dict(l=20, r=20, t=30, b=20))
        st.plotly_chart(fig_dd, use_container_width=True)

# ---------------------------------------------------------
# Comprehensive Quantitative Metrics Table
# ---------------------------------------------------------
st.markdown("---")
st.subheader("📋 Quantitative Performance Scorecard")

if metrics_list:
    scorecard_df = pd.DataFrame(metrics_list)
    cols_order = ["Fund", "Start NAV", "Current NAV", "CAGR (%)", "Volatility (%)", "Sharpe Ratio", "Sortino Ratio", "Max Drawdown (%)", "Beta", "Alpha (%)"]
    st.dataframe(
        scorecard_df[cols_order].style.highlight_max(axis=0, subset=["CAGR (%)", "Sharpe Ratio", "Sortino Ratio"], color="#065F46")
                                  .highlight_min(axis=0, subset=["Volatility (%)", "Max Drawdown (%)"], color="#7F1D1D"),
        use_container_width=True
    )
