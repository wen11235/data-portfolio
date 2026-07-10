# %% [markdown]
# # Retail Sales Interactive Dashboard — Build Script
#
# Takes the same cleaned Online Retail data as
# [Project 1](../../01-retail-customer-analytics/) and packages it as a
# self-serve, click-and-filter dashboard instead of a static report — the
# same analysis, built for a different audience (a stakeholder who wants to
# explore the data themselves, not read a write-up).
#
# Output is plain HTML + Plotly.js (loaded from CDN) — fully static, no
# server required, so it runs directly on GitHub Pages. Filters (country
# dropdown, metric toggle) are handled client-side via Plotly `updatemenus`;
# there's no cross-filtering server backend (that would need Dash/Streamlit
# with a live Python process, which GitHub Pages can't host) — see the
# project README for that scope trade-off.

# %%
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.io as pio
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

pio.templates.default = "plotly_white"

# Validated categorical palette (see dataviz skill), fixed order
BLUE, AQUA, YELLOW, GREEN, VIOLET, RED, MAGENTA, ORANGE = (
    "#2a78d6", "#1baf7a", "#eda100", "#008300", "#4a3aa7", "#e34948", "#e87ba4", "#eb6834"
)
SERIES_COLORS = [BLUE, AQUA, ORANGE, VIOLET, RED, GREEN, MAGENTA, YELLOW]

# %% [markdown]
# ## 1. Load & clean (same steps as Project 1)

# %%
raw = pd.read_csv("../../01-retail-customer-analytics/data/online_retail.csv", parse_dates=["InvoiceDate"])
df = raw.copy()
df = df[~df["InvoiceNo"].astype(str).str.startswith("C")]
df = df.dropna(subset=["CustomerID"])
df["CustomerID"] = df["CustomerID"].astype(int)
df = df[(df["Quantity"] > 0) & (df["UnitPrice"] > 0)]
df["TotalPrice"] = df["Quantity"] * df["UnitPrice"]
df["Month"] = df["InvoiceDate"].dt.to_period("M").dt.to_timestamp()
print(f"{df.shape[0]:,} clean rows, {df['CustomerID'].nunique():,} customers, {df['Country'].nunique()} countries")

# %% [markdown]
# ## 2. Chart 1 — Revenue trend with a country filter
#
# Precompute monthly revenue for "All countries" plus the top 8 countries by
# revenue, then use a Plotly dropdown to toggle which trace is visible —
# entirely client-side, no server needed.

# %%
top_countries = df.groupby("Country")["TotalPrice"].sum().sort_values(ascending=False).head(8).index.tolist()
options = ["All countries"] + top_countries

monthly_all = df.groupby("Month")["TotalPrice"].sum().sort_index()

fig_trend = go.Figure()
for i, opt in enumerate(options):
    series = monthly_all if opt == "All countries" else df[df["Country"] == opt].groupby("Month")["TotalPrice"].sum().reindex(monthly_all.index, fill_value=0)
    fig_trend.add_trace(go.Scatter(
        x=series.index, y=series.values, mode="lines+markers",
        name=opt, visible=(i == 0),
        line=dict(color=BLUE, width=2.5),
        hovertemplate="%{x|%b %Y}<br>£%{y:,.0f}<extra></extra>",
    ))

buttons = [
    dict(label=opt, method="update",
         args=[{"visible": [j == i for j in range(len(options))]},
               {"title": f"Monthly Revenue — {opt}"}])
    for i, opt in enumerate(options)
]
fig_trend.update_layout(
    updatemenus=[dict(buttons=buttons, direction="down", x=1.0, xanchor="right", y=1.18, yanchor="top")],
    title="Monthly Revenue — All countries",
    xaxis=dict(rangeslider=dict(visible=True), title=None),
    yaxis=dict(title="Revenue (£)", tickprefix="£"),
    height=460, margin=dict(t=90, l=60, r=30, b=40),
    hovermode="x unified",
)

# %% [markdown]
# ## 3. Chart 2 — Revenue by country (choropleth)

# %%
ISO3 = {
    "United Kingdom": "GBR", "Germany": "DEU", "France": "FRA", "EIRE": "IRL",
    "Spain": "ESP", "Netherlands": "NLD", "Belgium": "BEL", "Switzerland": "CHE",
    "Portugal": "PRT", "Australia": "AUS", "Norway": "NOR", "Italy": "ITA",
    "Finland": "FIN", "Channel Islands": "GBR", "Denmark": "DNK", "Cyprus": "CYP",
    "Sweden": "SWE", "Austria": "AUT", "Japan": "JPN", "Poland": "POL",
    "Israel": "ISR", "Singapore": "SGP", "Iceland": "ISL", "USA": "USA",
    "Canada": "CAN", "Greece": "GRC", "Malta": "MLT", "United Arab Emirates": "ARE",
    "European Community": None, "RSA": "ZAF", "Lebanon": "LBN", "Lithuania": "LTU",
    "Brazil": "BRA", "Czech Republic": "CZE", "Bahrain": "BHR", "Saudi Arabia": "SAU",
    "Hong Kong": "HKG", "Unspecified": None,
}
country_rev = df.groupby("Country")["TotalPrice"].sum().reset_index()
country_rev["iso3"] = country_rev["Country"].map(ISO3)
country_rev = country_rev.dropna(subset=["iso3"])
# UK is ~82% of revenue — a linear color scale would wash out every other
# country, so color by log10(revenue) while showing the real £ value on hover
country_rev["log_rev"] = np.log10(country_rev["TotalPrice"])

