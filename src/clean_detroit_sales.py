"""
clean_detroit_sales.py
Turn the raw Detroit sales file (542k rows, mostly NOT normal market sales)
into a small table of recent, residential, arm's-length sales.
Each filter prints how many rows survive, so we can see where rows disappear.
Grantor / Grantee (people's names) are never loaded.
"""

from pathlib import Path

import pandas as pd

RAW = "data/raw/detroit_sales.csv"
OUT = Path("data/processed/detroit_sales_clean.csv")

# Settings in one place, so they are easy to change later
START_DATE = "2023-01-01"        # only sales from this date on
MIN_PRICE = 10_000               # below this is rarely a livable home
MAX_PRICE = 1_000_000            # above this is rarely a normal house
KEEP_CLASSES = ["RESIDENTIAL"]   # no vacant land, commercial or condos (yet)

COLUMNS = [
    "Sales ID", "Parcel ID", "Address", "Sale Date", "Sale Price",
    "Terms of Sale", "Multi Parcel Sale", "Property Class Description",
    "Neighborhood", "Zip Code", "Longitude", "Latitude",
]

df = pd.read_csv(
    RAW,
    usecols=COLUMNS,
    dtype={"Sales ID": str, "Parcel ID": str, "Zip Code": str},
)
df["Sale Date"] = pd.to_datetime(df["Sale Date"], errors="coerce")
df["Sale Price"] = pd.to_numeric(df["Sale Price"], errors="coerce")


def step(label, frame):
    """Print how many rows are left after a filter, then pass the table on."""
    print(f"{label:<45s} {len(frame):>8,}")
    return frame


print(f"{'Filter':<45s} {'rows left':>8s}")
df = step("All rows in the file", df)
df = step("Sale date is not in the future", df[df["Sale Date"] <= pd.Timestamp.today()])
df = step(f"Sold on or after {START_DATE}", df[df["Sale Date"] >= START_DATE])
df = step("Terms of sale: arm's length", df[df["Terms of Sale"] == "03-ARM'S LENGTH"])
df = step("Only one parcel in the sale", df[df["Multi Parcel Sale"].astype(str).str.lower() == "false"])
df = step("Property class: residential", df[df["Property Class Description"].isin(KEEP_CLASSES)])
df = step(f"Price between {MIN_PRICE:,} and {MAX_PRICE:,}", df[df["Sale Price"].between(MIN_PRICE, MAX_PRICE)])
df = step("Has a map location", df.dropna(subset=["Latitude", "Longitude"]))
df = step("Duplicate sale IDs removed", df.drop_duplicates(subset="Sales ID"))

print("\nMedian sale price by year:")
print(df.groupby(df["Sale Date"].dt.year)["Sale Price"].median().round(0).to_string())

print("\nSales in the 10 busiest ZIP codes:")
print(df["Zip Code"].value_counts().head(10).to_string())

OUT.parent.mkdir(parents=True, exist_ok=True)
df.drop(columns=["Terms of Sale", "Multi Parcel Sale"]).to_csv(OUT, index=False)
print(f"\nSaved {len(df):,} rows to {OUT}")