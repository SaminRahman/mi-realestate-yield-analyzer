"""
prepare_oakland.py
Combine Oakland's site-address points (location) with its tax-parcel table
(values, class, size). We never load owner names (NAME1, NAME2) or the
mailing address (POSTALADDRESS).
"""

import numpy as np
import pandas as pd

SITE = "data/raw/oakland_site_address.csv"
PARCELS = "data/raw/oakland_tax_parcels.csv"
OUT = "data/processed/oakland_residential.csv"
KEEP_CLASSES = ["401"]  # residential with a building; confirmed below by the counts

# 1) Locations. X and Y are in meters (Web Mercator), not degrees, so convert them.
site = pd.read_csv(SITE, usecols=["X", "Y", "TYPE", "PIN"], dtype=str)
site = site[site["TYPE"] == "Primary Property Address"].copy()
site = site.drop_duplicates(subset="PIN")

EARTH_RADIUS = 6378137.0  # meters, used by Web Mercator
site["lon"] = pd.to_numeric(site["X"]) / EARTH_RADIUS * 180 / np.pi
site["lat"] = np.degrees(2 * np.arctan(np.exp(pd.to_numeric(site["Y"]) / EARTH_RADIUS)) - np.pi / 2)
print("Site points:", f"{len(site):,}")
print("Latitude range:", round(site["lat"].min(), 2), "to", round(site["lat"].max(), 2),
      "| Longitude range:", round(site["lon"].min(), 2), "to", round(site["lon"].max(), 2))
print("PIN lengths in site file:", site["PIN"].str.len().value_counts().to_dict())

# 2) Parcel details
parcels = pd.read_csv(
    PARCELS,
    usecols=["PIN", "CLASSCODE", "CVTTAXDESCRIPTION", "ASSESSEDVALUE", "TAXABLEVALUE",
             "NUM_BEDS", "NUM_BATHS", "STRUCTURE_DESC", "LIVING_AREA_SQFT",
             "SITEADDRESS", "SITECITY", "SITEZIP5"],
    dtype=str,
)
print("\nPIN lengths in parcel file:", parcels["PIN"].str.len().value_counts().to_dict())
print("\nParcel class codes (10 most common):")
print(parcels["CLASSCODE"].value_counts().head(10).to_string())

res = parcels[parcels["CLASSCODE"].isin(KEEP_CLASSES)].copy()
for col in ["ASSESSEDVALUE", "TAXABLEVALUE", "NUM_BEDS", "NUM_BATHS", "LIVING_AREA_SQFT"]:
    res[col] = pd.to_numeric(res[col], errors="coerce")

# 3) Join: residential parcels get their map point
res = res.merge(site[["PIN", "lat", "lon"]], on="PIN", how="left")
print(f"\nResidential parcels: {len(res):,}")
print(f"... with a map point: {res['lat'].notna().sum():,}")
print("\nAssessed value (median):", res["ASSESSEDVALUE"].median())
print("Taxable value (median): ", res["TAXABLEVALUE"].median())
print("Median taxable / assessed:", round((res["TAXABLEVALUE"] / res["ASSESSEDVALUE"]).median(), 2))
print("\nShare with real details:")
for col in ["NUM_BEDS", "NUM_BATHS", "LIVING_AREA_SQFT"]:
    print(f"  {col:17s} {(res[col] > 0).mean():.0%}")

res = res.rename(columns={
    "PIN": "pin", "CLASSCODE": "class_code", "CVTTAXDESCRIPTION": "tax_district",
    "ASSESSEDVALUE": "sev", "TAXABLEVALUE": "taxable_value", "NUM_BEDS": "bedrooms",
    "NUM_BATHS": "baths", "STRUCTURE_DESC": "structure", "LIVING_AREA_SQFT": "sqft",
    "SITEADDRESS": "address", "SITECITY": "city", "SITEZIP5": "zip",
})
res.to_csv(OUT, index=False)
print(f"\nSaved {len(res):,} rows to {OUT}")