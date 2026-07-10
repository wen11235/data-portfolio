# Data source

Dataset: [UCI Machine Learning Repository — Online Retail](https://archive.ics.uci.edu/dataset/352/online+retail)

Direct download used by the notebook:
```
https://archive.ics.uci.edu/ml/machine-learning-databases/00352/Online%20Retail.xlsx
```

Not committed to the repo (~23MB as .xlsx / ~46MB as .csv). To reproduce:

```bash
curl -L -o online_retail.xlsx "https://archive.ics.uci.edu/ml/machine-learning-databases/00352/Online%20Retail.xlsx"
python3 -c "import pandas as pd; pd.read_excel('online_retail.xlsx').to_csv('online_retail.csv', index=False)"
```

541,909 transactions, Dec 2010 – Dec 2011, UK-based online gift retailer, 8 columns (InvoiceNo, StockCode, Description, Quantity, InvoiceDate, UnitPrice, CustomerID, Country).
