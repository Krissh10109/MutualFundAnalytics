# Data Dictionary - Bluestock Mutual Fund Analytics Database

This data dictionary provides technical and business documentation for all tables, entity relationships, columns, data types, constraints, and source references within the `bluestock_mf.db` SQLite database and processed CSV datasets.

---

## 🏗️ Relational Architecture & Schema Overview

The database is built on a **Star Schema Architecture** designed for high-performance analytical queries and business intelligence reporting.

```
                         +-----------------------+
                         |       dim_date        |
                         +-----------------------+
                         | date (PK)             |
                         | year, quarter, month  |
                         | day_of_week, etc.     |
                         +-----------+-----------+
                                     |
           +-------------------------+-------------------------+
           |                         |                         |
+----------v----------+   +----------v----------+   +----------v----------+
|      fact_nav       |   |  fact_transactions  |   |      fact_aum       |
+---------------------+   +---------------------+   +---------------------+
| amfi_code (FK)      |   | transaction_id (PK) |   | date (FK), fund_house|
| date (FK)           |   | amfi_code (FK)      |   | aum_lakh_crore      |
| nav                 |   | transaction_date(FK)|   | aum_crore           |
+----------+----------+   | amount_inr, state   |   +---------------------+
           |              | transaction_type    |
           |              +----------+----------+
           |                         |
+----------v-------------------------v----------+
|                  dim_fund                     |
+-----------------------------------------------+
| amfi_code (PK)                                |
| scheme_name, fund_house, category, plan       |
| expense_ratio_pct, launch_date, benchmark     |
+-----------------------------------------------+
```

---

## 📊 Table Specifications

### 1. `dim_fund` (Fund Dimension Table)
- **Business Definition**: Master catalog of all mutual fund schemes tracked on the platform.
- **Primary Key**: `amfi_code`
- **Source File**: `data/processed/fund_master.csv` (Raw: `01_fund_master.csv`)

| Column Name | Data Type | Constraints | Nullable | Business Definition | Source Reference |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `amfi_code` | TEXT | PRIMARY KEY | No | Unique 6-digit AMFI scheme identifier code | `01_fund_master.csv` |
| `fund_house` | TEXT | NOT NULL | No | Name of the Asset Management Company (AMC) | `01_fund_master.csv` |
| `scheme_name` | TEXT | NOT NULL | No | Complete official scheme name | `01_fund_master.csv` |
| `category` | TEXT | NOT NULL | No | Primary asset category (Equity, Debt, Hybrid, Solution) | `01_fund_master.csv` |
| `sub_category` | TEXT | - | Yes | SEBI sub-category (Large Cap, Mid Cap, Liquid, etc.) | `01_fund_master.csv` |
| `plan` | TEXT | - | Yes | Plan type (Regular Plan, Direct Plan) | `01_fund_master.csv` |
| `launch_date` | TEXT | DATE (`YYYY-MM-DD`) | Yes | Inception / launch date of the mutual fund scheme | `01_fund_master.csv` |
| `benchmark` | TEXT | - | Yes | Primary benchmark index (e.g., NIFTY 100 TRI) | `01_fund_master.csv` |
| `expense_ratio_pct` | REAL | NUMERIC | Yes | Annual operational fee charged as percentage of AUM | `01_fund_master.csv` |
| `exit_load_pct` | REAL | NUMERIC | Yes | Penalty fee percentage for early redemption | `01_fund_master.csv` |
| `min_sip_amount` | REAL | NUMERIC | Yes | Minimum Systematic Investment Plan ticket size (INR) | `01_fund_master.csv` |
| `min_lumpsum_amount` | REAL | NUMERIC | Yes | Minimum one-time investment amount (INR) | `01_fund_master.csv` |
| `fund_manager` | TEXT | - | Yes | Lead portfolio manager handling the scheme | `01_fund_master.csv` |
| `risk_category` | TEXT | - | Yes | Riskometer rating (Low, Moderate, High, Very High) | `01_fund_master.csv` |
| `sebi_category_code` | TEXT | - | Yes | SEBI standardized category classification code | `01_fund_master.csv` |

---

### 2. `dim_date` (Date Dimension Table)
- **Business Definition**: Standardized calendar date dimension for temporal aggregation and roll-ups.
- **Primary Key**: `date`
- **Source File**: Generated calendar grid (`2022-01-01` to `2026-12-31`)

