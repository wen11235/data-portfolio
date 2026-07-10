# Retail Customer Analytics & Segmentation

**TL;DR:** 4,338 customers, £8.9M in revenue, one year of UK e-commerce transactions — segmented into 4 actionable groups using RFM + KMeans. The top 12.9% of customers ("Champions") drive **62.7%** of total revenue.

[📄 Full report](report.html) · [📓 Notebook](notebooks/analysis.ipynb)

## Problem

A retailer has a year of raw transaction logs but no way to tell which customers matter most, or which are about to churn. The goal: turn the raw log into a segmentation a marketing team could act on this week.

## Data

[UCI "Online Retail"](https://archive.ics.uci.edu/dataset/352/online+retail) — 541,909 real transactions from a UK-based online gift retailer, Dec 2010 – Dec 2011. Not committed to this repo (23MB); see `data/README.md` for the download link, or re-download via the notebook's first cell.

## Method

1. **Clean** — drop cancellations (`InvoiceNo` starting `C`), rows with no `CustomerID`, and non-positive quantity/price. 397,884 of 541,909 rows (73%) survive — the rest are cancellations/guest checkouts that can't be attributed to a customer.
2. **SQL (DuckDB)** — monthly revenue trend, top international markets, top products, run as real `SELECT`/`GROUP BY` queries against the dataframe.
3. **RFM features** — Recency (days since last order), Frequency (distinct orders), Monetary (total spend) per customer, log-transformed to tame the heavy right skew before scaling.
4. **KMeans (k=4)** — chosen via elbow + silhouette score; segments ranked and named by average Monetary/Recency.
5. **Cohort retention** — customers grouped by first-purchase month, tracked forward to see how retention decays.

## Findings

| Segment | # Customers | % of Customers | Avg Recency (days) | Avg Frequency | Avg Monetary | % of Revenue |
|---|---|---|---|---|---|---|
| **Champions** | 558 | 12.9% | 20 | 16.0 | £10,008 | **62.7%** |
| **Loyal / Steady** | 1,448 | 33.4% | 46 | 4.3 | £1,668 | 27.1% |
| **At Risk** | 1,393 | 32.1% | 59 | 1.5 | £393 | 6.1% |
| **Lost / Low-Value** | 939 | 21.6% | 260 | 1.4 | £387 | 4.1% |

- Revenue is extremely concentrated: **13% of customers generate 63% of revenue.**
- "At Risk" customers used to order about as often as "Loyal" customers early on, but haven't ordered in ~2 months — this is the highest-leverage group for a win-back campaign since they're not gone yet.
- Cohort retention drops sharply after month 1 for every cohort, then flattens for a smaller group that becomes the long-term repeat-purchase base — this group overlaps heavily with Champions/Loyal.

## Business recommendations

| Segment | Recommendation |
|---|---|
| Champions | Protect this revenue base — early access, loyalty perks, white-glove service |
| Loyal / Steady | Cross-sell/upsell campaigns to grow order value; nudge toward Champion tier |
| At Risk | Time-sensitive win-back offers before they lapse further — best ROI segment to target |
| Lost / Low-Value | Low-cost re-engagement (email) only; not worth heavy discount spend given low historical value |

## Skills demonstrated

SQL (DuckDB), data cleaning, RFM feature engineering, KMeans clustering, cohort analysis, business storytelling.
