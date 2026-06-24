# Feature Engineering Report
## Phase 6 - Derived Feature Construction

**Generated:** 2026-06-24  
**Input Dataset:** `data/processed/telco_customer_churn_processed.csv`  
**Output Dataset:** `data/processed/telco_customer_churn_engineered.csv`  
**Status:** In Progress - Core engineered feature set generated

---

## Summary

- Records processed: 7,043
- Total output features: 52
- New engineered features added: 17
- Churn base rate (reference): 19.05%
- Target distribution: No=5,701, Yes=1,342

## Engineered Features Added

- `is_new_customer_0_6m`
- `is_established_customer_24m`
- `is_long_tenure_48m`
- `is_month_to_month`
- `is_auto_pay`
- `is_electronic_check`
- `has_internet`
- `security_bundle`
- `addon_count`
- `internet_addon_adoption_rate`
- `charges_per_tenure_month`
- `high_monthly_charge`
- `high_total_value`
- `churn_risk_proxy`
- `tenure_x_monthlycharges`
- `mtm_x_echeck`
- `new_x_fiber`

## Quick Diagnostics

- High risk proxy customers (`churn_risk_proxy >= 2.0`): 15.75%
- New customers (`is_new_customer_0_6m = 1`): 9.12%
- Average add-on count: 2.02 / 6

## Notes

- Features are numeric and compatible with scikit-learn/XGBoost training pipelines.
- Risk proxy is a business-informed composite signal and does not use target leakage.
- Interaction features are included to improve nonlinear separation in churn models.
- Current dataset snapshot has single-class target if `Yes = 0`, which blocks supervised churn modeling until resolved.

## Next Steps

1. Run feature importance screening and collinearity checks.
2. Build train/validation split with stratification for Phase 9 modeling.
3. Benchmark baseline vs engineered-feature model lift.