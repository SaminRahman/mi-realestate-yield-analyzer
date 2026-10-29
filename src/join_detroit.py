"""
join_detroit.py
Join the cleaned Detroit sales to the Detroit assessment roll (one row per parcel)
and test two ideas with real data:
  1. Is "SEV x 2" a good estimate of what a home really sells for?
  2. After a sale, does taxable value jump up to the SEV ("uncapping")?
Owner-name and owner-address columns are never loaded.
"""

import pandas as pd

SALES = "data/processed/detroit_sales_clean.csv"
ASSESS = "data/raw/wayne_detroit_assessment.csv"
OUT = "data/processed/detroit_sales_joined.csv"

# The columns we need from the assessment file, with friendlier names
COLUMN_NAMES = {
    "Parcels.pnum": "parcel_id",
    "Parcels.propclass": "prop_class",
    "Parcels.schooldist": "school_district",
    "Parcels.homedate": "homestead_date",
    "ParcelMaster.resb_yearbuilt": "year_built",
    "ParcelMaster.resb_floorarea": "floor_area",
    "ParcelMaster.resb_nbed": "bedrooms",
    "ParcelMaster.resb_fullbaths": "full_baths",
    "ParcelMaster.resb_halfbaths": "half_baths",
    "ParcelReadonly.mborsev_1": "sev",            # latest year's SEV
    "ParcelReadonly.tax_1": "taxable_value",      # latest year's taxable value
}
NUMBER_COLUMNS = ["year_built", "floor_area", "bedrooms", "full_baths",
                  "half_baths", "sev", "taxable_value"]

sales = pd.read_csv(
    SALES,
    dtype={"Sales ID": str, "Parcel ID": str, "Zip Code": str},
    parse_dates=["Sale Date"],
)
assess = pd.read_csv(
    ASSESS, usecols=list(COLUMN_NAMES), dtype=str, low_memory=False
).rename(columns=COLUMN_NAMES)

for col in NUMBER_COLUMNS:
    assess[col] = pd.to_numeric(assess[col], errors="coerce")

# A join can multiply rows if a parcel number appears twice, so remove repeats first
before = len(assess)
assess = assess.drop_duplicates(subset="parcel_id")
print(f"Assessment rows: {before:,}; repeated parcel numbers removed: {before - len(assess):,}")

merged = sales.merge(assess, left_on="Parcel ID", right_on="parcel_id", how="left")
print(f"Sales before join: {len(sales):,}; after join: {len(merged):,} (these must be equal)")
print(f"Sales that found an assessment record: {merged['sev'].notna().sum():,}")

# Work only with sales that have both a value and a price
m = merged[(merged["sev"] > 0) & (merged["Sale Price"] > 0)].copy()
m["value_ratio"] = (m["sev"] * 2) / m["Sale Price"]  # 1.00 = assessor's value equals the price
m["taxable_to_sev"] = m["taxable_value"] / m["sev"]
m["sale_year"] = m["Sale Date"].dt.year

print("\n1) (SEV x 2) / sale price. 1.00 means a perfect match.")
print("Overall median:", round(m["value_ratio"].median(), 2))
bands = pd.cut(
    m["Sale Price"],
    [0, 30_000, 60_000, 100_000, 200_000, 1_000_000],
    labels=["under 30k", "30-60k", "60-100k", "100-200k", "200k+"],
)
print("\nBy sale price band (median ratio and number of sales):")
print(m.groupby(bands, observed=True)["value_ratio"].agg(["median", "count"]).round(2).to_string())

print("\n2) Taxable value / SEV by sale year. Near 1.00 means the tax base reset to SEV.")
print(m.groupby("sale_year")["taxable_to_sev"].median().round(2).to_string())

print("\n3) How complete are the house details? (share of sales with a real value)")
for col in ["year_built", "floor_area", "bedrooms", "full_baths"]:
    print(f"  {col:12s} {(merged[col] > 0).mean():.0%}")

merged.to_csv(OUT, index=False)
print(f"\nSaved {len(merged):,} rows to {OUT}")