# Data source

Dataset: [Real / Fake Job Posting Prediction](https://www.kaggle.com/datasets/shivamb/real-or-fake-fake-jobposting-prediction) (Kaggle, shivamb).

Direct download used by the notebook:
```
https://raw.githubusercontent.com/Vishvam17/Real-or-Fake-Jobposting-Prediction/master/fake_job_postings.csv
```

Not committed to the repo (~48MB). To reproduce:
```bash
curl -L -o fake_job_postings.csv "https://raw.githubusercontent.com/Vishvam17/Real-or-Fake-Jobposting-Prediction/master/fake_job_postings.csv"
```

17,880 postings, 18 columns (title, location, department, salary_range, company_profile, description, requirements, benefits, telecommuting, has_company_logo, has_questions, employment_type, required_experience, required_education, industry, function, fraudulent). 4.84% labeled fraudulent.
