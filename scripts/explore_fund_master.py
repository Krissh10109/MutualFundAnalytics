import pandas as pd

df = pd.read_csv("data/raw/01_fund_master.csv")

print("=" * 80)
print("FUND MASTER EXPLORATION")
print("=" * 80)

print("\nDataset Shape:")
print(df.shape)

print("\nColumns:")
print(df.columns.tolist())

print("\nUnique Fund Houses:")
print(df["fund_house"].unique())

print("\nUnique Categories:")
print(df["category"].unique())

print("\nUnique Sub Categories:")
print(df["sub_category"].unique())

print("\nUnique Risk Categories:")
print(df["risk_category"].unique())

print("\nNumber of Unique AMFI Codes:")
print(df["amfi_code"].nunique())