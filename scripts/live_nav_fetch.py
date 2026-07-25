import os
import requests
import pandas as pd

# Create folder if it doesn't exist
OUTPUT_FOLDER = "data/raw/live_nav"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Scheme Codes
schemes = {
    "125497": "HDFC_Top100_Direct",
    "119551": "SBI_Bluechip",
    "120503": "ICICI_Bluechip",
    "118632": "Nippon_Large_Cap",
    "119092": "Axis_Bluechip",
    "120841": "Kotak_Bluechip"
}

print("=" * 70)
print("Fetching Live NAV Data")
print("=" * 70)

for code, name in schemes.items():
    try:
        url = f"https://api.mfapi.in/mf/{code}"
        response = requests.get(url)
        response.raise_for_status()

        data = response.json()

        # Save NAV history
        nav_df = pd.DataFrame(data["data"])
        nav_df.to_csv(f"{OUTPUT_FOLDER}/{name}.csv", index=False)

        print(f"✅ {name} downloaded successfully.")

    except Exception as e:
        print(f"❌ Failed to fetch {name}")
        print(e)

print("\nAll NAV files downloaded.")