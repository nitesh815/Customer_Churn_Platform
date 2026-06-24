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