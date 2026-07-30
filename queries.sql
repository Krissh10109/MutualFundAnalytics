-- =====================================================================
-- Bluestock Mutual Fund Analytics - 10 Core Analytical SQL Queries
-- Target Database: bluestock_mf.db (SQLite Star Schema)
-- =====================================================================

-- ---------------------------------------------------------------------
-- 1. Top 5 Mutual Funds by AUM (Assets Under Management)
-- Business Goal: Identify the largest fund schemes by AUM.
-- ---------------------------------------------------------------------
SELECT 
    p.amfi_code,
    p.scheme_name,
    p.fund_house,
    p.category,
    p.aum_crore,
    p.expense_ratio_pct,
    p.morningstar_rating
FROM fact_performance p
ORDER BY p.aum_crore DESC
LIMIT 5;


-- ---------------------------------------------------------------------
-- 2. Average NAV per Month per Fund Category
-- Business Goal: Track average daily NAV valuation across fund categories over time.
-- ---------------------------------------------------------------------
SELECT 
    d.year,
    d.month,
    d.month_name,
    f.category,
    ROUND(AVG(n.nav), 4) AS avg_nav,
    MIN(n.nav) AS min_nav,
    MAX(n.nav) AS max_nav
FROM fact_nav n
JOIN dim_fund f ON n.amfi_code = f.amfi_code
JOIN dim_date d ON n.date = d.date
GROUP BY d.year, d.month, f.category
ORDER BY d.year DESC, d.month DESC, f.category;


-- ---------------------------------------------------------------------
-- 3. Monthly SIP Inflows & YoY Growth Rate Trend Analysis
-- Business Goal: Monitor systematic investment growth trends over monthly periods.
-- ---------------------------------------------------------------------
SELECT 
    month,
    sip_inflow_crore,
    active_sip_accounts_crore,
    new_sip_accounts_lakh,
    sip_aum_lakh_crore,
    yoy_growth_pct
FROM fact_monthly_sip_inflows
ORDER BY month DESC;


-- ---------------------------------------------------------------------
-- 4. Investor Transaction Count & Total Investment Amount by State
-- Business Goal: Analyze geographic distribution of mutual fund investments across India.
-- ---------------------------------------------------------------------
SELECT 
    t.state,
    COUNT(t.transaction_id) AS total_transactions,
    ROUND(SUM(t.amount_inr), 2) AS total_amount_inr,
    ROUND(AVG(t.amount_inr), 2) AS avg_transaction_amount_inr,
    COUNT(DISTINCT t.investor_id) AS unique_investors
FROM fact_transactions t
GROUP BY t.state
ORDER BY total_amount_inr DESC;


-- ---------------------------------------------------------------------
-- 5. Cost Efficiency: Mutual Funds with Low Expense Ratio (< 1.0%)
-- Business Goal: Identify cost-effective funds with superior cost structures.
-- ---------------------------------------------------------------------
SELECT 
    f.amfi_code,
    f.scheme_name,
    f.fund_house,
    f.category,
    p.expense_ratio_pct,
    p.return_3yr_pct,
    p.sharpe_ratio,
    p.morningstar_rating
FROM dim_fund f
JOIN fact_performance p ON f.amfi_code = p.amfi_code
WHERE p.expense_ratio_pct < 1.0
ORDER BY p.expense_ratio_pct ASC, p.return_3yr_pct DESC;


-- ---------------------------------------------------------------------
-- 6. Top Fund Houses by Latest Total AUM & Market Share
-- Business Goal: Evaluate AMC market concentration and ranking.
-- ---------------------------------------------------------------------
SELECT 
    fund_house,
    aum_crore,
    aum_lakh_crore,
    num_schemes,
    date AS as_of_date
FROM fact_aum
WHERE date = (SELECT MAX(date) FROM fact_aum)
ORDER BY aum_crore DESC
LIMIT 5;


-- ---------------------------------------------------------------------
-- 7. Risk-Adjusted Performance Analysis: Top Funds by Sharpe Ratio & Alpha
-- Business Goal: Rank funds that generate excess returns relative to risk.
-- ---------------------------------------------------------------------
SELECT 
    f.amfi_code,
    f.scheme_name,
    f.category,
    p.return_3yr_pct,
    p.return_5yr_pct,
    p.alpha,
    p.beta,
    p.sharpe_ratio,
    p.sortino_ratio,
    p.max_drawdown_pct
FROM dim_fund f
JOIN fact_performance p ON f.amfi_code = p.amfi_code
ORDER BY p.sharpe_ratio DESC, p.alpha DESC
LIMIT 10;


-- ---------------------------------------------------------------------
-- 8. Redemption vs Investment Ratio by State and City Tier
-- Business Goal: Track capital outflows (Redemption) against inflows (SIP/Lumpsum).
-- ---------------------------------------------------------------------
SELECT 
    t.state,
    t.city_tier,
    SUM(CASE WHEN t.transaction_type = 'SIP' THEN t.amount_inr ELSE 0 END) AS sip_amount,
    SUM(CASE WHEN t.transaction_type = 'Lumpsum' THEN t.amount_inr ELSE 0 END) AS lumpsum_amount,
    SUM(CASE WHEN t.transaction_type = 'Redemption' THEN t.amount_inr ELSE 0 END) AS redemption_amount,
    ROUND(
        SUM(CASE WHEN t.transaction_type = 'Redemption' THEN t.amount_inr ELSE 0 END) * 100.0 / 
        NULLIF(SUM(CASE WHEN t.transaction_type IN ('SIP', 'Lumpsum') THEN t.amount_inr ELSE 0 END), 0), 
        2
    ) AS redemption_to_investment_pct
FROM fact_transactions t
GROUP BY t.state, t.city_tier
ORDER BY redemption_to_investment_pct DESC;


-- ---------------------------------------------------------------------
-- 9. KYC Compliance Status Distribution across Demographics
-- Business Goal: Assess compliance risks by investor age group and gender.
-- ---------------------------------------------------------------------
SELECT 
    t.age_group,
    t.gender,
    COUNT(t.transaction_id) AS total_transactions,
    SUM(CASE WHEN t.kyc_status = 'Verified' THEN 1 ELSE 0 END) AS verified_count,
    SUM(CASE WHEN t.kyc_status = 'Pending' THEN 1 ELSE 0 END) AS pending_count,
    ROUND(
        SUM(CASE WHEN t.kyc_status = 'Verified' THEN 1 ELSE 0 END) * 100.0 / COUNT(t.transaction_id), 
        2
    ) AS kyc_verified_pct
FROM fact_transactions t
GROUP BY t.age_group, t.gender
ORDER BY t.age_group, t.gender;


-- ---------------------------------------------------------------------
-- 10. Sector Allocation Concentration Across Top Holdings
-- Business Goal: Measure portfolio diversification across underlying economic sectors.
-- ---------------------------------------------------------------------
SELECT 
    h.sector,
    COUNT(DISTINCT h.amfi_code) AS funds_holding_sector,
    ROUND(SUM(h.market_value_cr), 2) AS total_market_value_cr,
    ROUND(AVG(h.weight_pct), 2) AS avg_holding_weight_pct
FROM fact_portfolio_holdings h
GROUP BY h.sector
ORDER BY total_market_value_cr DESC;
