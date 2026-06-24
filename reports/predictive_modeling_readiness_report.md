# Predictive Modeling Readiness Report
## Phase 9 - Baseline Modeling Gate

**Generated:** 2026-06-24  
**Input Dataset:** `data/processed/telco_customer_churn_clv.csv`  
**Status:** In Progress - Baseline models trained

---

## Summary

- Records evaluated: 7,043
- Candidate features: 65
- Target classes present: 2
- Class 0 count: 5,701
- Class 1 count: 1,342

## Readiness Checks

- [x] Modeling dataset loaded successfully
- [x] Leakage-prone identifiers can be excluded from feature matrix
- [x] Target distribution validated
- [x] Both churn classes available for supervised training
- [x] Baseline model training
- [x] Model comparison and selection

## Blocking Issue

No blocking issue detected for target classes. Supervised model training can proceed.

## Planned Model Stack

- Logistic Regression baseline
- Random Forest classifier
- XGBoost classifier

## Baseline Model Results

| Model | Accuracy | Precision | Recall | F1 | ROC AUC |
|---|---:|---:|---:|---:|---:|
| Logistic Regression | 0.8013 | 0.4143 | 0.1082 | 0.1716 | 0.7609 |
| Random Forest | 0.8048 | 0.4364 | 0.0896 | 0.1486 | 0.7458 |

- Current champion by ROC AUC: **Logistic Regression** (0.7609)

## Next Steps

1. Tune top model hyperparameters with cross-validation.
2. Add threshold analysis for recall/precision trade-offs.
3. Promote champion model into Phase 10 explainability workflow.