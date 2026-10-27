"""
explore_sales.py
Look inside the Detroit sales file BEFORE cleaning it. We want to know which
values appear in the columns that say whether a sale was a normal market sale.
We never load Grantor / Grantee (people's names).
"""

import pandas as pd

COLUMNS = [
    "Sales ID", "Parcel ID", "Address", "Sale Date", "Sale Price",
    "Terms of Sale", "Sale Verification", "Sale Instrument",
    "Property Transfer Percentage", "Multi Parcel Sale",
    "Property Class Code", "Property Class Description",
    "Zip Code", "Longitude", "Latitude",
]

df = pd.read_csv(
    "data/raw/detroit_sales.csv",
    usecols=COLUMNS,  # only these columns, so names are never loaded
    dtype={"Sales ID": str, "Parcel ID": str, "Zip Code": str},
)
df["Sale Date"] = pd.to_datetime(df["Sale Date"], errors="coerce")
df["Sale Price"] = pd.to_numeric(df["Sale Price"], errors="coerce")

print("Rows:", len(df))
print("Sale dates that could not be read:", df["Sale Date"].isna().sum())

print("\nSales per year:")
print(df["Sale Date"].dt.year.value_counts().sort_index().to_string())

print("\nSale price summary:")
print(df["Sale Price"].describe().round(0).to_string())
print("Sales of $1:", (df["Sale Price"] == 1).sum())
print("Sales of $1,000 or less:", (df["Sale Price"] <= 1000).sum())

for col in ["Terms of Sale", "Sale Verification", "Sale Instrument",
            "Multi Parcel Sale", "Property Class Description"]:
    print(f"\n{col} (15 most common):")
    print(df[col].value_counts(dropna=False).head(15).to_string())