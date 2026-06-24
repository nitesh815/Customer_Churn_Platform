# Power BI Data Model Specification
## Phase 12 – Customer Churn Analytics Platform

**Source:** `data/processed/churn_analytics.db` (SQLite)  
**Connection mode:** Import (full table + views imported on refresh)  
**Date generated:** 2026-06-24

---

## 1. Data Source Connection

| Setting | Value |
|---|---|
| Source type | ODBC → SQLite3 ODBC Driver |
| Database file | `data/processed/churn_analytics.db` (absolute path on local machine) |
| Alternative | Import from CSV: `data/processed/telco_customer_churn_clv.csv` (66 columns, all features + CLV) |
| Refresh mode | Manual (static dataset) |

### Import steps in Power BI Desktop
1. **Get Data → ODBC** → Select SQLite3 driver → point to `churn_analytics.db`
2. Select all five views: `vw_churn_overview`, `vw_segment_kpis`, `vw_contract_retention`, `vw_clv_bands`, `vw_top_risk_customers`
3. Select base table: `customer_analytics`
4. Load all six objects. Do **not** create relationships between the summary views — they are flat aggregations.

---

## 2. Table Inventory

| Table / View | Row Count | Purpose |
|---|---|---|
| `customer_analytics` | 7,043 | Base fact table — one row per customer, all features |
| `vw_churn_overview` | 1 | Global KPI summary (churn rate, avg CLV, total CLV) |
| `vw_segment_kpis` | 4 | Per-segment KPIs (churn rate, CLV, retention leverage) |
| `vw_contract_retention` | 3 | Per-contract-type churn and CLV |
| `vw_clv_bands` | 3 | High / Mid / Low CLV band comparison |
| `vw_top_risk_customers` | 10 | Top 10 customers by churn risk score |

---

## 3. Base Fact Table Schema — `customer_analytics`

All columns inherited from `telco_customer_churn_clv.csv`. Key columns for dashboard measures:

### Identity
| Column | Type | Description |
|---|---|---|
| `customerID` | Text | Unique customer identifier (e.g. ID-000354) |

### Target
| Column | Type | Description |
|---|---|---|
| `Churn_encoded` | Integer (0/1) | 1 = churned, 0 = retained |

### Demographic & Service
| Column | Type | Description |
|---|---|---|
| `tenure_normalized` | Decimal [0-1] | Normalized tenure (0=new, 1=72+ months) |
| `MonthlyCharges_normalized` | Decimal [0-1] | Normalized monthly charges |
| `TotalCharges_normalized` | Decimal [0-1] | Normalized total charges |
| `Contract_encoded` | Integer | 0=Month-to-month, 1=One year, 2=Two year |
| `is_senior_citizen` | Integer (0/1) | Senior citizen indicator |

### Engineered Features (Phase 6)
| Column | Type | Description |
|---|---|---|
| `is_new_customer_0_6m` | Integer (0/1) | Tenure ≤ 6 months |
| `is_mid_tenure_6_24m` | Integer (0/1) | Tenure 6–24 months |
| `is_long_tenure_48m` | Integer (0/1) | Tenure ≥ 48 months |
| `is_month_to_month` | Integer (0/1) | Month-to-month contract flag |
| `is_auto_pay` | Integer (0/1) | Auto-pay payment method |
| `is_electronic_check` | Integer (0/1) | Electronic check payment method |
| `addon_count` | Integer [0-5] | Number of add-on services subscribed |
| `security_bundle` | Integer (0/1) | Has both online security + tech support |
| `churn_risk_proxy` | Decimal | Composite churn risk score (higher = riskier) |

### CLV Features (Phase 8)
| Column | Type | Description |
|---|---|---|
| `monthly_value_score` | Decimal | Estimated monthly revenue contribution |
| `projected_lifetime_months` | Decimal | Estimated remaining tenure |
| `discounted_lifetime_value` | Decimal | Discounted CLV in $ |
| `retention_leverage_score` | Decimal | Potential CLV saved by retaining customer |
| `clv_percentile` | Decimal [0-100] | Customer percentile rank by CLV |

