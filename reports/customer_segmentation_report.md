# Customer Segmentation Report
## Phase 7 - RFM-Style Clustering

**Generated:** 2026-06-24  
**Input Dataset:** `data/processed/telco_customer_churn_engineered.csv`  
**Output Dataset:** `data/processed/telco_customer_churn_segments.csv`  
**Status:** In Progress - Segment profiles generated

---

## Summary

- Customers segmented: 7,043
- Churn labels available in snapshot: 1,342
- Segment count: 4

## Segmentation Features

- `recency_proxy`
- `frequency_proxy`
- `monetary_proxy`
- `service_depth_proxy`
- `commitment_proxy`
- `churn_risk_proxy`

## Segment Profiles

### Low Engagement Churn Risk

- Segment ID: 3
- Customers: 1,981
- Average tenure proxy: 0.4206
- Average monthly charge proxy: 0.5061
- Average total charge proxy: 0.2405
- Average add-on count: 2.37
- Average risk proxy: 1.5937
- Churn rate: 35.39%

### Stable Value Seekers

- Segment ID: 0
- Customers: 1,856
- Average tenure proxy: 0.7910
- Average monthly charge proxy: 0.5743
- Average total charge proxy: 0.4965
- Average add-on count: 2.27
- Average risk proxy: -0.9411
- Churn rate: 7.00%

### At-Risk New Customers

- Segment ID: 1
- Customers: 1,736
- Average tenure proxy: 0.2979
- Average monthly charge proxy: 0.4301
- Average total charge proxy: 0.1388
- Average add-on count: 2.53
- Average risk proxy: -1.0905
- Churn rate: 11.29%

### High Value Loyalists

- Segment ID: 2
- Customers: 1,470
- Average tenure proxy: 0.4922
- Average monthly charge proxy: 0.4877
- Average total charge proxy: 0.2717
- Average add-on count: 0.65
- Average risk proxy: 0.4702
- Churn rate: 21.43%

## Stability Check

- k=3 | inertia=26410.3242 | silhouette=0.2123
- k=4 | inertia=23263.4174 | silhouette=0.1982
- k=5 | inertia=21084.5456 | silhouette=0.1945

## Retention Playbooks

### At-Risk New Customers

- Trigger: tenure under 6 months or low add-on adoption.
- Action: launch a guided onboarding sequence with first-30-day check-ins.
- Action: push auto-pay adoption and simplify first-bill resolution.
- KPI: reduce early-stage churn exposure and increase addon_count within 60 days.

### Low Engagement Churn Risk

- Trigger: moderate tenure with weak bundle adoption and elevated risk proxy.
- Action: run targeted engagement nudges and service-bundle offers.
- Action: review support friction and unresolved service issues.
- KPI: lift service_depth_proxy and lower churn_risk_proxy over 90 days.

### High Value Loyalists

- Trigger: long tenure, higher monetary value, and strong service adoption.
- Action: provide loyalty rewards, premium support, and proactive renewal outreach.
- Action: cross-sell value-added services instead of discount-led interventions.
- KPI: preserve retention while expanding average add-on count and value.

### Stable Value Seekers

- Trigger: stable tenure and moderate value with balanced service usage.
- Action: maintain price transparency and promote low-friction self-service.
- Action: cross-sell carefully to avoid churn-inducing complexity.
- KPI: sustain retention and gradually increase service adoption efficiency.


- Best balance observed at k=3 by silhouette score.

## Notes

- Segment labels are business-friendly summaries mapped from clustering output.
- Recency and monetary proxies preserve ordering for behavioral interpretation.
- Churn rate is shown only as an exploratory snapshot because the current dataset has no positive churn cases.

## Next Steps

1. Validate segment stability across alternate cluster counts.
2. Use retention playbooks to drive segment-level interventions and dashboard views.
3. Use segmentation output as a feature for CLV and recommendation analyses.