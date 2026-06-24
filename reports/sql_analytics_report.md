# SQL Analytics Layer Report
## Phase 11 - Relational KPI Views

**Generated:** 2026-06-24  
**Database:** `data/processed/churn_analytics.db`  
**Source Table:** `customer_analytics`  
**Status:** In Progress - Views, quality checks, and templates generated

---

## View Inventory

- `vw_churn_overview`
- `vw_segment_kpis`
- `vw_contract_retention`
- `vw_clv_bands`
- `vw_top_risk_customers`

## Churn Overview

| customers | churned_customers | churn_rate_pct | avg_discounted_clv | total_discounted_clv |
|---|---|---|---|---|
| 7043 | 1342 | 19.05 | 3881.64 | 27338378.78 |

## Segment KPIs

| segment_label | customers | churn_rate_pct | avg_monthly_charges_norm | avg_discounted_clv | avg_retention_leverage |
|---|---|---|---|---|---|
| Stable Value Seekers | 1856 | 7 | 0.5743 | 4731.84 | 2394.59 |
| High Value Loyalists | 1470 | 21.43 | 0.4877 | 3894.74 | 1955.87 |
| At-Risk New Customers | 1736 | 11.29 | 0.4301 | 3490.21 | 1768.55 |
| Low Engagement Churn Risk | 1981 | 35.39 | 0.5061 | 3418.38 | 1727.17 |

## Contract Retention

| Contract_encoded | contract_type | customers | churn_rate_pct | avg_discounted_clv |
|---|---|---|---|---|
| 0 | Month-to-month | 2331 | 36.25 | 3459.11 |
| 1 | One year | 2376 | 13.76 | 4002.12 |
| 2 | Two year | 2336 | 7.28 | 4180.71 |

## CLV Bands

| clv_band | customers | churn_rate_pct | avg_churn_risk_proxy |
|---|---|---|---|
| High CLV (>=4500) | 2714 | 15.7 | -0.3097 |
| Mid CLV (2500-4499) | 2430 | 21.23 | 0.1798 |
| Low CLV (<2500) | 1899 | 21.06 | 0.3224 |

## Top Risk Customers (Top 10)

| customerID | segment_label | churn_risk_proxy | discounted_lifetime_value | risk_reason |
|---|---|---|---|---|
| ID-000354 | Low Engagement Churn Risk | 5.3 | 2796.77 | Month-to-month risk |
| ID-000409 | High Value Loyalists | 5.3 | 2287 | Month-to-month risk |
| ID-004938 | High Value Loyalists | 4.5 | 4374.69 | Month-to-month risk |
| ID-001128 | Low Engagement Churn Risk | 4.5 | 3794.38 | Month-to-month risk |
| ID-004375 | Low Engagement Churn Risk | 4.5 | 3715.57 | Month-to-month risk |
| ID-004649 | Low Engagement Churn Risk | 4.5 | 3603.94 | Month-to-month risk |
| ID-002164 | High Value Loyalists | 4.5 | 3508.4 | Month-to-month risk |
| ID-001482 | Low Engagement Churn Risk | 4.5 | 2956.11 | Month-to-month risk |
| ID-001485 | High Value Loyalists | 4.5 | 2613.01 | Month-to-month risk |
| ID-005188 | Low Engagement Churn Risk | 4.5 | 2353.92 | Month-to-month risk |

## SQL Quality Checks

| Check | Status | Description |
|---|---|---|
| row_count_match_overview | PASS | Base table row count matches churn overview total. |
| segment_sum_matches_base | PASS | Sum of segment customers matches base row count. |
| contract_sum_matches_base | PASS | Sum of contract customers matches base row count. |
| clv_band_sum_matches_base | PASS | Sum of CLV band customers matches base row count. |
| churn_rate_bounds | PASS | Overall churn rate is within 0-100%. |
| non_null_customer_id | PASS | No NULL/blank customer IDs in base table. |

## Parameterized Dashboard Query Templates

The following templates are available in `sql/dashboard_query_templates.sql` for dashboard filters and drill-downs:

```sql
-- Phase 11: Parameterized Dashboard Query Templates (SQLite style)
-- Named placeholders can be bound by dashboard tools/app code.

-- 1) Segment KPI filter template
SELECT
    segment_label,
    COUNT(*) AS customers,
    ROUND(100.0 * AVG(CASE WHEN Churn_encoded = 1 THEN 1.0 ELSE 0.0 END), 2) AS churn_rate_pct,
    ROUND(AVG(discounted_lifetime_value), 2) AS avg_discounted_clv
FROM customer_analytics
WHERE (:segment_label IS NULL OR segment_label = :segment_label)
GROUP BY segment_label
ORDER BY avg_discounted_clv DESC;

-- 2) CLV threshold and risk filter template
SELECT
    customerID,
    segment_label,
    ROUND(discounted_lifetime_value, 2) AS discounted_lifetime_value,
    ROUND(churn_risk_proxy, 4) AS churn_risk_proxy
FROM customer_analytics
WHERE discounted_lifetime_value >= :min_clv
  AND churn_risk_proxy >= :min_risk
ORDER BY churn_risk_proxy DESC, discounted_lifetime_value DESC
LIMIT :top_n;

-- 3) Contract retention comparison template
SELECT
    CASE
        WHEN Contract_encoded = 0 THEN 'Month-to-month'
        WHEN Contract_encoded = 1 THEN 'One year'
        WHEN Contract_encoded = 2 THEN 'Two year'
        ELSE 'Unknown'
    END AS contract_type,
    COUNT(*) AS customers,
    ROUND(100.0 * AVG(CASE WHEN Churn_encoded = 1 THEN 1.0 ELSE 0.0 END), 2) AS churn_rate_pct,
    ROUND(AVG(discounted_lifetime_value), 2) AS avg_discounted_clv
FROM customer_analytics
WHERE (:include_month_to_month = 1 OR Contract_encoded <> 0)
GROUP BY Contract_encoded
ORDER BY Contract_encoded;

-- 4) Segment + payment method drill-down template
SELECT
    segment_label,
    PaymentMethod_encoded,
    COUNT(*) AS customers,
    ROUND(100.0 * AVG(CASE WHEN Churn_encoded = 1 THEN 1.0 ELSE 0.0 END), 2) AS churn_rate_pct,
    ROUND(AVG(churn_risk_proxy), 4) AS avg_churn_risk_proxy
FROM customer_analytics
WHERE (:segment_filter IS NULL OR segment_label = :segment_filter)
  AND (:payment_method_filter IS NULL OR PaymentMethod_encoded = :payment_method_filter)
GROUP BY segment_label, PaymentMethod_encoded
ORDER BY customers DESC;
```

## Next Steps

1. Connect SQL views and parameterized templates to Power BI semantic model.
2. Add refresh monitoring checks for production readiness.
3. Add dashboard-level query performance benchmarks.