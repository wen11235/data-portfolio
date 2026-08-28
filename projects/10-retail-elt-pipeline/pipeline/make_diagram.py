"""Generates assets/architecture.png — a plain matplotlib box-and-arrow
diagram of the pipeline, kept as a script (like every chart elsewhere in
this portfolio) rather than hand-drawn, so it's reproducible."""

import os

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyArrowPatch

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_PATH = os.path.join(HERE, "..", "assets", "architecture.png")

BLUE, AQUA, VIOLET, ORANGE, GREY = "#2a78d6", "#1baf7a", "#7a5cd6", "#eb6834", "#5a5f6e"

fig, ax = plt.subplots(figsize=(11.5, 5.5))
ax.set_xlim(0, 11)
ax.set_ylim(0, 5.5)
ax.axis("off")


def box(x, y, w, h, text, color, fontsize=9.5):
    rect = mpatches.FancyBboxPatch(
        (x, y), w, h, boxstyle="round,pad=0.06,rounding_size=0.08",
        linewidth=1.6, edgecolor=color, facecolor=color + "22"
    )
    ax.add_patch(rect)
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fontsize,
             color="#1a1a1a", weight="bold")
    return (x, y, w, h)


def arrow_right(b1, b2, label=None, color=GREY):
    x1, y1 = b1[0] + b1[2], b1[1] + b1[3] / 2
    x2, y2 = b2[0], b2[1] + b2[3] / 2
    a = FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=14,
                         linewidth=1.6, color=color)
    ax.add_patch(a)
    if label:
        ax.text((x1 + x2) / 2, y1 + 0.28, label, ha="center", fontsize=8, color=color, style="italic")


def arrow_left(b1, b2, label=None, color=GREY):
    x1, y1 = b1[0], b1[1] + b1[3] / 2
    x2, y2 = b2[0] + b2[2], b2[1] + b2[3] / 2
    a = FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=14,
                         linewidth=1.6, color=color)
    ax.add_patch(a)
    if label:
        ax.text((x1 + x2) / 2, y1 + 0.28, label, ha="center", fontsize=8, color=color, style="italic")


def arrow_down(b1, b2, label=None, color=GREY):
    x1, y1 = b1[0] + b1[2] / 2, b1[1]
    x2, y2 = b2[0] + b2[2] / 2, b2[1] + b2[3]
    a = FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=14,
                         linewidth=1.6, color=color)
    ax.add_patch(a)
    if label:
        ax.text(x1 + 0.55, (y1 + y2) / 2, label, ha="left", fontsize=8, color=color, style="italic")


# Row 1 (top, left -> right): source -> extract/load -> raw -> quality gate
b_source = box(0.2, 3.6, 1.9, 1.3, "data/raw_daily/\n*.csv\n(30 daily drops)", GREY)
b_extract = box(2.7, 3.6, 2.0, 1.3, "extract_load.py\n(idempotent —\nwatermark table)", BLUE)
b_raw = box(5.3, 3.6, 1.7, 1.3, "raw.orders_raw\n(DuckDB)", BLUE)
b_quality = box(7.6, 3.6, 2.2, 1.3, "quality_checks.py\n(blocking +\nwarning checks)", ORANGE)

arrow_right(b_source, b_extract)
arrow_right(b_extract, b_raw)
arrow_right(b_raw, b_quality)

# Row 2 (bottom, right -> left, directly under quality gate): stg_orders <- marts
b_stg = box(7.6, 1.4, 2.2, 1.3, "dbt: stg_orders\n(clean, filter)", AQUA)
b_marts = box(0.2, 1.4, 6.7, 1.3, "dbt: marts\ndim_customers · dim_products · dim_date\nfct_orders · customer_rfm  (22 dbt tests)", VIOLET)

arrow_down(b_quality, b_stg, label="PASS")
arrow_left(b_stg, b_marts)

# Orchestration label spanning the whole thing
ax.add_patch(mpatches.FancyBboxPatch(
    (0.2, 0.1), 9.6, 0.85, boxstyle="round,pad=0.05,rounding_size=0.08",
    linewidth=1.2, edgecolor=GREY, facecolor="#00000000", linestyle="--"
))
ax.text(5.0, 0.53, "orchestrated by GitHub Actions — scheduled (daily cron) + on-demand (workflow_dispatch)",
        ha="center", va="center", fontsize=9, color=GREY, style="italic")

plt.title("Retail ELT Pipeline — Architecture", fontsize=13, fontweight="bold", pad=14)
plt.tight_layout()
plt.savefig(OUT_PATH, dpi=150, bbox_inches="tight")
print(f"Saved {OUT_PATH}")
