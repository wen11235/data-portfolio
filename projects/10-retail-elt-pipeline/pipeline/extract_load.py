"""
Extract + load stage of the pipeline: picks up daily raw CSV files from
data/raw_daily/ and loads them into the `raw.orders_raw` table in a DuckDB
warehouse file, tracking what's already been loaded in a control table
(`raw._pipeline_state`) so re-running the pipeline is safe — already-loaded
batches are skipped, not duplicated. This "watermark" pattern is the same
idea a real pipeline uses against a data warehouse's load-tracking table,
just simplified to fit one DuckDB file.

Usage:
    python3 pipeline/extract_load.py            # load any new batches
    python3 pipeline/extract_load.py --reload 2010-12-01   # force-reload one batch
"""

import argparse
import glob
import os
from datetime import datetime, timezone

import duckdb

HERE = os.path.dirname(os.path.abspath(__file__))
RAW_DIR = os.path.join(HERE, "..", "data", "raw_daily")
DB_PATH = os.path.join(HERE, "..", "warehouse.duckdb")

DDL = """
CREATE SCHEMA IF NOT EXISTS raw;

CREATE TABLE IF NOT EXISTS raw.orders_raw (
    InvoiceNo   VARCHAR,
    StockCode   VARCHAR,
    Description VARCHAR,
    Quantity    BIGINT,
    InvoiceDate TIMESTAMP,
    UnitPrice   DOUBLE,
    CustomerID  DOUBLE,
    Country     VARCHAR,
    _batch_date DATE,
    _loaded_at  TIMESTAMP
);

CREATE TABLE IF NOT EXISTS raw._pipeline_state (
    batch_date DATE PRIMARY KEY,
    loaded_at  TIMESTAMP,
    row_count  BIGINT
);
"""


def already_loaded(conn, batch_date):
    row = conn.execute(
        "SELECT 1 FROM raw._pipeline_state WHERE batch_date = ?", [batch_date]
    ).fetchone()
    return row is not None


def load_batch(conn, csv_path, batch_date):
    loaded_at = datetime.now(timezone.utc)
    conn.execute(
        """
        INSERT INTO raw.orders_raw
        SELECT *, ?::DATE AS _batch_date, ?::TIMESTAMP AS _loaded_at
        FROM read_csv_auto(?, header=true)
        """,
        [batch_date, loaded_at, csv_path],
    )
    row_count = conn.execute(
        "SELECT COUNT(*) FROM raw.orders_raw WHERE _batch_date = ?", [batch_date]
    ).fetchone()[0]
    conn.execute(
        """
        INSERT INTO raw._pipeline_state (batch_date, loaded_at, row_count)
        VALUES (?, ?, ?)
        ON CONFLICT (batch_date) DO UPDATE SET loaded_at = excluded.loaded_at, row_count = excluded.row_count
        """,
        [batch_date, loaded_at, row_count],
    )
    return row_count


def unload_batch(conn, batch_date):
    conn.execute("DELETE FROM raw.orders_raw WHERE _batch_date = ?", [batch_date])
    conn.execute("DELETE FROM raw._pipeline_state WHERE batch_date = ?", [batch_date])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--reload", metavar="YYYY-MM-DD", help="force-reload a single already-loaded batch"
    )
    args = parser.parse_args()

    conn = duckdb.connect(DB_PATH)
    conn.execute(DDL)

    if args.reload:
        print(f"Force-reloading batch {args.reload}...")
        unload_batch(conn, args.reload)
        csv_path = os.path.join(RAW_DIR, f"{args.reload}.csv")
        n = load_batch(conn, csv_path, args.reload)
        print(f"Reloaded {n:,} rows for {args.reload}.")
        conn.close()
        return

    files = sorted(glob.glob(os.path.join(RAW_DIR, "*.csv")))
    if not files:
        print(f"No raw files found in {RAW_DIR} — run generate_daily_drops.py first.")
        conn.close()
        return

    loaded, skipped = 0, 0
    for path in files:
        batch_date = os.path.splitext(os.path.basename(path))[0]
        if already_loaded(conn, batch_date):
            skipped += 1
            continue
        n = load_batch(conn, path, batch_date)
        print(f"Loaded {batch_date}: {n:,} rows")
        loaded += 1

    total_rows = conn.execute("SELECT COUNT(*) FROM raw.orders_raw").fetchone()[0]
    total_batches = conn.execute("SELECT COUNT(*) FROM raw._pipeline_state").fetchone()[0]
    print(
        f"\nRun summary: {loaded} new batch(es) loaded, {skipped} already loaded (skipped). "
        f"Warehouse now has {total_batches} batches, {total_rows:,} raw rows total."
    )
    conn.close()


if __name__ == "__main__":
    main()
