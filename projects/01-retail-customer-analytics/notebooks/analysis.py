# %% [markdown]
# # Retail Customer Analytics & Segmentation
#
# **Goal:** Turn a year of raw UK e-commerce transactions into concrete, actionable
# customer segments — the kind of analysis a growth/marketing team could act on directly.
#
# **Dataset:** [UCI "Online Retail"](https://archive.ics.uci.edu/dataset/352/online+retail) —
# 541,909 transactions from a UK-based online gift retailer, Dec 2010 – Dec 2011.
#
# **Approach:**
# 1. Clean the raw transaction log (cancellations, missing customer IDs, bad quantities/prices)
# 2. Answer core business questions with SQL (via DuckDB, run directly on the dataframe)
# 3. Engineer RFM (Recency, Frequency, Monetary) features per customer
# 4. Segment customers with KMeans clustering and profile each segment
# 5. Measure cohort retention over time
# 6. Translate findings into business recommendations

# %%
import pandas as pd
import numpy as np
import duckdb
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

sns.set_theme(style="whitegrid", palette="deep")
plt.rcParams["figure.dpi"] = 110
CHART_DIR = "../assets"
import os
os.makedirs(CHART_DIR, exist_ok=True)

# %% [markdown]
# ## 1. Load & clean data

# %%
raw = pd.read_csv("../data/online_retail.csv", parse_dates=["InvoiceDate"])
print(f"Raw shape: {raw.shape}")
raw.head()

# %%
df = raw.copy()

# Cancellations are invoices starting with 'C' — exclude them (they're refunds, not sales)
df = df[~df["InvoiceNo"].astype(str).str.startswith("C")]

# Drop rows with no CustomerID — can't attribute revenue to a customer for segmentation
df = df.dropna(subset=["CustomerID"])
df["CustomerID"] = df["CustomerID"].astype(int)

# Drop non-positive quantity/price (data entry errors / test rows)
df = df[(df["Quantity"] > 0) & (df["UnitPrice"] > 0)]

df["TotalPrice"] = df["Quantity"] * df["UnitPrice"]

print(f"Cleaned shape: {df.shape}  ({df.shape[0] / raw.shape[0]:.1%} of raw rows kept)")
print(f"Date range: {df['InvoiceDate'].min().date()} to {df['InvoiceDate'].max().date()}")
print(f"Customers: {df['CustomerID'].nunique():,} | Countries: {df['Country'].nunique()} | Total revenue: £{df['TotalPrice'].sum():,.0f}")

# %% [markdown]
# ## 2. Business questions via SQL (DuckDB)
#
# Running SQL directly against the cleaned dataframe — same queries you'd write against
# a transactions table in a warehouse.

# %%
monthly_revenue = duckdb.query("""
    SELECT
        strftime(InvoiceDate, '%Y-%m') AS month,
        ROUND(SUM(TotalPrice), 2) AS revenue,
        COUNT(DISTINCT InvoiceNo) AS orders,
        COUNT(DISTINCT CustomerID) AS customers
    FROM df
    GROUP BY 1
    ORDER BY 1
""").df()
monthly_revenue

# %%
top_countries = duckdb.query("""
    SELECT Country, ROUND(SUM(TotalPrice), 2) AS revenue, COUNT(DISTINCT CustomerID) AS customers
    FROM df
    WHERE Country != 'United Kingdom'
    GROUP BY Country
    ORDER BY revenue DESC
    LIMIT 10
""").df()
top_countries

# %%
top_products = duckdb.query("""
    SELECT Description, ROUND(SUM(TotalPrice), 2) AS revenue, SUM(Quantity) AS units_sold
    FROM df
    GROUP BY Description
    ORDER BY revenue DESC
    LIMIT 10
""").df()
top_products

# %% [markdown]
# ### Monthly revenue trend

# %%
fig, ax = plt.subplots(figsize=(10, 4.5))
ax.plot(monthly_revenue["month"], monthly_revenue["revenue"], marker="o", linewidth=2)
ax.set_title("Monthly Revenue (Dec 2010 – Dec 2011)", fontsize=13, fontweight="bold")
ax.set_ylabel("Revenue (£)")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"£{x/1000:.0f}k"))
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
plt.savefig(f"{CHART_DIR}/monthly_revenue.png", dpi=150)
plt.show()