### Segmentation (Phase 7)
| Column | Type | Description |
|---|---|---|
| `segment_id` | Integer [0-3] | KMeans cluster ID |
| `segment_label` | Text | Human-readable segment name |

---

## 4. View Schemas

### `vw_churn_overview` (1 row)
| Column | Type |
|---|---|
| `customers` | Integer |
| `churned_customers` | Integer |
| `churn_rate_pct` | Decimal |
| `avg_discounted_clv` | Decimal |
| `total_discounted_clv` | Decimal |

### `vw_segment_kpis` (4 rows)
| Column | Type |
|---|---|
| `segment_label` | Text |
| `customers` | Integer |
| `churn_rate_pct` | Decimal |
| `avg_monthly_charges_norm` | Decimal |
| `avg_discounted_clv` | Decimal |
| `avg_retention_leverage` | Decimal |

### `vw_contract_retention` (3 rows)
| Column | Type |
|---|---|
| `Contract_encoded` | Integer |
| `contract_type` | Text |
| `customers` | Integer |
| `churn_rate_pct` | Decimal |
| `avg_discounted_clv` | Decimal |

### `vw_clv_bands` (3 rows)
| Column | Type |
|---|---|
| `clv_band` | Text |
| `customers` | Integer |
| `churn_rate_pct` | Decimal |
| `avg_churn_risk_proxy` | Decimal |

### `vw_top_risk_customers` (10 rows)
| Column | Type |
|---|---|
| `customerID` | Text |
| `segment_label` | Text |
| `churn_risk_proxy` | Decimal |
| `discounted_lifetime_value` | Decimal |
| `risk_reason` | Text |

---

## 5. Relationships

| From table | Column | To table | Column | Cardinality | Active |
|---|---|---|---|---|---|
| `customer_analytics` | `segment_label` | `vw_segment_kpis` | `segment_label` | Many-to-one | Yes |
| `customer_analytics` | `Contract_encoded` | `vw_contract_retention` | `Contract_encoded` | Many-to-one | Yes |

> **Note:** `vw_churn_overview`, `vw_clv_bands`, and `vw_top_risk_customers` are standalone; connect them to `customer_analytics` only if drill-through is needed. Prefer using DAX measures on `customer_analytics` directly for all KPI cards.

---

## 6. Calculated Columns (add in Power Query / Power BI)

These columns are derived in M (Power Query) for display clarity:

```m
// Expand contract label
ContractLabel = if [Contract_encoded] = 0 then "Month-to-month"
                else if [Contract_encoded] = 1 then "One year"
                else "Two year"

// CLV Band bucketing (mirrors SQL view)
CLV_Band = if [discounted_lifetime_value] >= 4500 then "High CLV (>=4500)"
           else if [discounted_lifetime_value] >= 2500 then "Mid CLV (2500-4499)"
           else "Low CLV (<2500)"

// Churn label for slicers
ChurnLabel = if [Churn_encoded] = 1 then "Churned" else "Retained"

// Tenure band (6-month buckets)
TenureBand = if [is_new_customer_0_6m] = 1 then "0-6 months"
             else if [is_mid_tenure_6_24m] = 1 then "6-24 months"
             else if [is_long_tenure_48m] = 1 then "48+ months"
             else "24-48 months"
```

---

## 7. Known Values (live query results — Phase 11)

| KPI | Value |
|---|---|
| Total customers | 7,043 |
| Churned | 1,342 |
| Overall churn rate | 19.05% |
| Total portfolio CLV | $27,338,378.78 |
| Avg discounted CLV | $3,881.64 |
| High CLV (≥4500) churn rate | 15.70% |
| Month-to-month churn rate | 36.25% |
| Two-year contract churn rate | 7.28% |
| Highest churn segment | Low Engagement Churn Risk (35.39%) |
| Lowest churn segment | Stable Value Seekers (7.00%) |
