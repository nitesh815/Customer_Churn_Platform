# Power BI Dashboard Blueprint
## Phase 12 – Customer Churn Analytics Platform

**Target tool:** Power BI Desktop (any version supporting SQLite ODBC or CSV import)  
**Audience:** Executives, retention managers, data analysts  
**Theme:** Dark professional (background: #1E2A38, accent: #00B4D8, alert: #E63946)  
**Date:** 2026-06-24

---

## Global Filters (Report-level slicers, visible on every page)

| Slicer | Field | Type | Default |
|---|---|---|---|
| Segment | `customer_analytics[segment_label]` | Dropdown | All |
| Contract Type | `customer_analytics[ContractLabel]` | Dropdown | All |
| CLV Band | `customer_analytics[CLV_Band]` | Dropdown | All |
| Churn Status | `customer_analytics[ChurnLabel]` | Toggle | All |

---

## Page 1 — Executive Overview

**Purpose:** One-screen snapshot for leadership. All KPIs visible without scrolling.

### KPI Cards (top row, equal-width)

| Card title | DAX Measure | Format |
|---|---|---|
| Total Customers | `[Total Customers]` | Integer |
| Overall Churn Rate | `[Churn Rate Label]` | Text (pre-formatted) |
| Portfolio CLV | `[Total CLV Label]` | Text (pre-formatted) |
| Customers at Risk | `[High Risk Customers]` | Integer |
| Revenue at Risk | `[CLV at Risk (Churned)]` | Currency `$#,##0` |

### Visuals (main canvas area)

**A. Churn Rate by Segment — Clustered Bar Chart**
- X-axis: `[Churn Rate %]`
- Y-axis: `vw_segment_kpis[segment_label]`
- Sort: descending by churn rate
- Color: conditional — red if > 25%, orange 15–25%, green < 15%
- Reference line: overall average 19.05%

**B. CLV by Segment — Bar Chart**
- X-axis: `vw_segment_kpis[avg_discounted_clv]`
- Y-axis: `vw_segment_kpis[segment_label]`
- Tooltips: customers count, retention leverage

**C. Churn vs Retention — Donut Chart**
- Values: `[Churned Customers]`, `[Retained Customers]`
- Colors: red / teal
- Center label: `[Churn Rate Label]`

**D. Summary KPI Table**
- Source: `vw_churn_overview`
- Show: all columns
- Use: at-a-glance validation card in bottom-right

**Interactions:** All visuals cross-filter. Bar click on a segment filters the donut and the table.

---

## Page 2 — Customer Segments

**Purpose:** Segment-level deep dive for retention planning.

### KPI Cards (filtered by global segment slicer)

| Card | Measure |
|---|---|
| Customers in Segment | `[Total Customers]` |
| Segment Churn Rate | `[Churn Rate Label]` |
| Avg CLV | `[Avg CLV Label]` |
| Avg Retention Leverage | `[CLV Retention Leverage Avg]` |

### Visuals

**A. Segment Size — Treemap**
- Category: `customer_analytics[segment_label]`
- Values: `[Total Customers]`
- Detail: `[Churn Rate %]` (tooltip)

**B. Segment KPI Comparison — Stacked Column Chart**
- X-axis: `vw_segment_kpis[segment_label]`
- Y-axis primary: `[Churn Rate %]`
- Y-axis secondary: `[Avg Discounted CLV]`
- Colors: segment palette (4 distinct hues)

**C. Retention Leverage vs Churn Rate — Scatter Plot**
- X-axis: `[Churn Rate %]`
- Y-axis: `[CLV Retention Leverage Avg]`
- Size: `[Total Customers]`
- Color: `customer_analytics[segment_label]`
- Annotation: quadrant lines at avg churn 19.05% and avg leverage

**D. Segment Characteristics — Matrix Table**
- Rows: `segment_label`
- Columns: `churn_rate_pct`, `avg_discounted_clv`, `avg_retention_leverage`, `customers`
- Source: `vw_segment_kpis`
- Conditional formatting: churn rate (red gradient), CLV (green gradient)

**E. Playbook Text Cards (one per segment)**
- Static text boxes with retention playbooks:
  - **High Value Loyalists (21.43% churn):** Proactive loyalty rewards; loyalty pricing lock-in; dedicated support tier
  - **Stable Value Seekers (7.00% churn):** Annual contract upgrade nudges; bundle upsell; satisfaction surveys
  - **At-Risk New Customers (11.29% churn):** 90-day onboarding journey; add-on trial offers; concierge setup
  - **Low Engagement Churn Risk (35.39% churn):** Urgent outreach within 30 days; discount offer; contract conversion incentive

---

## Page 3 — CLV & Revenue Analysis

**Purpose:** Financial impact of churn; prioritization by economic value.

### KPI Cards

| Card | Measure |
|---|---|
| Total Portfolio CLV | `[Total Portfolio CLV]` |
| CLV at Risk | `[CLV at Risk (Churned)]` |
| High CLV Customers | `[High CLV Customers]` |
| High CLV % | `[High CLV %]` |

### Visuals

**A. CLV Band Distribution — Clustered Bar**
- X-axis: `vw_clv_bands[clv_band]`
- Y-axis group 1: `vw_clv_bands[customers]`
- Y-axis group 2: `vw_clv_bands[churn_rate_pct]` (secondary axis)
- Sort: CLV band descending (High → Mid → Low)

**B. CLV Distribution Histogram — Area Chart**
- X-axis: `discounted_lifetime_value` (binned into $500 buckets)
- Y-axis: count of customers
- Overlay: churned customers as separate series (filled red)
- Source: `customer_analytics`

**C. CLV Percentile vs Churn Risk — Scatter Plot**
- X-axis: `customer_analytics[clv_percentile]`
- Y-axis: `customer_analytics[churn_risk_proxy]`
- Color: `customer_analytics[ChurnLabel]`
- Reference quadrant lines: percentile 50, risk proxy = 0
- Tooltip: `customerID`, `segment_label`, `discounted_lifetime_value`

**D. Revenue at Risk by Contract — Stacked Bar**
- X-axis: `vw_contract_retention[contract_type]`
- Y-axis: `[CLV at Risk (Churned)]`
- Color segments: churned / retained
- Tooltip: churn rate %, customer count

---

## Page 4 — Churn Drivers & Contract Analysis

**Purpose:** Root-cause breakdown of churn by contract, payment, and service factors.

### KPI Cards

| Card | Measure |
|---|---|
| Month-to-Month Churn Rate | `[Month-to-Month Churn Rate %]` |
| Two-Year Churn Rate | `[Two Year Contract Churn Rate %]` |
| E-Check Churn Rate | `[E-Check Churn Rate %]` |
| New Customer Churn Rate | `[New Customer Churn Rate %]` |

### Visuals

**A. Churn by Contract Type — 100% Stacked Bar**
- X-axis: `vw_contract_retention[contract_type]`
- Y-axis: percentage churned / retained
- Color: Churned (red) / Retained (teal)
- Data labels: churn rate %
- Source: `vw_contract_retention`

**B. Churn by Tenure Band — Bar Chart**
- X-axis: `customer_analytics[TenureBand]`
- Y-axis: `[Churn Rate %]`
- Sort: logical order (0–6, 6–24, 24–48, 48+)

**C. Churn by Add-on Count — Line Chart**
- X-axis: `customer_analytics[addon_count]` (0–5)
- Y-axis: `[Churn Rate %]`
- Title: "More services → lower churn"

**D. Feature Importance — Horizontal Bar Chart**
- Static data (paste from `reports/feature_explanations.csv`):

| Feature | Importance |
|---|---|
| churn_risk_proxy | 0.0280 |
| is_month_to_month | 0.0210 |
| Contract_encoded | 0.0130 |
| is_auto_pay | 0.0070 |
| security_bundle | 0.0060 |
| addon_count | 0.0050 |

- Source: `reports/feature_explanations.csv` (imported as separate table, no relationship)
- Sort: descending by importance
- Color: gradient from dark blue (low) to bright cyan (high)

**E. Payment Method Comparison — Matrix**
- Rows: `is_auto_pay`, `is_electronic_check` (expand to labels via calculated column)
- Columns: `customers`, `churn_rate_pct`, `avg_discounted_clv`

---

## Page 5 — At-Risk Customer Watchlist

**Purpose:** Actionable intervention list for retention managers.

### KPI Cards

| Card | Measure |
|---|---|
| Critical Risk Customers | `[Critical Risk Customers]` |
| High Risk % | `[High Risk %]` |
| Avg Risk Score | `[Avg Churn Risk Proxy]` |

### Visuals

**A. Top Risk Customers — Table (scrollable)**
- Source: `vw_top_risk_customers`
- Columns: `customerID`, `segment_label`, `churn_risk_proxy`, `discounted_lifetime_value`, `risk_reason`
- Conditional formatting:
  - `churn_risk_proxy` ≥ 5.0 → red background
  - `churn_risk_proxy` 4.0–4.9 → orange background
  - `discounted_lifetime_value` ≥ 4000 → bold font
- Sort: `churn_risk_proxy` descending

**B. Risk Score Distribution — Histogram**
- X-axis: `churn_risk_proxy` (binned into 0.5 increments)
- Y-axis: customer count
- Color: red for bins ≥ 2.0, grey for low-risk bins

**C. Risk vs CLV Matrix — Scatter Plot**
- X-axis: `customer_analytics[churn_risk_proxy]`
- Y-axis: `customer_analytics[discounted_lifetime_value]`
- Color: `customer_analytics[segment_label]`
- Quadrant annotation:
  - Top-right: "Priority 1 — Retain urgently" (high CLV, high risk)
  - Bottom-right: "Priority 2 — Evaluate ROI" (low CLV, high risk)
  - Top-left: "Monitor" (high CLV, low risk)
  - Bottom-left: "Low priority" (low CLV, low risk)
- Tooltip: `customerID`, `risk_reason`, `contract_type`

**D. Segment Breakdown of At-Risk Customers — Donut**
- Category: `segment_label` (filtered to `churn_risk_proxy >= 2`)
- Values: count
- Colors: segment palette

---

## Page 6 — ML Model Insights

**Purpose:** Model validation and feature contribution for data-savvy users.

### KPI Cards

| Card | Value (static from model run) |
|---|---|
| Best Model | Logistic Regression |
| ROC AUC | 0.7609 |
| Runner-up (RF AUC) | 0.7458 |
| Features Used | 52 |

### Visuals

**A. Model Comparison — Bar Chart (static data)**

| Model | AUC |
|---|---|
| Logistic Regression | 0.7609 |
| Random Forest | 0.7458 |

**B. Feature Importance — Horizontal Bar (same as Page 4-D)**
- Source: `reports/feature_explanations.csv` (imported)

**C. Explanation Stability — Line Chart**
- Source: `reports/explanation_stability.csv`
- X-axis: feature name (top 10)
- Y-axis: importance value
- Series: seed_1, seed_2, seed_3 (3 lines)
- Purpose: shows importance scores are stable across random seeds

**D. Local Reason Codes Sample — Table**
- Source: `reports/local_reason_codes.csv` (first 20 rows imported)
- Columns: `customerID`, top 3 contributing feature columns
- Filter: show only churned customers

---

## Design Notes

### Color Palette
| Usage | Hex |
|---|---|
| Page background | #1E2A38 |
| Card background | #243447 |
| Primary accent | #00B4D8 |
| Alert / churn | #E63946 |
| Positive / retained | #06D6A0 |
| Neutral | #8D99AE |
| Segment A (High Value Loyalists) | #F4A261 |
| Segment B (Stable Value Seekers) | #06D6A0 |
| Segment C (At-Risk New Customers) | #FFB703 |
| Segment D (Low Engagement Churn Risk) | #E63946 |

### Typography
- Title font: Segoe UI Semibold, 16pt, white
- Card value: Segoe UI Bold, 24pt, white
- Card subtitle: Segoe UI, 10pt, #8D99AE
- Table: Segoe UI, 10pt

### Navigation
- Add page navigator buttons (rectangles with page icons) in the top-right of every page.
- Label: Overview | Segments | CLV | Drivers | Watchlist | ML Insights

### Refresh / Data Lineage
- Source file: `data/processed/churn_analytics.db` or `data/processed/telco_customer_churn_clv.csv`
- Refresh triggers: run `src/utils/build_sql_analytics_layer.py` → then refresh Power BI dataset
- Report last refreshed: shown in footer via DAX `[Last Refresh] = NOW()`
