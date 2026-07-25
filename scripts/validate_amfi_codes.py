import pandas as pd

# Load datasets
fund_master = pd.read_csv("data/raw/01_fund_master.csv")
nav_history = pd.read_csv("data/raw/02_nav_history.csv")

print("=" * 80)
print("AMFI CODE VALIDATION")
print("=" * 80)

print("\nNAV History Columns:")
print(nav_history.columns.tolist())

# Change this if the NAV file uses a different column name
nav_column = "amfi_code"

fund_codes = set(fund_master["amfi_code"])
nav_codes = set(nav_history[nav_column])

missing_codes = fund_codes - nav_codes

print(f"\nTotal Fund Master Codes : {len(fund_codes)}")
print(f"Total NAV History Codes : {len(nav_codes)}")

if len(missing_codes) == 0:
    print("\n✅ All AMFI codes are present in NAV history.")
else:
    print(f"\n❌ Missing Codes: {len(missing_codes)}")
    print(sorted(missing_codes))