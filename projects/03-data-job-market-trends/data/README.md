# Data source

Dataset: [iweld/data-analyst-job-postings](https://github.com/iweld/data-analyst-job-postings) (`gsearch_jobs_2022.csv`), originally compiled by Luke Barousse from Google Jobs search results for his Data Analyst course.

Direct download used by the notebook:
```
https://raw.githubusercontent.com/iweld/data-analyst-job-postings/main/source_data/csv/gsearch_jobs_2022.csv
```

Not committed to the repo (~25MB). To reproduce:
```bash
curl -L -o gsearch_jobs_2022.csv "https://raw.githubusercontent.com/iweld/data-analyst-job-postings/main/source_data/csv/gsearch_jobs_2022.csv"
```

5,488 US data job postings, Nov–Dec 2022, 27 columns including `title`, `company_name`, `description`, `description_tokens` (pre-extracted skill/tool keywords), and `salary_standardized`.
