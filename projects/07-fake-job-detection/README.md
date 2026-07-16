# Detecting Fake Job Postings with Text Mining

**TL;DR:** Classified 17,880 real job postings as real or fraudulent under severe class imbalance (4.84% fraud). Best reproduced result: TF-IDF + SVM + SMOTE, 0.903 F1 / 0.849 balanced accuracy. Originally extended to CNN/BiLSTM/BERT (up to 0.96 F1) — see the scope note below on what's freshly reproduced here vs. cited from the original run.

[📄 Full report](report.html) · [📓 Notebook](notebooks/analysis.ipynb) · [📑 Original project write-up](Text_Mining_Report.pdf)

*Originally built as a graduate Text Mining course project (Information Management, UIUC). The traditional ML baseline, SMOTE resampling, and feature-importance analysis are re-executed fresh in this repo's notebook; the deep learning and BERT results are cited from the original run (see scope note).*

## Problem

Fraudulent job postings cost applicants money, time, and in some cases their identity. This project builds a text classifier that flags fraudulent postings using only the text content (title, company profile, description, requirements, benefits) — under a dataset where fraud is less than 5% of postings, so naive accuracy is a meaningless metric (predicting "real" for everything scores 95%).

## Scope note: what's fresh vs. cited

This notebook **reproduces end to end**: data cleaning, EDA, TF-IDF/CountVectorizer feature extraction, 4 traditional ML models (Naive Bayes, Logistic Regression, SVM, Random Forest), SMOTE resampling, and Logistic Regression feature-importance analysis — all executed fresh for this repo, with real (and slightly different from the original run) numbers, since randomness, library versions, and minor preprocessing choices don't reproduce bit-for-bit.

The original project also trained **CNN, LSTM, BiLSTM** (Keras) and **fine-tuned BERT-base** (HuggingFace, 5 epochs). Those aren't re-run here — the deep learning models need TensorFlow (not worth the install for this repo), and fine-tuning BERT on 17,880 documents for 5 epochs needs a GPU (the original ran on Colab; CPU-only in this environment would take hours). Those results are **cited from the original completed run**, not re-derived — see the table below and the [original PDF write-up](Text_Mining_Report.pdf) for full methodology and error analysis on those models.

## Data

[Real / Fake Job Posting Prediction](https://www.kaggle.com/datasets/shivamb/real-or-fake-fake-jobposting-prediction) (Kaggle, shivamb) — 17,880 postings, 18 columns. Not committed to this repo (~48MB, see `data/README.md`).

## Method (this notebook)

1. **Clean** — fill missing text fields with `"NA"`, combine title/location/company profile/description/requirements/benefits into one document per posting, lowercase, strip punctuation/numbers, remove stopwords, lemmatize.
2. **Split** — 80/20 stratified (14,304 train / 3,576 test), vectorizers fit on training data only.
3. **Baseline models** — Naive Bayes, Logistic Regression, SVM, Random Forest × TF-IDF/CountVectorizer (2,000-term vocabulary).
4. **SMOTE** — synthetic minority oversampling on the training set only, same 4 models re-evaluated.
5. **Feature importance** — Logistic Regression + TF-IDF coefficients, ranked.

## Results (reproduced fresh in this repo)

| Vectorizer | Model | Balanced Acc. | Precision | Recall | F1 |
|---|---|---|---|---|---|
| CountVec | Logistic Regression (baseline) | 0.885 | 0.887 | 0.885 | 0.886 |
| TF-IDF | SVM (baseline) | 0.795 | 0.990 | 0.795 | 0.866 |
| **TF-IDF** | **SVM + SMOTE** | **0.849** | **0.980** | **0.849** | **0.903** |
| TF-IDF | Random Forest + SMOTE | 0.829 | 0.983 | 0.829 | 0.890 |
| TF-IDF | Logistic Regression + SMOTE | 0.912 | 0.808 | 0.912 | 0.851 |

TF-IDF + SVM + SMOTE was the best F1 in this run. Logistic Regression + SMOTE trades precision for the highest recall (0.912) — the better choice if missing a fraudulent posting is costlier than a false alarm.

**Top fraud-indicative words** (Logistic Regression + TF-IDF coefficients): *earn, entry, aptitude, financing, administrative, link, money, phone, cash* — urgency and vague-compensation language.
**Top real-indicative words**: *team, client, website, growing, search, recruitment, employment, software, digital* — specific professional/organizational context.

## Results (cited from the original run — CNN/LSTM/BiLSTM/BERT)

| Model | Type | Balanced Acc. | Precision | Recall | F1 |
|---|---|---|---|---|---|
| **CNN** | Deep Learning | 0.930 | 0.99 | 0.93 | **0.96** |
| **BiLSTM** | Deep Learning | 0.930 | 0.99 | 0.93 | **0.96** |
| LSTM | Deep Learning | 0.500 | 0.49 | 0.50 | 0.49 |
| BERT (fine-tuned) | Transformer | 0.930 | 0.96 | 0.93 | 0.94 |

CNN and BiLSTM won outright in the original run; the unidirectional LSTM collapsed to predicting the majority class (likely too little context to pick up scam signals scattered through longer postings). BERT was competitive but didn't clearly beat the lighter CNN/BiLSTM despite far higher training cost — a real accuracy-vs-cost tradeoff, not just "bigger model wins."

## Error analysis (from the original run)

The hardest cases to classify, across every model, shared a pattern: **short or generic descriptions**, and **fraudulent postings written in polished, professional-sounding language** that mimics legitimate corporate tone — hard to catch even for a human reader. Conversely, some real postings with enthusiastic marketing-style language ("join our fast-growing team in a fun environment!") got flagged as false positives, since that phrasing overlaps with scam-adjacent lexical patterns.

## Skills demonstrated

Text preprocessing (NLTK, lemmatization), TF-IDF/CountVectorizer, class-imbalance handling (SMOTE), traditional ML model comparison, deep learning (CNN/LSTM/BiLSTM), BERT fine-tuning, feature importance / model interpretability, qualitative error analysis, literature review.
