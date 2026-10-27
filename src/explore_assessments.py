"""
explore_assessment.py
Decode the Wayne County assessment file. Hamtramck is small, so we test on it first.
We load only the columns we need and NEVER the owner-name / owner-address columns.
"""

import pandas as pd

PATH = "data/raw/wayne_hamtramck_assessment.csv"

KEEP = [
    "Parcels.pnum", "Parcels.propclass", "Parcels.useCode", "Parcels.schooldist",
    "Parcels.homedate", "Parcels.hometaxyear",
    "ParcelMaster.propstreetcombined", "ParcelMaster.propcity", "ParcelMaster.propzip",
    "ParcelMaster.lastSalePrice", "ParcelMaster.lastSaleDate", "ParcelMaster.esttcv",
    "ParcelMaster.resb_yearbuilt", "ParcelMaster.resb_floorarea",
    "ParcelMaster.resb_nbed", "ParcelMaster.resb_fullbaths", "ParcelMaster.resb_halfbaths",
]
VALUE_GUESSES = [  # columns that might hold assessed / taxable values
    "ParcelReadonly.ass_1", "ParcelReadonly.mborass_1",
    "ParcelReadonly.mborsev_1", "ParcelReadonly.mborsev_2", "ParcelReadonly.mborsev_3",
    "ParcelReadonly.tax_1", "ParcelReadonly.tax_2", "ParcelReadonly.tax_3",
]

df = pd.read_csv(PATH, usecols=KEEP + VALUE_GUESSES, dtype=str, low_memory=False)


def num(series):
    """Turn text into numbers; anything unreadable becomes 'not a number'."""
    return pd.to_numeric(series, errors="coerce")


print("Parcels:", len(df))

print("\nProperty classes (10 most common):")
print(df["Parcels.propclass"].value_counts().head(10).to_string())

print("\nFive parcels that have a house on them (no owner data):")
has_house = num(df["ParcelMaster.resb_yearbuilt"]) > 0
print(df[has_house].head(5).T.to_string())

tcv = num(df["ParcelMaster.esttcv"])
ok = tcv > 0
print(f"\nParcels with an estimated true cash value: {ok.sum()}")
print("\nMedian of (column / estimated true cash value). SEV should be near 0.50:")
for col in VALUE_GUESSES:
    ratio = num(df[col])[ok] / tcv[ok]
    print(f"  {col:28s} {ratio.median():.2f}")

price = num(df["ParcelMaster.lastSalePrice"])
print("\nLast sale price: parcels with a price:", (price > 0).sum(), "| $1 sales:", (price == 1).sum())
years = pd.to_datetime(df["ParcelMaster.lastSaleDate"], errors="coerce").dt.year
print("Last sale year (most recent 10 years in the file):")
print(years.value_counts().sort_index().tail(10).to_string())