| Column Name | Data Type | Constraints | Nullable | Business Definition |
| :--- | :--- | :--- | :--- | :--- |
| `date` | TEXT | PRIMARY KEY (`YYYY-MM-DD`) | No | ISO calendar date string |
| `year` | INTEGER | NOT NULL | No | 4-digit calendar year (e.g., 2024) |
| `quarter` | INTEGER | NOT NULL | No | Calendar quarter (1 to 4) |
| `month` | INTEGER | NOT NULL | No | Calendar month index (1 to 12) |
| `month_name` | TEXT | NOT NULL | No | Full month name (e.g., January) |
| `day` | INTEGER | NOT NULL | No | Day of the month (1 to 31) |
| `day_of_week` | TEXT | NOT NULL | No | Name of the day (e.g., Monday) |
| `is_weekend` | INTEGER | 0 or 1 | No | Flag indicating weekend (1 = Saturday/Sunday, 0 = Weekday) |

---

### 3. `fact_nav` (Daily Net Asset Value Fact Table)
- **Business Definition**: Daily valuation price per unit (NAV) for each mutual fund scheme, forward-filled over weekends and holidays.
- **Primary Key**: Composite (`amfi_code`, `date`)
- **Foreign Keys**: `amfi_code` -> `dim_fund(amfi_code)`, `date` -> `dim_date(date)`
- **Source File**: `data/processed/nav_history.csv` (Raw: `02_nav_history.csv`)

| Column Name | Data Type | Constraints | Nullable | Business Definition | Source Reference |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `amfi_code` | TEXT | PK, FK -> `dim_fund` | No | AMFI unique scheme identifier | `02_nav_history.csv` |
| `date` | TEXT | PK, FK -> `dim_date` | No | Valuation date (`YYYY-MM-DD`) | `02_nav_history.csv` |
| `nav` | REAL | > 0 | No | Net Asset Value per unit in INR | `02_nav_history.csv` |
| `repurchase_price` | REAL | NUMERIC | Yes | Price at which AMC buys back units | `02_nav_history.csv` |
| `sale_price` | REAL | NUMERIC | Yes | Price at which investors purchase units | `02_nav_history.csv` |

---

### 4. `fact_transactions` (Investor Transactions Fact Table)
- **Business Definition**: Individual buy, sell, and systematic investment transaction records executed by retail/institutional investors.
- **Primary Key**: `transaction_id`
- **Foreign Keys**: `amfi_code` -> `dim_fund(amfi_code)`, `transaction_date` -> `dim_date(date)`
- **Source File**: `data/processed/investor_transactions.csv` (Raw: `08_investor_transactions.csv`)

| Column Name | Data Type | Constraints | Nullable | Business Definition | Source Reference |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `transaction_id` | INTEGER | PRIMARY KEY | No | Auto-incrementing unique transaction record ID | Generated / `08_investor_transactions.csv` |
| `investor_id` | TEXT | NOT NULL | No | Masked investor client account identifier | `08_investor_transactions.csv` |
| `transaction_date` | TEXT | FK -> `dim_date` | No | Execution date (`YYYY-MM-DD`) | `08_investor_transactions.csv` |
| `amfi_code` | TEXT | FK -> `dim_fund` | No | Target mutual fund scheme AMFI code | `08_investor_transactions.csv` |
| `transaction_type` | TEXT | Enum (`SIP`, `Lumpsum`, `Redemption`) | No | Type of transaction executed | `08_investor_transactions.csv` |
| `amount_inr` | REAL | > 0 | No | Transaction monetary volume in INR | `08_investor_transactions.csv` |
| `state` | TEXT | - | Yes | Indian state of investor residence | `08_investor_transactions.csv` |
| `city` | TEXT | - | Yes | City of investor residence | `08_investor_transactions.csv` |
| `city_tier` | TEXT | Enum (`T30`, `B30`) | Yes | Industry location tier (Top 30 vs Beyond 30 cities) | `08_investor_transactions.csv` |
| `age_group` | TEXT | - | Yes | Investor age demographic bracket | `08_investor_transactions.csv` |
| `gender` | TEXT | - | Yes | Investor gender | `08_investor_transactions.csv` |
| `annual_income_lakh` | REAL | NUMERIC | Yes | Investor reported annual household income (INR Lakh) | `08_investor_transactions.csv` |
| `payment_mode` | TEXT | - | Yes | Mode of payment (UPI, NetBanking, NACH, etc.) | `08_investor_transactions.csv` |
| `kyc_status` | TEXT | Enum (`Verified`, `Pending`) | No | Investor KYC regulatory compliance verification status | `08_investor_transactions.csv` |

---

### 5. `fact_performance` (Scheme Performance & Risk Metrics Fact Table)
- **Business Definition**: Risk-adjusted returns, historical CAGR, benchmark comparisons, and ratings for each fund.
- **Primary Key**: `amfi_code`
- **Foreign Key**: `amfi_code` -> `dim_fund(amfi_code)`
- **Source File**: `data/processed/scheme_performance.csv` (Raw: `07_scheme_performance.csv`)

