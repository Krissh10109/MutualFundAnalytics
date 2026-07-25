# Mutual Fund Analytics

A comprehensive Python and SQL-powered data analytics platform designed for tracking, evaluating, and visualizing mutual fund performance, risk metrics, and portfolio composition.

---

## 📁 Project Architecture

```
MutualFundAnalytics
│
├── data/
│   ├── raw/          # Raw ingested data (CSV, JSON, Excel dumps)
│   └── processed/    # Cleaned, standardized, and transformed datasets
│
├── notebooks/        # Jupyter Notebooks for exploratory data analysis (EDA)
│
├── sql/              # SQL schema definitions and analytical queries
│
├── dashboard/        # Interactive Streamlit dashboard application
│
├── reports/          # Generated analytical summary reports & exports
│
├── scripts/          # Modular Python packages and processing pipeline
│
├── requirements.txt  # Dependencies and environment setup specifications
│
├── README.md         # Project documentation and guide
│
└── .gitignore        # Git exclusion rules
```

---

## 🚀 Key Features & Functionalities

1. **NAV & Historical Performance Tracking**: Calculate daily returns, annualized returns, Compound Annual Growth Rate (CAGR), and rolling returns across 1-year, 3-year, and 5-year periods.
2. **Risk & Quantitative Metrics**:
   - **Volatility (Standard Deviation)**: Measure portfolio fluctuation.
   - **Sharpe & Sortino Ratios**: Risk-adjusted returns evaluation against risk-free benchmark rates.
   - **Alpha & Beta**: Sensitivity to benchmark indices (e.g., Nifty 50, S&P 500) and excess return generated.
   - **Maximum Drawdown**: Quantify peak-to-trough decline.
3. **Interactive Streamlit Dashboard**: Visualize equity vs debt allocation, compare mutual funds side-by-side, and dynamically track investment growth over time.
4. **SQL Analytics Engine**: Pre-built database schemas and queries for storing funds metadata, historical NAVs, and running complex analytical aggregates.

---

## 🛠️ Getting Started

### 1. Prerequisites
Ensure you have Python 3.9+ installed on your machine.

### 2. Installation & Environment Setup
Clone the repository and set up a virtual environment:

```bash
# Navigate to project directory
cd MutualFundAnalytics

# Create a virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Running Analytics Scripts
To run the automated data ingestion and analytics pipeline:

```bash
python scripts/main.py
```

### 4. Launching the Interactive Dashboard
To launch the interactive dashboard UI:

```bash
streamlit run dashboard/app.py
```

---

## 📊 Modules & Usage Overview

- **`scripts/data_loader.py`**: Handles downloading/ingesting raw mutual fund NAV records and cleaning data for analysis.
- **`scripts/metrics_calculator.py`**: Formulates quantitative financial metrics (Sharpe, Beta, CAGR, Drawdown).
- **`sql/schema.sql`**: Relational database tables for funds, NAV history, and asset allocations.
- **`sql/analysis_queries.sql`**: Analytical queries for top-performing funds, risk-adjusted rankings, and monthly trend analysis.

---

## 📜 License
This repository is maintained for Bluestock Internship / Analytical Portfolio purposes.
