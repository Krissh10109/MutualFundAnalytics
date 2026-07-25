-- =========================================================
-- Mutual Fund Analytics - Key Analytical SQL Queries
-- =========================================================

-- 1. Latest NAV for all mutual funds along with AMC details
SELECT 
    mf.fund_id,
    mf.fund_name,
    a.amc_name,
    mf.category,
    mf.expense_ratio,
    dn.nav_date,
    dn.nav_price AS latest_nav
FROM mutual_funds mf
JOIN amc a ON mf.amc_id = a.amc_id
JOIN daily_nav dn ON mf.fund_id = dn.fund_id
WHERE dn.nav_date = (
    SELECT MAX(nav_date) 
    FROM daily_nav 
    WHERE fund_id = mf.fund_id
)
ORDER BY mf.category, mf.fund_name;


-- 2. Calculate 1-Year Returns for each fund
WITH nav_1yr AS (
    SELECT 
        fund_id,
        nav_price AS current_nav,
        nav_date AS current_date
    FROM daily_nav
    WHERE nav_date = (SELECT MAX(nav_date) FROM daily_nav)
),
nav_prev AS (
    SELECT 
        fund_id,
        nav_price AS prev_nav,
        nav_date AS prev_date
    FROM daily_nav
    WHERE nav_date = (SELECT MAX(nav_date) - INTERVAL '1 YEAR' FROM daily_nav)
)
SELECT 
    mf.fund_name,
    mf.category,
    curr.current_nav,
    prev.prev_nav,
    ROUND(((curr.current_nav - prev.prev_nav) / prev.prev_nav) * 100, 2) AS return_1yr_pct
FROM nav_1yr curr
JOIN nav_prev prev ON curr.fund_id = prev.fund_id
JOIN mutual_funds mf ON curr.fund_id = mf.fund_id
ORDER BY return_1yr_pct DESC;


-- 3. Average Expense Ratio by Fund Category
SELECT 
    category,
    COUNT(fund_id) AS total_funds,
    ROUND(AVG(expense_ratio), 2) AS avg_expense_ratio,
    MIN(expense_ratio) AS min_expense_ratio,
    MAX(expense_ratio) AS max_expense_ratio
FROM mutual_funds
GROUP BY category
ORDER BY avg_expense_ratio ASC;


-- 4. Top Sector Allocation across all funds
SELECT 
    sector_name,
    ROUND(AVG(weight_percentage), 2) AS avg_sector_weight,
    COUNT(DISTINCT fund_id) AS funds_holding_sector
FROM sector_allocation
GROUP BY sector_name
ORDER BY avg_sector_weight DESC;
