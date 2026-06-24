# Explainable AI Report
## Phase 10 - Model Interpretability

**Generated:** 2026-06-24  
**Input Dataset:** `data/processed/telco_customer_churn_clv.csv`  
**Output Artifacts:** `reports/feature_explanations.csv`, `reports/local_reason_codes.csv`, `reports/explanation_stability.csv`  
**Status:** In Progress - Global and local explanations generated

---

## Candidate Model Performance

| Model | ROC AUC |
|---|---:|
| Logistic Regression | 0.7609 |
| Random Forest | 0.7458 |

- Champion model: **Logistic Regression**

## Top Feature Explanations

| Feature | Permutation Importance | Model-Specific Importance |
|---|---:|---:|
| churn_risk_proxy | 0.028208 | 0.333366 |
| is_month_to_month | 0.020542 | 0.287654 |
| Contract_encoded | 0.012675 | -0.241837 |
| commitment_proxy | 0.009689 | -0.198976 |
| PaymentMethod_encoded | 0.005697 | -0.119377 |
| InternetService_encoded | 0.005395 | 0.153796 |
| TechSupport_Yes | 0.003936 | -0.096983 |
| is_long_tenure_48m | 0.003429 | -0.123517 |
| internet_addon_adoption_rate | 0.003065 | 0.140115 |
| is_electronic_check | 0.003046 | 0.059912 |
| security_bundle | 0.001851 | 0.062585 |
| PaperlessBilling | 0.001587 | 0.075325 |
| monthly_value_proxy | 0.001327 | 0.061959 |
| MonthlyCharges_normalized | 0.001327 | 0.061959 |
| is_new_customer_0_6m | 0.001035 | 0.179762 |

## Local Reason Codes (Top 10 High-Risk Customers)

| Row ID | Predicted Risk | Reason Rank | Feature | Contribution |
|---:|---:|---:|---|---:|
| 3431 | 0.840921 | 1 | churn_risk_proxy | 0.944182 |
| 3431 | 0.840921 | 2 | is_new_customer_0_6m | 0.568568 |
| 3431 | 0.840921 | 3 | is_month_to_month | 0.408107 |
| 1127 | 0.810916 | 1 | churn_risk_proxy | 0.944182 |
| 1127 | 0.810916 | 2 | is_new_customer_0_6m | 0.568568 |
| 1127 | 0.810916 | 3 | is_month_to_month | 0.408107 |
| 1231 | 0.806772 | 1 | churn_risk_proxy | 0.901885 |
| 1231 | 0.806772 | 2 | is_new_customer_0_6m | 0.568568 |
| 1231 | 0.806772 | 3 | is_month_to_month | 0.408107 |
| 3353 | 0.794830 | 1 | churn_risk_proxy | 0.732700 |
| 3353 | 0.794830 | 2 | is_new_customer_0_6m | 0.568568 |
| 3353 | 0.794830 | 3 | is_month_to_month | 0.408107 |
| 642 | 0.793075 | 1 | churn_risk_proxy | 0.626959 |
| 642 | 0.793075 | 2 | is_new_customer_0_6m | 0.568568 |
| 642 | 0.793075 | 3 | is_month_to_month | 0.408107 |
| 343 | 0.790419 | 1 | churn_risk_proxy | 0.944182 |
| 343 | 0.790419 | 2 | is_new_customer_0_6m | 0.568568 |
| 343 | 0.790419 | 3 | is_month_to_month | 0.408107 |
| 4981 | 0.784663 | 1 | churn_risk_proxy | 0.732700 |
| 4981 | 0.784663 | 2 | is_new_customer_0_6m | 0.568568 |
| 4981 | 0.784663 | 3 | is_month_to_month | 0.408107 |
| 5187 | 0.783848 | 1 | churn_risk_proxy | 0.944182 |
| 5187 | 0.783848 | 2 | is_new_customer_0_6m | 0.568568 |
| 5187 | 0.783848 | 3 | is_month_to_month | 0.408107 |
| 1408 | 0.782956 | 1 | churn_risk_proxy | 0.901885 |
| 1408 | 0.782956 | 2 | is_new_customer_0_6m | 0.568568 |
| 1408 | 0.782956 | 3 | is_month_to_month | 0.408107 |
| 3127 | 0.775411 | 1 | churn_risk_proxy | 0.732700 |
| 3127 | 0.775411 | 2 | is_new_customer_0_6m | 0.568568 |
| 3127 | 0.775411 | 3 | is_month_to_month | 0.408107 |

## Explanation Stability Across Alternate Splits

| Seed | ROC AUC | Jaccard vs Seed 7 |
|---:|---:|---:|
| 7 | 0.7625 | 1.0000 |
| 42 | 0.7609 | 0.5385 |
| 99 | 0.7806 | 0.4286 |

## Interpretation Guidance

- Features with consistently high permutation and model-specific importance are strongest global drivers.
- Positive logistic coefficients increase churn risk score; negative coefficients reduce risk.
- Local reason codes can be attached to customer records for intervention workflows.
- Stability table shows whether top drivers are robust across alternate splits.

## Next Steps

1. Validate stability across time windows in addition to random split seeds.
2. Publish model cards and explanation summaries for business stakeholders.
3. Connect reason codes into dashboard and retention operations workflows.