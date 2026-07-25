-- =========================================================
-- Mutual Fund Analytics Database Schema
-- Compatible with PostgreSQL / MySQL / SQLite
-- =========================================================

-- 1. Asset Management Companies (AMCs) / Fund Houses
CREATE TABLE IF NOT EXISTS amc (
    amc_id INT PRIMARY KEY AUTO_INCREMENT,
    amc_name VARCHAR(255) NOT NULL UNIQUE,
    website VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Mutual Fund Master Table
CREATE TABLE IF NOT EXISTS mutual_funds (
    fund_id INT PRIMARY KEY AUTO_INCREMENT,
    amc_id INT NOT NULL,
    fund_name VARCHAR(255) NOT NULL,
    category VARCHAR(100) NOT NULL, -- Large Cap, Mid Cap, Small Cap, Hybrid, Debt
    sub_category VARCHAR(100),
    risk_rating VARCHAR(50), -- Low, Moderate, High, Very High
    expense_ratio DECIMAL(5, 2), -- e.g., 0.75 for 0.75%
    benchmark_index VARCHAR(100), -- Nifty 50, Nifty Midcap 150, etc.
    inception_date DATE,
    FOREIGN KEY (amc_id) REFERENCES amc(amc_id) ON DELETE CASCADE
);

-- 3. Daily Net Asset Value (NAV) Records
CREATE TABLE IF NOT EXISTS daily_nav (
    nav_id BIGINT PRIMARY KEY AUTO_INCREMENT,
    fund_id INT NOT NULL,
    nav_date DATE NOT NULL,
    nav_price DECIMAL(10, 4) NOT NULL,
    repurchase_price DECIMAL(10, 4),
    sale_price DECIMAL(10, 4),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (fund_id, nav_date),
    FOREIGN KEY (fund_id) REFERENCES mutual_funds(fund_id) ON DELETE CASCADE
);

-- 4. Benchmark Daily Index Values
CREATE TABLE IF NOT EXISTS benchmark_data (
    benchmark_id INT PRIMARY KEY AUTO_INCREMENT,
    index_name VARCHAR(100) NOT NULL,
    trade_date DATE NOT NULL,
    close_price DECIMAL(12, 4) NOT NULL,
    UNIQUE (index_name, trade_date)
);

-- 5. Portfolio Sector Allocation
CREATE TABLE IF NOT EXISTS sector_allocation (
    allocation_id INT PRIMARY KEY AUTO_INCREMENT,
    fund_id INT NOT NULL,
    sector_name VARCHAR(100) NOT NULL,
    weight_percentage DECIMAL(5, 2) NOT NULL,
    as_of_date DATE NOT NULL,
    FOREIGN KEY (fund_id) REFERENCES mutual_funds(fund_id) ON DELETE CASCADE
);
