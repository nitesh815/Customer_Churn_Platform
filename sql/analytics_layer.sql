-- Phase 11: SQL Analytics Layer
-- This script defines reusable analytical views on top of the
-- customer_analytics table loaded from the CLV-enriched dataset.

DROP VIEW IF EXISTS vw_churn_overview;
CREATE VIEW vw_churn_overview AS
SELECT
    COUNT(*) AS customers,
    SUM(CASE WHEN Churn_encoded = 1 THEN 1 ELSE 0 END) AS churned_customers,
    ROUND(100.0 * SUM(CASE WHEN Churn_encoded = 1 THEN 1 ELSE 0 END) / COUNT(*), 2) AS churn_rate_pct,
    ROUND(AVG(discounted_lifetime_value), 2) AS avg_discounted_clv,
    ROUND(SUM(discounted_lifetime_value), 2) AS total_discounted_clv
FROM customer_analytics;

DROP VIEW IF EXISTS vw_segment_kpis;
CREATE VIEW vw_segment_kpis AS
SELECT
    segment_label,
    COUNT(*) AS customers,
    ROUND(100.0 * AVG(CASE WHEN Churn_encoded = 1 THEN 1.0 ELSE 0.0 END), 2) AS churn_rate_pct,
    ROUND(AVG(MonthlyCharges_normalized), 4) AS avg_monthly_charges_norm,
    ROUND(AVG(discounted_lifetime_value), 2) AS avg_discounted_clv,
    ROUND(AVG(retention_leverage_score), 2) AS avg_retention_leverage
FROM customer_analytics
GROUP BY segment_label
ORDER BY avg_discounted_clv DESC;

DROP VIEW IF EXISTS vw_contract_retention;
CREATE VIEW vw_contract_retention AS
SELECT
    Contract_encoded,
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
GROUP BY Contract_encoded
ORDER BY Contract_encoded;

DROP VIEW IF EXISTS vw_clv_bands;
CREATE VIEW vw_clv_bands AS
SELECT
    CASE
        WHEN discounted_lifetime_value < 2500 THEN 'Low CLV (<2500)'
        WHEN discounted_lifetime_value < 4500 THEN 'Mid CLV (2500-4499)'
        ELSE 'High CLV (>=4500)'
    END AS clv_band,
    COUNT(*) AS customers,
    ROUND(100.0 * AVG(CASE WHEN Churn_encoded = 1 THEN 1.0 ELSE 0.0 END), 2) AS churn_rate_pct,
    ROUND(AVG(churn_risk_proxy), 4) AS avg_churn_risk_proxy
FROM customer_analytics
GROUP BY clv_band
ORDER BY customers DESC;

DROP VIEW IF EXISTS vw_top_risk_customers;
CREATE VIEW vw_top_risk_customers AS
SELECT
    customerID,
    segment_label,
    ROUND(churn_risk_proxy, 4) AS churn_risk_proxy,
    ROUND(discounted_lifetime_value, 2) AS discounted_lifetime_value,
    CASE
        WHEN is_month_to_month = 1 THEN 'Month-to-month risk'
        WHEN is_new_customer_0_6m = 1 THEN 'New-customer risk'
        WHEN is_electronic_check = 1 THEN 'Payment-method risk'
        ELSE 'Composite risk profile'
    END AS risk_reason
FROM customer_analytics
ORDER BY churn_risk_proxy DESC, discounted_lifetime_value DESC;