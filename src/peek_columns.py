"""
peek_columns.py
Prints the column names of our raw files. It reads only a few rows,
and reads everything as text so IDs keep their zeros and dots.
"""

import pandas as pd

FILES = {
    "Detroit sales": "data/raw/detroit_sales.csv",
    "Hamtramck assessment": "data/raw/wayne_hamtramck_assessment.csv",
    "Oakland site address": "data/raw/oakland_site_address.csv",
    "Oakland tax parcels": "data/raw/oakland_tax_parcels.csv",
}

for label, path in FILES.items():
    df = pd.read_csv(path, nrows=5, low_memory=False, dtype=str)
    print(f"\n{label}: {len(df.columns)} columns")
    print(list(df.columns))