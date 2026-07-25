import os
import pandas as pd

DATA_FOLDER = "data/raw"

print("=" * 80)
print("MUTUAL FUND DATA INGESTION REPORT")
print("=" * 80)

csv_files = sorted(
    [file for file in os.listdir(DATA_FOLDER) if file.endswith(".csv")]
)

for file in csv_files:

    print("\n" + "=" * 80)
    print(f"Dataset: {file}")
    print("=" * 80)

    file_path = os.path.join(DATA_FOLDER, file)

    try:
        df = pd.read_csv(file_path)

        print(f"\nShape: {df.shape}")

        print("\nColumns:")
        print(df.columns.tolist())

        print("\nData Types:")
        print(df.dtypes)

        print("\nFirst 5 Rows:")
        print(df.head())

        print("\nMissing Values:")
        print(df.isnull().sum())

        print(f"\nDuplicate Rows: {df.duplicated().sum()}")

    except Exception as e:
        print(f"❌ Error reading {file}")
        print(e)

print("\n" + "=" * 80)
print("All datasets processed successfully!")
print("=" * 80)