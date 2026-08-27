"""
Exports two CSVs for the Tableau Public dashboard — same cleaned data, RFM
features, and KMeans segments as notebooks/analysis.ipynb (Project 1), split
into two tables at their natural grain instead of one denormalized file:

  - transactions.csv: one row per (cleaned) transaction line item.
  - customers.csv: one row per customer, with Recency/Frequency/Monetary/
    SegmentName. This is the grain the segment sizing/RFM scatter sheets
    need — computing those from a flattened transaction-level file would
    either double-count customers with many transactions or need a
    workaround calculated field. Keeping two tables and relating them in
    Tableau on CustomerID (see BUILD_GUIDE.md) lets each sheet aggregate at
    the grain it actually needs, which is also the more realistic modern-
    Tableau pattern (relationships, not one flat join) worth being able to
    talk about in an interview.

Run from this directory: python3 prepare_data.py
Output (~45MB total, gitignored) is not committed; regenerate any time by
re-running this script.
"""

import os

import duckdb
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

HERE = os.path.dirname(os.path.abspath(__file__))
RAW_PATH = os.path.join(HERE, "..", "data", "online_retail.csv")
TRANSACTIONS_OUT = os.path.join(HERE, "transactions.csv")
CUSTOMERS_OUT = os.path.join(HERE, "customers.csv")

raw = pd.read_csv(RAW_PATH, parse_dates=["InvoiceDate"])

# ---- Same cleaning as notebooks/analysis.py ----
df = raw.copy()
df = df[~df["InvoiceNo"].astype(str).str.startswith("C")]  # drop cancellations
df = df.dropna(subset=["CustomerID"])
df["CustomerID"] = df["CustomerID"].astype(int)
df = df[(df["Quantity"] > 0) & (df["UnitPrice"] > 0)]  # drop bad rows
df["TotalPrice"] = df["Quantity"] * df["UnitPrice"]

print(f"Cleaned shape: {df.shape}")

# ---- Same RFM + KMeans as notebooks/analysis.py ----
snapshot_date = df["InvoiceDate"].max() + pd.Timedelta(days=1)
rfm = (
    duckdb.query(
        f"""
        SELECT
            CustomerID,
            date_diff('day', MAX(InvoiceDate), TIMESTAMP '{snapshot_date}') AS Recency,
            COUNT(DISTINCT InvoiceNo) AS Frequency,
            ROUND(SUM(TotalPrice), 2) AS Monetary
        FROM df
        GROUP BY CustomerID
        """
    )
    .df()
    .set_index("CustomerID")
)

rfm_log = rfm.copy()
rfm_log["Frequency"] = np.log1p(rfm_log["Frequency"])
rfm_log["Monetary"] = np.log1p(rfm_log["Monetary"])
rfm_scaled = StandardScaler().fit_transform(rfm_log[["Recency", "Frequency", "Monetary"]])

K = 4
kmeans = KMeans(n_clusters=K, random_state=42, n_init=10)
rfm["Segment"] = kmeans.fit_predict(rfm_scaled)

segment_profile = rfm.groupby("Segment")[["Recency", "Frequency", "Monetary"]].mean()
ranked = segment_profile.sort_values(["Monetary", "Recency"], ascending=[False, True]).index.tolist()
segment_names = {
    ranked[0]: "Champions",
    ranked[1]: "Loyal / Steady",
    ranked[2]: "At Risk",
    ranked[3]: "Lost / Low-Value",
}
rfm["SegmentName"] = rfm["Segment"].map(segment_names)

# ---- Export: transactions (no RFM columns — those belong to customers.csv) ----
transactions = df[
    ["InvoiceNo", "StockCode", "Description", "Quantity", "InvoiceDate", "UnitPrice", "CustomerID", "Country", "TotalPrice"]
]
transactions.to_csv(TRANSACTIONS_OUT, index=False)

# ---- Export: customers (one row per customer) ----
customers = rfm.reset_index()[["CustomerID", "Recency", "Frequency", "Monetary", "SegmentName"]]
customers.to_csv(CUSTOMERS_OUT, index=False)

for path in (TRANSACTIONS_OUT, CUSTOMERS_OUT):
    print(f"Exported {path} — {os.path.getsize(path) / 1e6:.1f} MB")
print(f"transactions: {len(transactions):,} rows | customers: {len(customers):,} rows")
print(customers["SegmentName"].value_counts())
