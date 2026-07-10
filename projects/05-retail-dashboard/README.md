# Retail Sales Interactive Dashboard

**TL;DR:** The same Online Retail dataset as [Project 1](../01-retail-customer-analytics/), repackaged as a click-and-filter dashboard instead of a static report — country dropdown, metric toggle, choropleth map, and a click-to-isolate segment chart, all running client-side with Plotly.js (no server, works directly on GitHub Pages).

[📊 Open the dashboard](dashboard.html) · [📓 Build notebook](notebooks/build_dashboard.ipynb)

## Why this exists

[Project 1](../01-retail-customer-analytics/) answers a fixed set of questions with a written report. Some stakeholders don't want a report — they want to poke at the data themselves. This project takes the identical cleaned dataset and RFM segmentation and turns it into something a non-technical stakeholder could open and explore without reading code, which is a different (and very commonly requested) Data Analyst skill: BI tooling, not just analysis.

## Scope trade-off: static, not Streamlit/Dash

A fully cross-filtered dashboard — click one country, every chart updates together — is usually built with Dash or Streamlit, both of which need a live Python process running somewhere. GitHub Pages only serves static files, so that wasn't an option without paying for separate hosting (Streamlit Community Cloud, etc.) and asking you to maintain a second deployment.

Instead, each chart is genuinely interactive on its own — hover tooltips, zoom/pan, a country dropdown on the revenue trend, a metric toggle on the product chart, legend click-to-isolate on the segment chart — built with Plotly's client-side `updatemenus`, exported to static HTML, and embedded directly in this page. No backend, loads instantly, and it'll still work exactly the same in five years with zero maintenance. The trade-off: charts filter independently rather than one global filter driving all four at once.

## What's in it

- **Revenue trend** — monthly revenue, filterable by country (dropdown) with a date range slider.
- **Revenue by country** — choropleth map, hover for exact figures.
- **Top 15 products** — toggle between revenue and units sold.
- **Customer segments** — the same RFM/KMeans segments as Project 1, as a donut chart; click a legend entry to isolate a segment.

## Method

Reuses Project 1's exact cleaning and RFM/KMeans logic (see the build notebook) so the numbers are consistent across both projects — same £8.9M revenue, same 4,338 customers, same 4 segments. Each Plotly figure is exported with `plotly.io.to_html(..., include_plotlyjs=False, full_html=False)` to get a lightweight `<div>` + script fragment, then all four are embedded into one page that loads Plotly.js once from a CDN.

## Skills demonstrated

Plotly, interactive dashboard design, client-side filtering without a backend, choropleth mapping, translating the same analysis for different audiences (technical report vs self-serve tool).
