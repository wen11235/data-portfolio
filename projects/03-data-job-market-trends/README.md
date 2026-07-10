# Data Job Market: Skill Demand Analysis

**TL;DR:** Text-mined 5,488 real US data job postings (Nov–Dec 2022). SQL (52%), Excel (37%), Python (30%), Power BI (29%) and Tableau (28%) are the top 5 requested skills overall — and Data Analyst vs Data Scientist postings want visibly different toolkits.

[📄 Full report](report.html) · [📓 Notebook](notebooks/skill_trends.ipynb)

## Why this project

Most portfolio projects analyze someone else's business problem. This one analyzes the job search itself — using the same text-mining skills a Data Analyst would use on any unstructured text field, applied to something directly useful for my own search (and hopefully for other Information Management grads doing the same search).

## Data

[gsearch_jobs_2022](https://github.com/iweld/data-analyst-job-postings) — 5,488 real US data job postings scraped from Google Jobs search results (Nov–Dec 2022), originally compiled by Luke Barousse for his Data Analyst course. Each posting includes a pre-extracted `description_tokens` field (tools/technologies mentioned in the description) plus title, company, and a standardized salary field where available. Not committed to this repo (~25MB, see `data/README.md`).

**Scope note:** two months, US only — this is a skill-demand *snapshot*, not a multi-year trend line. Framed that way throughout rather than overclaiming trend data we don't have.

## Method

1. Classify each posting's `title` into **Data Analyst**, **Data Scientist**, or **Hybrid/Other** by keyword match.
2. Parse `description_tokens` (a stringified list per posting) and explode into one row per (posting, skill) — 113 distinct skills/tools across the dataset.
3. Rank overall skill demand, then compare Data Analyst vs Data Scientist postings side by side.
4. Cross-reference skills against the 18% of postings with a standardized salary figure.

## Findings

**Top 5 skills overall** (% of all 5,488 postings mentioning it): SQL 52.2%, Excel 36.6%, Python 30.4%, Power BI 28.5%, Tableau 28.2%.

**Data Analyst (n=4,430) vs Data Scientist (n=161) postings:**

| Skill | Data Analyst | Data Scientist |
|---|---|---|
| SQL | 57.8% | 59.6% |
| Excel | 41.5% | 5.6% |
| Power BI | 33.3% | 6.8% |
| Tableau | 31.4% | 19.3% |
| Python | 31.2% | **70.8%** |
| R | 23.0% | **39.8%** |
| AWS | 5.6% | 14.3% |

SQL is table stakes for both roles at nearly identical rates. Everything else diverges sharply: Analyst postings lean on Excel/Power BI/Tableau (reporting & BI tooling), while Scientist postings lean hard on Python and R (modeling tooling) and skew more toward cloud (AWS).

**Skills associated with higher average posted salary** (min. 20 postings, of the 987 with salary data): Java ($127.6k), Hadoop ($125.6k), NoSQL ($125.2k), Qlik ($117.3k), AWS ($117.1k), Snowflake ($113.1k) — these lean toward specialized/production/data-engineering-adjacent tooling rather than general spreadsheet or BI tools.

## Caveats

- `description_tokens` is a pre-extracted keyword list from the source dataset, not something I NLP'd myself from raw text — a couple of entries (e.g. "Go") may include false positives from common English words rather than the Golang language. Read the low-frequency tail with appropriate skepticism.
- Salary data covers only 18% of postings and isn't randomly distributed (larger/more transparent employers post salary more often), so the salary-vs-skill numbers are directional, not a rigorous causal estimate.
- Nov–Dec 2022, US-only — not necessarily representative of the current or non-US market (relevant if job-hunting in Taiwan, for instance).

## Takeaways for my own job search

- SQL and Excel are genuinely table-stakes for Data Analyst roles — worth being rock-solid rather than "familiar with."
- Python + stats/ML tooling is the clearest Data Analyst → Data Scientist differentiator, which is why [Project 1](../01-retail-customer-analytics/) and [Project 2](../02-churn-prediction/) in this portfolio deliberately cover both sides of that line.
- Cloud/warehouse tools (AWS, Snowflake) show up often enough, and correlate with higher posted salary, to be worth a passing familiarity even in an entry-level search.

## Skills demonstrated

Text mining / keyword extraction, pandas `explode`, comparative analysis, market research framed as a self-directed data project.