fig_map = go.Figure(go.Choropleth(
    locations=country_rev["iso3"], z=country_rev["log_rev"], text=country_rev["Country"],
    customdata=country_rev["TotalPrice"],
    colorscale=[[0, "#cde2fb"], [0.5, "#5598e7"], [1, "#0d366b"]],
    marker_line_color="white", marker_line_width=0.5,
    colorbar=dict(title="Revenue (£, log scale)", tickvals=[3, 4, 5, 6, 7], ticktext=["£1k", "£10k", "£100k", "£1M", "£10M"]),
    hovertemplate="%{text}<br>£%{customdata:,.0f}<extra></extra>",
))
fig_map.update_geos(fitbounds="locations", visible=False)
fig_map.update_layout(
    title="Revenue by Country (log-scaled color)",
    geo=dict(showframe=False, showcoastlines=False, projection_type="natural earth"),
    height=460, margin=dict(t=60, l=10, r=10, b=10),
)

# %% [markdown]
# ## 4. Chart 3 — Top products, with a metric toggle

# %%
top_products = (
    df.groupby("Description")
    .agg(Revenue=("TotalPrice", "sum"), Units=("Quantity", "sum"))
    .sort_values("Revenue", ascending=False)
    .head(15)
)
top_products_by_units = df.groupby("Description")["Quantity"].sum().sort_values(ascending=False).head(15)

fig_products = go.Figure()
fig_products.add_trace(go.Bar(
    y=top_products.index[::-1], x=top_products["Revenue"][::-1], orientation="h",
    marker_color=AQUA, name="Revenue", visible=True,
    hovertemplate="%{y}<br>£%{x:,.0f}<extra></extra>",
))
fig_products.add_trace(go.Bar(
    y=top_products_by_units.index[::-1], x=top_products_by_units.values[::-1], orientation="h",
    marker_color=ORANGE, name="Units Sold", visible=False,
    hovertemplate="%{y}<br>%{x:,.0f} units<extra></extra>",
))
fig_products.update_layout(
    updatemenus=[dict(
        buttons=[
            dict(label="By Revenue", method="update", args=[{"visible": [True, False]}, {"title": "Top 15 Products by Revenue", "xaxis": {"tickprefix": "£"}}]),
            dict(label="By Units Sold", method="update", args=[{"visible": [False, True]}, {"title": "Top 15 Products by Units Sold", "xaxis": {"tickprefix": ""}}]),
        ],
        direction="down", x=1.0, xanchor="right", y=1.12, yanchor="top",
    )],
    title="Top 15 Products by Revenue", showlegend=False,
    xaxis=dict(tickprefix="£"),
    height=520, margin=dict(t=80, l=280, r=30, b=40),
)

# %% [markdown]
# ## 5. Chart 4 — Customer segments (same RFM/KMeans as Project 1)

# %%
snapshot_date = df["InvoiceDate"].max() + pd.Timedelta(days=1)
rfm = df.groupby("CustomerID").agg(
    Recency=("InvoiceDate", lambda s: (snapshot_date - s.max()).days),
    Frequency=("InvoiceNo", "nunique"),
    Monetary=("TotalPrice", "sum"),
)
rfm_log = rfm.copy()
rfm_log["Frequency"] = np.log1p(rfm_log["Frequency"])
rfm_log["Monetary"] = np.log1p(rfm_log["Monetary"])
scaled = StandardScaler().fit_transform(rfm_log[["Recency", "Frequency", "Monetary"]])
kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)
rfm["Segment"] = kmeans.fit_predict(scaled)
profile = rfm.groupby("Segment")[["Recency", "Frequency", "Monetary"]].mean()
ranked = profile.sort_values(["Monetary", "Recency"], ascending=[False, True]).index.tolist()
names = {ranked[0]: "Champions", ranked[1]: "Loyal / Steady", ranked[2]: "At Risk", ranked[3]: "Lost / Low-Value"}
rfm["SegmentName"] = rfm["Segment"].map(names)

seg_counts = rfm["SegmentName"].value_counts()
seg_revenue = rfm.groupby("SegmentName")["Monetary"].sum()
seg_order = ["Champions", "Loyal / Steady", "At Risk", "Lost / Low-Value"]
seg_colors = {"Champions": BLUE, "Loyal / Steady": AQUA, "At Risk": ORANGE, "Lost / Low-Value": RED}

fig_segments = go.Figure(go.Pie(
    labels=seg_order, values=[seg_counts[s] for s in seg_order],
    marker_colors=[seg_colors[s] for s in seg_order],
    hole=0.5, textinfo="label+percent",
    customdata=[seg_revenue[s] for s in seg_order],
    hovertemplate="%{label}<br>%{value} customers (%{percent})<br>£%{customdata:,.0f} revenue<extra></extra>",
))
fig_segments.update_layout(
    title="Customer Segments",
    height=460, margin=dict(t=60, l=20, r=20, b=20),
)

# %% [markdown]
# ## 6. Export standalone HTML fragments (embedded into dashboard.html)

# %%
KPI = {
    "revenue": f"£{df['TotalPrice'].sum():,.0f}",
    "orders": f"{df['InvoiceNo'].nunique():,}",
    "customers": f"{df['CustomerID'].nunique():,}",
    "aov": f"£{df['TotalPrice'].sum() / df['InvoiceNo'].nunique():,.2f}",
}
print(KPI)

configs = dict(displaylogo=False, modeBarButtonsToRemove=["lasso2d", "select2d"])

for name, fig in [("chart_trend", fig_trend), ("chart_map", fig_map), ("chart_products", fig_products), ("chart_segments", fig_segments)]:
    html = pio.to_html(fig, include_plotlyjs=False, full_html=False, div_id=name, config=configs)
    with open(f"../assets/{name}.html", "w") as f:
        f.write(html)
    print("wrote", name)
