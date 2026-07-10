# Data Portfolio

A collection of end-to-end data analytics / data science projects, built to showcase skills for Data Analyst / Data Scientist roles. Each project uses a real public dataset and includes a Jupyter notebook (full analysis) plus a standalone `report.html` (shareable write-up with charts and findings).

Live site: `https://wen11235.github.io/<repo-name>/` (update once deployed).

## Projects

| # | Project | Focus | Key Skills |
|---|---------|-------|------------|
| 1 | [Retail Customer Analytics & Segmentation](projects/01-retail-customer-analytics/) | Data Analyst | SQL (DuckDB), RFM segmentation, cohort analysis, business storytelling |
| 2 | [Customer Churn Prediction](projects/02-churn-prediction/) | Data Scientist | ML pipeline, model comparison, SHAP explainability |
| 3 | [Data Job Market Skill Trends](projects/03-data-job-market-trends/) | Data Analyst / NLP | Text mining, skill-demand analysis, market research |
| 4 | [Brain Tumor Segmentation (MRI)](projects/04-brain-tumor-segmentation/) | Deep Learning / Coursework | PyTorch, U-Net variants, evaluation methodology, model calibration |
| 5 | [Retail Sales Interactive Dashboard](projects/05-retail-dashboard/) | Data Analyst / BI | Plotly, interactive dashboards, client-side filtering |
| 6 | [A/B Test Analysis: Cookie Cats](projects/06-ab-testing/) | Data Scientist / Experimentation | Hypothesis testing, bootstrap resampling, statistical vs. practical significance |

## Running locally

```bash
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
jupyter lab
```

Open any `projects/*/notebooks/*.ipynb` and run top-to-bottom. Each project folder has its own README with the dataset source, method, and findings.

## Site

`index.html` + `assets/` form a static portfolio homepage (no build step). To deploy: push this repo to GitHub and enable GitHub Pages on the `main` branch, root folder.
