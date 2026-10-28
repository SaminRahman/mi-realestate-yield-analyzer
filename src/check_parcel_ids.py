"""
check_parcel_ids.py
To join sales to assessments, the parcel numbers must look the same in both files.
Print a few of each, plus a test of how many match exactly.
"""

import pandas as pd

sales = pd.read_csv("data/processed/detroit_sales_clean.csv", dtype=str)
assess = pd.read_csv("data/raw/wayne_detroit_assessment.csv", usecols=["Parcels.pnum"], dtype=str)

print("Sales parcel IDs:")
print(sales["Parcel ID"].head(8).to_list())
print("\nAssessment parcel numbers (random sample):")
print(assess["Parcels.pnum"].sample(8, random_state=1).to_list())
print("\nRows in the Detroit assessment:", f"{len(assess):,}")

found = sales["Parcel ID"].isin(set(assess["Parcels.pnum"]))
print(f"\nSales whose parcel ID matches exactly: {found.sum():,} of {len(sales):,}")