# Data source

Dataset: [IBM Telco Customer Churn](https://github.com/IBM/telco-customer-churn-on-icp4d) (also mirrored widely as the "Telco Customer Churn" Kaggle dataset).

Direct download used by the notebook:
```
https://raw.githubusercontent.com/IBM/telco-customer-churn-on-icp4d/master/data/Telco-Customer-Churn.csv
```

Not committed to the repo. To reproduce:
```bash
curl -L -o telco_churn.csv "https://raw.githubusercontent.com/IBM/telco-customer-churn-on-icp4d/master/data/Telco-Customer-Churn.csv"
```

7,043 customers, 21 columns (customerID + 19 features + Churn label).