# %% [markdown]
# Note the sharp Dec-2011 drop — the dataset simply ends mid-month, not a real decline.
#
# ### Revenue outside the UK (top 10 markets)

# %%
fig, ax = plt.subplots(figsize=(9, 5))
sns.barplot(data=top_countries, y="Country", x="revenue", hue="Country", legend=False, ax=ax)
ax.set_title("Top 10 International Markets by Revenue", fontsize=13, fontweight="bold")
ax.set_xlabel("Revenue (£)")
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"£{x/1000:.0f}k"))
plt.tight_layout()
plt.savefig(f"{CHART_DIR}/top_countries.png", dpi=150)
plt.show()

# %% [markdown]
# ## 3. RFM feature engineering
#
# For every customer: **Recency** (days since last purchase), **Frequency** (number of
# distinct orders), **Monetary** (total spend). These three numbers compress a customer's
# entire purchase history into a segmentable profile.

# %%
snapshot_date = df["InvoiceDate"].max() + pd.Timedelta(days=1)

rfm = duckdb.query(f"""
    SELECT
        CustomerID,
        date_diff('day', MAX(InvoiceDate), TIMESTAMP '{snapshot_date}') AS Recency,
        COUNT(DISTINCT InvoiceNo) AS Frequency,
        ROUND(SUM(TotalPrice), 2) AS Monetary
    FROM df
    GROUP BY CustomerID
""").df().set_index("CustomerID")

rfm.describe()

# %%
fig, axes = plt.subplots(1, 3, figsize=(13, 3.5))
for ax, col in zip(axes, ["Recency", "Frequency", "Monetary"]):
    sns.histplot(rfm[col], bins=40, ax=ax, log_scale=(False, True) if col != "Recency" else False)
    ax.set_title(col)
plt.suptitle("RFM Distributions (log-scaled y-axis for skewed metrics)", y=1.05)
plt.tight_layout()
plt.savefig(f"{CHART_DIR}/rfm_distributions.png", dpi=150)
plt.show()

# %% [markdown]
# ## 4. Customer segmentation (KMeans)
#
# RFM values are heavily right-skewed, so we log-transform before scaling — otherwise a
# handful of huge spenders would dominate the distance metric KMeans uses.

# %%
rfm_log = rfm.copy()
rfm_log["Frequency"] = np.log1p(rfm_log["Frequency"])
rfm_log["Monetary"] = np.log1p(rfm_log["Monetary"])
# Recency: smaller = more recent = better, keep as-is (already fairly well behaved)

scaler = StandardScaler()
rfm_scaled = scaler.fit_transform(rfm_log[["Recency", "Frequency", "Monetary"]])

# %%
inertias, sil_scores = [], []
k_range = range(2, 9)
for k in k_range:
    km = KMeans(n_clusters=k, random_state=42, n_init=10)
    labels = km.fit_predict(rfm_scaled)
    inertias.append(km.inertia_)
    sil_scores.append(silhouette_score(rfm_scaled, labels))

fig, axes = plt.subplots(1, 2, figsize=(11, 4))
axes[0].plot(list(k_range), inertias, marker="o")
axes[0].set_title("Elbow Method")
axes[0].set_xlabel("k")
axes[0].set_ylabel("Inertia")
axes[1].plot(list(k_range), sil_scores, marker="o", color="darkorange")
axes[1].set_title("Silhouette Score")
axes[1].set_xlabel("k")
plt.tight_layout()
plt.savefig(f"{CHART_DIR}/kmeans_selection.png", dpi=150)
plt.show()
print(f"Best silhouette score at k={list(k_range)[int(np.argmax(sil_scores))]}")

# %%
K = 4  # chosen for interpretability + strong silhouette score (see chart above)
kmeans = KMeans(n_clusters=K, random_state=42, n_init=10)
rfm["Segment"] = kmeans.fit_predict(rfm_scaled)

segment_profile = rfm.groupby("Segment")[["Recency", "Frequency", "Monetary"]].mean().round(1)
segment_profile["CustomerCount"] = rfm.groupby("Segment").size()
segment_profile = segment_profile.sort_values("Monetary", ascending=False)
segment_profile

