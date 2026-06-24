# Customer Lifetime Value Report
## Phase 8 - CLV Proxy Analysis

**Generated:** 2026-06-24  
**Input Dataset:** `data/processed/telco_customer_churn_segments.csv`  
**Output Dataset:** `data/processed/telco_customer_churn_clv.csv`  
**Status:** In Progress - CLV dataset generated

---

## Summary

- Customers analyzed: 7,043
- Total discounted CLV proxy: $27,338,378.78
- Average CLV proxy per customer: $3,881.64

## CLV Features

- `monthly_value_proxy`
- `projected_remaining_months`
- `expected_lifetime_months`
- `discounted_lifetime_value`
- `retention_leverage_score`

## Segment Summary

### Stable Value Seekers

- Customers: 1,856
- Average monthly value proxy: $75.43
- Average expected lifetime: 100.08 months
- Average discounted CLV: $4,731.84
- Average retention leverage: 2394.59
- Average risk proxy: -0.9411

### High Value Loyalists

- Customers: 1,470
- Average monthly value proxy: $66.77
- Average expected lifetime: 89.28 months
- Average discounted CLV: $3,894.74
- Average retention leverage: 1955.87
- Average risk proxy: 0.4702

### At-Risk New Customers

- Customers: 1,736
- Average monthly value proxy: $61.01
- Average expected lifetime: 86.04 months
- Average discounted CLV: $3,490.21
- Average retention leverage: 1768.55
- Average risk proxy: -1.0905

### Low Engagement Churn Risk

- Customers: 1,981
- Average monthly value proxy: $68.61
- Average expected lifetime: 69.51 months
- Average discounted CLV: $3,418.38
- Average retention leverage: 1727.17
- Average risk proxy: 1.5937

## Top Customers by CLV

| Customer ID | Segment | Monthly Value | Expected Lifetime (Months) | Discounted CLV |
|---|---|---:|---:|---:|
| ID-002740 | Stable Value Seekers | $117.30 | 116.00 | $8,031.56 |
| ID-001844 | Stable Value Seekers | $116.36 | 116.00 | $7,967.20 |
| ID-004070 | High Value Loyalists | $115.99 | 116.00 | $7,941.86 |
| ID-000442 | Stable Value Seekers | $115.74 | 116.00 | $7,924.75 |
| ID-001635 | Stable Value Seekers | $115.70 | 116.00 | $7,922.01 |
| ID-002510 | Stable Value Seekers | $115.50 | 116.00 | $7,908.31 |
| ID-000425 | High Value Loyalists | $117.95 | 111.00 | $7,886.36 |
| ID-001534 | High Value Loyalists | $117.50 | 111.00 | $7,856.27 |
| ID-002152 | Stable Value Seekers | $114.56 | 116.00 | $7,843.95 |
| ID-004520 | Stable Value Seekers | $116.95 | 111.00 | $7,819.50 |

## Notes

- CLV is intentionally explainable and proxy-based because supervised churn probabilities are not available from the current snapshot.
- The model rewards longer projected lifetimes, higher monthly value, and lower operational risk.
- Segment-level results can be used to prioritize retention investment and upsell strategy.

## Next Steps

1. Validate CLV sensitivity against alternate discount rates and retention horizons.
2. Build CLV threshold bands for executive dashboarding.
3. Use segment-specific CLV to refine retention playbooks and marketing offers.