| Column Name | Data Type | Constraints | Nullable | Business Definition | Source Reference |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `amfi_code` | TEXT | PK, FK -> `dim_fund` | No | AMFI unique scheme identifier | `07_scheme_performance.csv` |
| `scheme_name` | TEXT | NOT NULL | No | Scheme name | `07_scheme_performance.csv` |
| `fund_house` | TEXT | NOT NULL | No | Asset Management Company | `07_scheme_performance.csv` |
| `category` | TEXT | NOT NULL | No | Fund category | `07_scheme_performance.csv` |
| `plan` | TEXT | - | Yes | Plan type | `07_scheme_performance.csv` |
| `return_1yr_pct` | REAL | NUMERIC | Yes | 1-Year trailing annualized return percentage | `07_scheme_performance.csv` |
| `return_3yr_pct` | REAL | NUMERIC | Yes | 3-Year trailing annualized CAGR percentage | `07_scheme_performance.csv` |
| `return_5yr_pct` | REAL | NUMERIC | Yes | 5-Year trailing annualized CAGR percentage | `07_scheme_performance.csv` |
| `benchmark_3yr_pct` | REAL | NUMERIC | Yes | 3-Year benchmark index return percentage | `07_scheme_performance.csv` |
| `alpha` | REAL | NUMERIC | Yes | Risk-adjusted excess return relative to benchmark | `07_scheme_performance.csv` |
| `beta` | REAL | NUMERIC | Yes | Volatility sensitivity relative to market benchmark | `07_scheme_performance.csv` |
| `sharpe_ratio` | REAL | NUMERIC | Yes | Sharpe Ratio (Risk-free adjusted return / Standard Deviation) | `07_scheme_performance.csv` |
| `sortino_ratio` | REAL | NUMERIC | Yes | Sortino Ratio (Excess return / Downside Deviation) | `07_scheme_performance.csv` |
| `std_dev_ann_pct` | REAL | NUMERIC | Yes | Annualized return volatility (Standard Deviation) | `07_scheme_performance.csv` |
| `max_drawdown_pct` | REAL | NUMERIC | Yes | Maximum peak-to-trough historical drawdown loss % | `07_scheme_performance.csv` |
| `aum_crore` | REAL | NUMERIC | Yes | Scheme total AUM in INR Crore | `07_scheme_performance.csv` |
| `expense_ratio_pct` | REAL | 0.1% – 2.5% | Yes | Validated total expense ratio percentage | `07_scheme_performance.csv` |
| `morningstar_rating` | INTEGER | 1 to 5 | Yes | Morningstar star rating | `07_scheme_performance.csv` |
| `risk_grade` | TEXT | - | Yes | Qualitative risk grade rating | `07_scheme_performance.csv` |

---

### 6. `fact_aum` (AMC Assets Under Management Fact Table)
- **Business Definition**: Historical quarterly and monthly total AUM and scheme count per Fund House.
- **Primary Key**: Composite (`date`, `fund_house`)
- **Foreign Key**: `date` -> `dim_date(date)`
- **Source File**: `data/processed/aum_by_fund_house.csv` (Raw: `03_aum_by_fund_house.csv`)

| Column Name | Data Type | Constraints | Nullable | Business Definition | Source Reference |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `date` | TEXT | PK, FK -> `dim_date` | No | Reporting date (`YYYY-MM-DD`) | `03_aum_by_fund_house.csv` |
| `fund_house` | TEXT | PK | No | Name of Fund House / AMC | `03_aum_by_fund_house.csv` |
| `aum_lakh_crore` | REAL | NUMERIC | Yes | Total AUM in INR Lakh Crore | `03_aum_by_fund_house.csv` |
| `aum_crore` | REAL | NUMERIC | Yes | Total AUM in INR Crore | `03_aum_by_fund_house.csv` |
| `num_schemes` | INTEGER | NUMERIC | Yes | Total active schemes managed by AMC | `03_aum_by_fund_house.csv` |

---

### 7. `fact_monthly_sip_inflows`
- **Business Definition**: Macro industry-wide monthly SIP investment collection statistics across India.
- **Primary Key**: `month`
- **Source File**: `data/processed/monthly_sip_inflows.csv` (Raw: `04_monthly_sip_inflows.csv`)

