"""
One-time setup: splits the Online Retail dataset (already used in Project 1)
into per-day raw CSV files under data/raw_daily/, simulating a source
system that exports one new batch of orders per day.

This sidesteps depending on a live third-party API for the pipeline demo —
after two free-tier hosting services expired/broke earlier in this
portfolio (see projects/09-concert-trip-planner/DEPLOY.md), a pipeline
whose "source system" is a real external API that could rate-limit, change
its schema, or go offline isn't worth the same risk for what's meant to be
a stable, always-working demo. The pipeline logic downstream (extract_load,
quality checks, dbt models) doesn't care where the daily files come from —
swapping this generator for a real API poll would be a small, contained
change if this were ever a real pipeline.

Run from this directory: python3 pipeline/generate_daily_drops.py
Output is gitignored — regenerate any time.
"""

import os

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
RAW_SOURCE = os.path.join(HERE, "..", "..", "01-retail-customer-analytics", "data", "online_retail.csv")
OUT_DIR = os.path.join(HERE, "..", "data", "raw_daily")
N_DAYS = 30

os.makedirs(OUT_DIR, exist_ok=True)

raw = pd.read_csv(RAW_SOURCE, parse_dates=["InvoiceDate"])
raw["_date"] = raw["InvoiceDate"].dt.date

# Deliberately NOT cleaned here — this is meant to be raw, as-exported
# source data (cancellations, missing CustomerIDs, bad quantities and all).
# Cleaning happens downstream, in the dbt staging model, same as any real
# ELT pattern (load raw first, transform in the warehouse).
dates = sorted(raw["_date"].unique())[:N_DAYS]

for d in dates:
    day_rows = raw[raw["_date"] == d].drop(columns=["_date"])
    day_rows.to_csv(os.path.join(OUT_DIR, f"{d}.csv"), index=False)

print(f"Wrote {len(dates)} daily files to {OUT_DIR} ({dates[0]} to {dates[-1]})")
print(f"Total rows across all days: {sum((raw['_date'] == d).sum() for d in dates):,}")
