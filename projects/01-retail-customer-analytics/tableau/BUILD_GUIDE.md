# Building the Tableau Public dashboard

This is the part I can't do for you — Tableau Public Desktop is a native
GUI app, not something scriptable from here. Everything below is exact
enough that you shouldn't have to improvise; budget ~45–60 minutes for a
first pass.

## 0. Setup

1. Generate the data files (if you haven't already):
   ```bash
   cd projects/01-retail-customer-analytics/tableau
   python3 prepare_data.py
   ```
   This writes `transactions.csv` (~38MB, one row per transaction line) and
   `customers.csv` (~0.1MB, one row per customer with Recency/Frequency/
   Monetary/SegmentName). Both gitignored — not committed, regenerate any
   time by re-running the script.
2. Download **Tableau Public Desktop** (free): https://public.tableau.com/en-us/s/download
3. Create a free Tableau Public account (this is where the finished
   dashboard gets hosted/shared from — you'll publish to it in step 7).

## 1. Connect both files and relate them

- Open Tableau Public Desktop → **Connect → Text File** → select
  `transactions.csv`.
- On the Data Source canvas, **Connect → Text File** again → select
  `customers.csv`. Drag it onto the canvas next to `transactions`.
- Tableau will detect the shared `CustomerID` field and offer a
  **Relationship** (the noodle/line connecting the two tables) — confirm
  it's on `CustomerID = CustomerID`. This is the modern Tableau data model
  (relationships, not a flat join): each sheet below pulls fields from
  whichever table it needs, aggregated at that table's own grain, without
  a customer's repeated transaction rows inflating a customer-level metric
  like Monetary. Worth being able to explain this choice in an interview —
  it's the actual reason the data is two files instead of one.

## 2. Fix field types (Tableau usually gets this right, but check)

- `InvoiceDate` (transactions) → **Date**
- `TotalPrice`, `UnitPrice`, `Recency`, `Frequency`, `Monetary` → **Number (decimal)**
- `Quantity` → **Number (whole)**
- `Country` (transactions) → should auto-detect a **Geographic Role**
  (globe icon next to the field name). If not: right-click **Country** →
  **Geographic Role → Country/Region**.

## 3. Sheet 1 — Monthly Revenue Trend (line chart)

New Worksheet →
- Drag **InvoiceDate** to **Columns**. Click the `+` on the pill until it
  reads **Month** at a **continuous** (green pill) granularity — continuous,
  not discrete, so it draws as one trend line instead of separate bars per
  month-number.
- Drag **TotalPrice** to **Rows** (auto-sums → `SUM(TotalPrice)`).
- Show Me panel (top right) → confirm **line chart**.
- Rename: `Monthly Revenue`.

## 4. Sheet 2 — Revenue by Country (filled map)

New Worksheet →
- Double-click **Country** in the Data pane — Tableau auto-builds a map.
- Drag **TotalPrice** onto **Color** on the Marks card.
- Marks type dropdown → **Filled Map**.
- Optional: right-click the color legend → **Edit Colors** → a sequential
  single-hue palette reads better than the rainbow default for "revenue
  intensity."
- Rename: `Revenue by Country`.

## 5. Sheet 3 — Top 10 Products (bar chart)

New Worksheet →
- Drag **Description** to **Rows**, **TotalPrice** to **Columns**.
- Sort descending (toolbar sort icon, or right-click the Description axis
  → Sort → Descending by TotalPrice).
- Filter to top 10: right-click the **Description** pill on Rows →
  **Filter... → Top tab → By field → Top 10 → by SUM(TotalPrice)**.
- Rename: `Top Products`.

## 6. Sheet 4 — Customer Segments (treemap)

New Worksheet →
- Drag **SegmentName** (from `customers`) to **Color** on the Marks card.
- Drag **Monetary** (from `customers`) to **Size**. Because this comes from
  the customer-grain table via the relationship, `SUM(Monetary)` here
  correctly totals each customer's spend exactly once per segment — no
  double-counting, no calculated-field workaround needed.
- Show Me panel → **Treemap**.
- Rename: `Segments`.

## 7. Sheet 5 — RFM Scatter (Recency vs Monetary, sized by Frequency)

New Worksheet →
- Drag **Recency** to **Columns**, **Monetary** to **Rows**.
- Drag **SegmentName** to **Color**, **Frequency** to **Size**.
- Drag **CustomerID** to **Detail** (so each mark is one customer, not an
  aggregate).
- Right-click the Monetary axis → **Log Scale** (Monetary is heavily
  right-skewed — same reason the Python version log-transforms it before
  clustering; log scale here just makes the chart readable, doesn't change
  the underlying data).
- Rename: `RFM Scatter`.

## 8. Dashboard — combine + cross-filter

**New Dashboard** (bottom tab bar, not New Worksheet) →
- Drag all 5 sheets onto the canvas — a 2×3 or similar grid, with
  `Segments` positioned prominently since it drives the cross-filter.
- Click the **Segments** treemap → toolbar funnel icon → **Use as
  Filter**. Clicking a segment now filters every other chart to that
  segment — genuine cross-filtering, which the Plotly version of this same
  data ([Project 5](../../05-retail-dashboard/)) explicitly can't do
  without a backend. That's the actual reason to add a Tableau version,
  not just "because job postings ask for it" — worth leading with in the
  write-up.
- Dashboard title: `Retail Customer Analytics — Tableau`.

## 9. Publish

**Server → Tableau Public → Save to Tableau Public...** (top menu). Sign
in with the account from step 0. Once it uploads, Tableau gives you a
permanent public URL like `https://public.tableau.com/views/.../Dashboard1`.

## Once it's live

Send me that URL and I'll:
- Add a "Tableau" section to this project's `report.html` and `README.md`
  (embedded or linked, your call).
- Add a `Tableau` tag to the homepage card.
- Update the skills-demonstrated list.