| Column Name | Data Type | Constraints | Nullable | Business Definition |
| :--- | :--- | :--- | :--- | :--- |
| `month` | TEXT | PRIMARY KEY (`YYYY-MM`) | No | Industry reporting month |
| `sip_inflow_crore` | REAL | NUMERIC | Yes | Total monthly SIP contribution volume (INR Crore) |
| `active_sip_accounts_crore` | REAL | NUMERIC | Yes | Total active SIP accounts (in Crores) |
| `new_sip_accounts_lakh` | REAL | NUMERIC | Yes | New SIP accounts registered during month (in Lakhs) |
| `sip_aum_lakh_crore` | REAL | NUMERIC | Yes | Total cumulative SIP AUM (in Lakh Crores) |
| `yoy_growth_pct` | REAL | NUMERIC | Yes | Year-over-Year growth percentage |

---

### 8. `fact_category_inflows`
- **Business Definition**: Monthly net inflow / outflow trends segmented by mutual fund asset category.
- **Primary Key**: Composite (`month`, `category`)
- **Source File**: `data/processed/category_inflows.csv` (Raw: `05_category_inflows.csv`)

| Column Name | Data Type | Constraints | Nullable | Business Definition |
| :--- | :--- | :--- | :--- | :--- |
| `month` | TEXT | PK (`YYYY-MM`) | No | Reporting month |
| `category` | TEXT | PK | No | Asset category (Large Cap, Mid Cap, Hybrid, etc.) |
| `net_inflow_crore` | REAL | NUMERIC | Yes | Net capital inflows minus redemptions (INR Crore) |

---

### 9. `fact_industry_folios`
- **Business Definition**: Industry-wide investor account (folio) counts categorized by asset class.
- **Primary Key**: `month`
- **Source File**: `data/processed/industry_folio_count.csv` (Raw: `06_industry_folio_count.csv`)

| Column Name | Data Type | Constraints | Nullable | Business Definition |
| :--- | :--- | :--- | :--- | :--- |
| `month` | TEXT | PRIMARY KEY (`YYYY-MM`) | No | Reporting month |
| `total_folios_crore` | REAL | NUMERIC | Yes | Total mutual fund folios across industry (in Crores) |
| `equity_folios_crore` | REAL | NUMERIC | Yes | Equity scheme folios (Crores) |
| `debt_folios_crore` | REAL | NUMERIC | Yes | Debt scheme folios (Crores) |
| `hybrid_folios_crore` | REAL | NUMERIC | Yes | Hybrid scheme folios (Crores) |
| `others_folios_crore` | REAL | NUMERIC | Yes | ETF / Solution / Index folios (Crores) |

---

### 10. `fact_portfolio_holdings`
- **Business Definition**: Top stock holding compositions and sector allocations per fund scheme.
- **Primary Key**: `holding_id`
- **Foreign Key**: `amfi_code` -> `dim_fund(amfi_code)`
- **Source File**: `data/processed/portfolio_holdings.csv` (Raw: `09_portfolio_holdings.csv`)

| Column Name | Data Type | Constraints | Nullable | Business Definition |
| :--- | :--- | :--- | :--- | :--- |
| `holding_id` | INTEGER | PRIMARY KEY | No | Auto-incrementing holding record ID |
| `amfi_code` | TEXT | FK -> `dim_fund` | No | Target fund scheme AMFI code |
| `stock_symbol` | TEXT | NOT NULL | No | Ticker symbol of underlying stock |
| `stock_name` | TEXT | NOT NULL | No | Company corporate name |
| `sector` | TEXT | NOT NULL | No | Industry sector classification |
| `weight_pct` | REAL | NUMERIC | Yes | Holding weight as percentage of scheme portfolio |
| `market_value_cr` | REAL | NUMERIC | Yes | Market value of position in INR Crore |
| `current_price_inr` | REAL | NUMERIC | Yes | Underlying stock closing unit price in INR |
| `portfolio_date` | TEXT | DATE (`YYYY-MM-DD`) | Yes | Portfolio disclosure snapshot date |

---

### 11. `fact_benchmark_indices`
- **Business Definition**: Daily benchmark equity and debt index closing values.
- **Primary Key**: Composite (`date`, `index_name`)
- **Foreign Key**: `date` -> `dim_date(date)`
- **Source File**: `data/processed/benchmark_indices.csv` (Raw: `10_benchmark_indices.csv`)

| Column Name | Data Type | Constraints | Nullable | Business Definition |
| :--- | :--- | :--- | :--- | :--- |
| `date` | TEXT | PK, FK -> `dim_date` | No | Market trade date (`YYYY-MM-DD`) |
| `index_name` | TEXT | PK | No | Name of benchmark index (e.g., NIFTY50, NIFTY500) |
| `close_value` | REAL | > 0 | No | Benchmark index daily closing level |
