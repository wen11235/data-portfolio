# Customer Churn Prediction

**TL;DR:** Predicting churn for 7,043 telecom customers (26.5% churn rate). Best model (Random Forest) reaches **0.843 ROC-AUC** and catches 76% of churners — with SHAP explaining exactly which factors drive each prediction.

[📄 Full report](report.html) · [📓 Notebook](notebooks/churn_model.ipynb)

## Problem

A telecom retention team needs to know, before a customer leaves, who's at risk and *why* — a black-box score isn't actionable. The goal: a model that ranks churn risk accurately **and** explains its reasoning well enough to inform a retention campaign.

## Data

[IBM Telco Customer Churn](https://github.com/IBM/telco-customer-churn-on-icp4d) — 7,043 real customers, 19 features (contract type, tenure, services subscribed, charges) + binary churn label. Not committed to this repo (~1MB, see `data/README.md`).

## Method

1. **Clean** — coerce `TotalCharges` to numeric (11 blank values, all brand-new tenure=0 customers → filled with 0).
2. **EDA** — churn rate by contract type, tenure, and monthly charges.
3. **Pipeline** — `ColumnTransformer` (one-hot encode 15 categorical features, scale 4 numeric features) feeding into 3 classifiers.
4. **Models compared** — Logistic Regression, Random Forest, XGBoost, all with class-imbalance handling (`class_weight="balanced"` / `scale_pos_weight`), evaluated on a held-out 20% stratified test set (1,409 customers).
5. **Explainability** — SHAP `TreeExplainer` on the winning model for global + per-customer feature attribution.

## Results

| Model | ROC-AUC | PR-AUC (Average Precision) |
|---|---|---|
| Logistic Regression | 0.842 | 0.633 |
| **Random Forest** | **0.843** | **0.653** |
| XGBoost | 0.841 | 0.652 |

All three models land within ~0.002 ROC-AUC of each other — Random Forest edges ahead and is the model used for the SHAP analysis below.

**Random Forest test-set performance** (accuracy alone is misleading here — churn is imbalanced, so precision/recall on the minority "Churned" class is what matters):

| Class | Precision | Recall | F1 |
|---|---|---|---|
| Stayed | 0.90 | 0.76 | 0.82 |
| Churned | 0.53 | **0.76** | 0.63 |

Recall on churners is prioritized over precision — for a retention team, missing an actual churner is far more costly than a false alarm (a discount offer to a loyal customer is cheap; losing a customer silently is not).

## What drives churn (SHAP)

- **Contract type dominates** — month-to-month customers churn far more than 1-2 year contract customers. Highest-leverage lever: incentivize a switch to annual contracts.
- **Tenure matters most in year 1** — churn risk peaks before the ~12-month mark. An onboarding/engagement push in months 1-6 targets the riskiest window directly.
- **High monthly charges without add-on services** (no tech support / online security) is a recurring churn pattern — bundling support may offset price sensitivity enough to retain at-risk customers.

## Skills demonstrated

`sklearn.Pipeline` / `ColumnTransformer`, model comparison under class imbalance (ROC-AUC, PR-AUC), XGBoost, SHAP explainability.
