"""
Data quality gate on the raw landing layer (raw.orders_raw), run after
extract_load.py and before the dbt transform layer.

Deliberately split into two tiers, not one flat list of checks:

  BLOCKING checks — fail the pipeline (exit 1). Reserved for things that
  mean the source file itself is structurally broken and nothing downstream
  can be trusted: a missing required column, a null in an identifier field
  that should never be null, an empty batch, data landing in the wrong day's
  file.

  WARNING checks — logged, not blocking. Reserved for real, *expected*
  messiness in this dataset that a hard-fail would incorrectly flag: guest
  checkouts have no CustomerID (~38% of rows, confirmed by inspecting the
  actual data before writing this, not assumed), cancellations/returns have
  negative Quantity, and a handful of invoices genuinely do repeat a
  (InvoiceNo, StockCode) pair. These get cleaned/filtered in the dbt staging
  model, not blocked here — the raw layer's job is to catch corruption, not
  enforce business rules.

Exit code 0 if no blocking failures (warnings can still be present);
exit code 1 if any blocking check fails.
"""

import os
import sys

import duckdb

HERE = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(HERE, "..", "warehouse.duckdb")

EXPECTED_COLUMNS = {
    "InvoiceNo": "VARCHAR",
    "StockCode": "VARCHAR",
    "Description": "VARCHAR",
    "Quantity": "BIGINT",
    "InvoiceDate": "TIMESTAMP",
    "UnitPrice": "DOUBLE",
    "CustomerID": "DOUBLE",
    "Country": "VARCHAR",
}


def check_schema(conn):
    cols = {row[0]: row[1] for row in conn.execute("DESCRIBE raw.orders_raw").fetchall()}
    missing = [c for c in EXPECTED_COLUMNS if c not in cols]
    wrong_type = [
        c for c, t in EXPECTED_COLUMNS.items() if c in cols and cols[c] != t
    ]
    if missing:
        return False, f"BLOCKING: missing expected columns: {missing}"
    if wrong_type:
        return False, f"BLOCKING: unexpected column types: {[(c, cols[c]) for c in wrong_type]}"
    return True, "schema OK — all expected columns present with expected types"


def check_no_nulls_in_identifiers(conn):
    row = conn.execute(
        """
        SELECT
            SUM(CASE WHEN InvoiceNo IS NULL THEN 1 ELSE 0 END),
            SUM(CASE WHEN StockCode IS NULL THEN 1 ELSE 0 END),
            SUM(CASE WHEN InvoiceDate IS NULL THEN 1 ELSE 0 END)
        FROM raw.orders_raw
        """
    ).fetchone()
    null_invoice, null_stock, null_date = row
    if null_invoice or null_stock or null_date:
        return False, (
            f"BLOCKING: null identifiers found — InvoiceNo={null_invoice}, "
            f"StockCode={null_stock}, InvoiceDate={null_date}"
        )
    return True, "identifier columns (InvoiceNo/StockCode/InvoiceDate) have zero nulls"


def check_batches_nonempty(conn):
    empty = conn.execute(
        "SELECT batch_date FROM raw._pipeline_state WHERE row_count = 0"
    ).fetchall()
    if empty:
        return False, f"BLOCKING: empty batch(es) loaded: {[str(r[0]) for r in empty]}"
    return True, "no empty batches"


def check_dates_land_correctly(conn):
    misfiled = conn.execute(
        "SELECT COUNT(*) FROM raw.orders_raw WHERE CAST(InvoiceDate AS DATE) != _batch_date"
    ).fetchone()[0]
    if misfiled:
        return False, f"BLOCKING: {misfiled} row(s) whose InvoiceDate doesn't match the batch file they landed in"
    return True, "every row's InvoiceDate matches the batch (day) it was loaded from"


def warn_null_customer_rate(conn):
    total, null_customer = conn.execute(
        "SELECT COUNT(*), SUM(CASE WHEN CustomerID IS NULL THEN 1 ELSE 0 END) FROM raw.orders_raw"
    ).fetchone()
    rate = null_customer / total if total else 0
    return f"WARNING (informational): {null_customer:,}/{total:,} rows ({rate:.1%}) have no CustomerID — expected (guest checkouts), filtered in dbt staging, not blocked here."


def warn_duplicate_line_items(conn):
    n = conn.execute(
        """
        SELECT COUNT(*) FROM (
            SELECT InvoiceNo, StockCode FROM raw.orders_raw
            GROUP BY 1, 2 HAVING COUNT(*) > 1
        )
        """
    ).fetchone()[0]
    return f"WARNING (informational): {n} (InvoiceNo, StockCode) pair(s) appear more than once — real, occasionally-legitimate repeat line items, not deduplicated here."


def warn_negative_quantity_rate(conn):
    total, negative = conn.execute(
        "SELECT COUNT(*), SUM(CASE WHEN Quantity < 0 THEN 1 ELSE 0 END) FROM raw.orders_raw"
    ).fetchone()
    rate = negative / total if total else 0
    return f"WARNING (informational): {negative:,}/{total:,} rows ({rate:.1%}) have negative Quantity — cancellations/returns, filtered in dbt staging, not blocked here."


def main():
    if not os.path.exists(DB_PATH):
        print(f"BLOCKING: warehouse not found at {DB_PATH} — run extract_load.py first.")
        sys.exit(1)

    conn = duckdb.connect(DB_PATH, read_only=True)

    blocking_checks = [
        check_schema,
        check_no_nulls_in_identifiers,
        check_batches_nonempty,
        check_dates_land_correctly,
    ]
    warnings = [
        warn_null_customer_rate,
        warn_duplicate_line_items,
        warn_negative_quantity_rate,
    ]

    print("=== Blocking checks ===")
    all_passed = True
    for check in blocking_checks:
        passed, message = check(conn)
        print(f"[{'PASS' if passed else 'FAIL'}] {message}")
        all_passed = all_passed and passed

    print("\n=== Warnings (informational, non-blocking) ===")
    for warn in warnings:
        print(warn(conn))

    conn.close()

    if not all_passed:
        print("\nData quality gate FAILED — see BLOCKING failures above.")
        sys.exit(1)
    print("\nData quality gate PASSED.")


if __name__ == "__main__":
    main()
