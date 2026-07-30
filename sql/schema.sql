-- =========================================================
-- Bluestock Mutual Fund Analytics Database Schema (SQLite)
-- Star Schema Architecture defining Dimensions and Fact Tables
-- =========================================================

PRAGMA foreign_keys = ON;

-- 1. Fund Dimension Table
CREATE TABLE IF NOT EXISTS dim_fund (
    amfi_code TEXT PRIMARY KEY,
    fund_house TEXT NOT NULL,
    scheme_name TEXT NOT NULL,
    category TEXT NOT NULL,
    sub_category TEXT,
    plan TEXT,
    launch_date TEXT,
    benchmark TEXT,
    expense_ratio_pct REAL,
    exit_load_pct REAL,
    min_sip_amount REAL,
    min_lumpsum_amount REAL,
    fund_manager TEXT,
    risk_category TEXT,
    sebi_category_code TEXT
);

-- 2. Date Dimension Table
CREATE TABLE IF NOT EXISTS dim_date (
    date TEXT PRIMARY KEY, -- YYYY-MM-DD
    year INTEGER NOT NULL,
    quarter INTEGER NOT NULL,
    month INTEGER NOT NULL,
    month_name TEXT NOT NULL,
    day INTEGER NOT NULL,
    day_of_week TEXT NOT NULL,
    is_weekend INTEGER NOT NULL
);

-- 3. Daily NAV Fact Table
CREATE TABLE IF NOT EXISTS fact_nav (
    amfi_code TEXT NOT NULL,
    date TEXT NOT NULL,
    nav REAL NOT NULL,
    repurchase_price REAL,
    sale_price REAL,
    PRIMARY KEY (amfi_code, date),
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code) ON DELETE CASCADE,
    FOREIGN KEY (date) REFERENCES dim_date(date) ON DELETE CASCADE
);

-- 4. Investor Transactions Fact Table
CREATE TABLE IF NOT EXISTS fact_transactions (
    transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
    investor_id TEXT NOT NULL,
    transaction_date TEXT NOT NULL,
    amfi_code TEXT NOT NULL,
    transaction_type TEXT NOT NULL, -- SIP, Lumpsum, Redemption
    amount_inr REAL NOT NULL,
    state TEXT,
    city TEXT,
    city_tier TEXT,
    age_group TEXT,
    gender TEXT,
    annual_income_lakh REAL,
    payment_mode TEXT,
    kyc_status TEXT NOT NULL, -- Verified, Pending
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code) ON DELETE CASCADE,
    FOREIGN KEY (transaction_date) REFERENCES dim_date(date) ON DELETE CASCADE
);

-- 5. Scheme Performance & Risk Metrics Fact Table
CREATE TABLE IF NOT EXISTS fact_performance (
    amfi_code TEXT PRIMARY KEY,
    scheme_name TEXT NOT NULL,
    fund_house TEXT NOT NULL,
    category TEXT NOT NULL,
    plan TEXT,
    return_1yr_pct REAL,
    return_3yr_pct REAL,
    return_5yr_pct REAL,
    benchmark_3yr_pct REAL,
    alpha REAL,
    beta REAL,
    sharpe_ratio REAL,
    sortino_ratio REAL,
    std_dev_ann_pct REAL,
    max_drawdown_pct REAL,
    aum_crore REAL,
    expense_ratio_pct REAL,
    morningstar_rating INTEGER,
    risk_grade TEXT,
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code) ON DELETE CASCADE
);

-- 6. AMC AUM History Fact Table
CREATE TABLE IF NOT EXISTS fact_aum (
    date TEXT NOT NULL,
    fund_house TEXT NOT NULL,
    aum_lakh_crore REAL,
    aum_crore REAL,
    num_schemes INTEGER,
    PRIMARY KEY (date, fund_house),
    FOREIGN KEY (date) REFERENCES dim_date(date) ON DELETE CASCADE
);

-- 7. Monthly SIP Inflows Fact Table
CREATE TABLE IF NOT EXISTS fact_monthly_sip_inflows (
    month TEXT PRIMARY KEY,
    sip_inflow_crore REAL,
    active_sip_accounts_crore REAL,
    new_sip_accounts_lakh REAL,
    sip_aum_lakh_crore REAL,
    yoy_growth_pct REAL
);

-- 8. Category Monthly Net Inflows Fact Table
CREATE TABLE IF NOT EXISTS fact_category_inflows (
    month TEXT NOT NULL,
    category TEXT NOT NULL,
    net_inflow_crore REAL,
    PRIMARY KEY (month, category)
);

-- 9. Industry Folios Fact Table
CREATE TABLE IF NOT EXISTS fact_industry_folios (
    month TEXT PRIMARY KEY,
    total_folios_crore REAL,
    equity_folios_crore REAL,
    debt_folios_crore REAL,
    hybrid_folios_crore REAL,
    others_folios_crore REAL
);

-- 10. Portfolio Holdings Detail Fact Table
CREATE TABLE IF NOT EXISTS fact_portfolio_holdings (
    holding_id INTEGER PRIMARY KEY AUTOINCREMENT,
    amfi_code TEXT NOT NULL,
    stock_symbol TEXT,
    stock_name TEXT,
    sector TEXT,
    weight_pct REAL,
    market_value_cr REAL,
    current_price_inr REAL,
    portfolio_date TEXT,
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code) ON DELETE CASCADE
);

-- 11. Benchmark Daily Indices Fact Table
CREATE TABLE IF NOT EXISTS fact_benchmark_indices (
    date TEXT NOT NULL,
    index_name TEXT NOT NULL,
    close_value REAL NOT NULL,
    PRIMARY KEY (date, index_name),
    FOREIGN KEY (date) REFERENCES dim_date(date) ON DELETE CASCADE
);
