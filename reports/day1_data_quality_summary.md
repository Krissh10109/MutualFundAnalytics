# Day 1 - Data Quality Summary

## Overview

Successfully completed the data ingestion process for the Mutual Fund Analytics project.

---

## Datasets Loaded

- Total datasets loaded: 10
- All datasets were successfully read using Pandas.
- No unreadable or corrupted files were found.

---

## Fund Master Exploration

### Total Schemes
40

### Total Fund Houses
10

Fund Houses:
- SBI Mutual Fund
- HDFC Mutual Fund
- ICICI Prudential MF
- Nippon India MF
- Kotak Mahindra MF
- Axis Mutual Fund
- Aditya Birla Sun Life MF
- UTI Mutual Fund
- Mirae Asset MF
- DSP Mutual Fund

### Categories
- Equity
- Debt

### Sub Categories

- Large Cap
- Mid Cap
- Small Cap
- Flexi Cap
- Large & Mid Cap
- Value
- ELSS
- Index
- Index/ETF
- Liquid
- Gilt
- Short Duration

### Risk Categories

- Low
- Moderate
- Moderately High
- High
- Very High

---

## AMFI Code Validation

- Total AMFI Codes in Fund Master: 40
- Total AMFI Codes in NAV History: 40

Validation Result:

✅ Every AMFI code from the Fund Master dataset exists in the NAV History dataset.

---

## Live NAV Fetch

Successfully fetched live NAV history from MFAPI for:

- HDFC Top 100 Direct
- SBI Bluechip
- ICICI Bluechip
- Nippon Large Cap
- Axis Bluechip
- Kotak Bluechip

All datasets were successfully saved inside:

data/raw/live_nav/

---

## Overall Assessment

The datasets are clean, consistent, and suitable for ETL, exploratory analysis, SQL operations, dashboard creation, and further analytical processing.