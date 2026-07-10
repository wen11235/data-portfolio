# Data source

Dataset: [Cookie Cats A/B Testing](https://www.kaggle.com/datasets/mursideyarkin/mobile-games-ab-testing-cookie-cats) (Kaggle), mirrored on GitHub.

Direct download used by the notebook:
```
https://raw.githubusercontent.com/ryanschaub/Mobile-Games-A-B-Testing-with-Cookie-Cats/master/cookie_cats.csv
```

Not committed to the repo (~2.7MB). To reproduce:
```bash
curl -L -o cookie_cats.csv "https://raw.githubusercontent.com/ryanschaub/Mobile-Games-A-B-Testing-with-Cookie-Cats/master/cookie_cats.csv"
```

90,189 players, 5 columns: `userid`, `version` (`gate_30`/`gate_40`), `sum_gamerounds`, `retention_1`, `retention_7`.