# %% [markdown]
# ### Naming the segments
#
# Ranking clusters by average Monetary value and Recency gives us business-readable names:

# %%
# Rank clusters: highest monetary + lowest recency = best customers
ranked = segment_profile.sort_values(["Monetary", "Recency"], ascending=[False, True]).index.tolist()
segment_names = {
    ranked[0]: "Champions",
    ranked[1]: "Loyal / Steady",
    ranked[2]: "At Risk",
    ranked[3]: "Lost / Low-Value",
}
rfm["SegmentName"] = rfm["Segment"].map(segment_names)
segment_profile["SegmentName"] = segment_profile.index.map(segment_names)
segment_profile

# %%
fig, axes = plt.subplots(1, 2, figsize=(12, 5))

order = segment_profile.sort_values("CustomerCount", ascending=False)["SegmentName"]
sns.scatterplot(
    data=rfm, x="Frequency", y="Monetary", hue="SegmentName", hue_order=order,
    alpha=0.5, s=25, ax=axes[0], palette="deep",
)
axes[0].set_yscale("log")
axes[0].set_xscale("log")
axes[0].set_title("Customer Segments: Frequency vs Monetary")

counts = rfm["SegmentName"].value_counts()
axes[1].pie(counts, labels=counts.index, autopct="%1.0f%%", startangle=90,
            colors=sns.color_palette("deep", len(counts)))
axes[1].set_title("Segment Size (% of customers)")

plt.tight_layout()
plt.savefig(f"{CHART_DIR}/segments.png", dpi=150)
plt.show()

# %% [markdown]
# ## 5. Cohort retention
#
# Group customers by the month of their *first* purchase, then track what fraction of
# each cohort is still buying in each subsequent month.

# %%
df["OrderMonth"] = df["InvoiceDate"].dt.to_period("M")
df["CohortMonth"] = df.groupby("CustomerID")["InvoiceDate"].transform("min").dt.to_period("M")
df["CohortIndex"] = (df["OrderMonth"] - df["CohortMonth"]).apply(lambda x: x.n)

cohort_data = df.groupby(["CohortMonth", "CohortIndex"])["CustomerID"].nunique().reset_index()
cohort_pivot = cohort_data.pivot(index="CohortMonth", columns="CohortIndex", values="CustomerID")
cohort_size = cohort_pivot.iloc[:, 0]
retention = cohort_pivot.divide(cohort_size, axis=0).round(3)

fig, ax = plt.subplots(figsize=(12, 7))
sns.heatmap(retention, annot=True, fmt=".0%", cmap="YlGnBu", vmin=0, vmax=0.5, ax=ax,
            cbar_kws={"label": "% of cohort still active"})
ax.set_title("Monthly Cohort Retention", fontsize=13, fontweight="bold")
ax.set_xlabel("Months Since First Purchase")
ax.set_ylabel("Cohort (first purchase month)")
plt.tight_layout()
plt.savefig(f"{CHART_DIR}/cohort_retention.png", dpi=150)
plt.show()

# %% [markdown]
# Retention drops off hard after month 1 for most cohorts, then a subset of customers
# settles into a steady repeat-purchase pattern — that steady group overlaps heavily
# with the "Champions" / "Loyal" segments identified above.

# %% [markdown]
# ## 6. Business recommendations
#
# | Segment | Profile | Recommendation |
# |---|---|---|
# | **Champions** | Recent, frequent, high spend | Reward with early access / loyalty perks — protect this revenue base, they're the most valuable and easiest to retain |
# | **Loyal / Steady** | Regular purchasers, moderate spend | Upsell/cross-sell campaigns to grow order value; nudge toward Champion tier |
# | **At Risk** | Used to buy often, haven't purchased recently | Time-sensitive win-back offers before they churn fully — highest-leverage segment to act on |
# | **Lost / Low-Value** | Long recency, low frequency/spend | Low-cost re-engagement (email) only; not worth heavy discounting given low historical value |
#
# **Key numbers:**

# %%
summary = segment_profile[["SegmentName", "CustomerCount", "Recency", "Frequency", "Monetary"]]
summary["RevenueShare"] = (rfm.groupby("SegmentName")["Monetary"].sum() / rfm["Monetary"].sum()).reindex(summary["SegmentName"]).round(3).values
summary
