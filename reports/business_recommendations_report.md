# Business Recommendations Report
**Phase 13 – Customer Churn Analytics Platform**  
**Generated:** 2026-06-24  
**Data source:** `data/processed/churn_analytics.db`  
**Audience:** Executive leadership, Retention strategy team

---

## Executive Summary
Our telco customer base of **7,043 customers** is losing **19.1% annually to churn**, equating to approximately **1,342 departing customers** each cycle. At an average customer lifetime value of **$3,881.64**, this translates to **$5,209,161 of revenue at risk**.

The analysis identifies four high-leverage intervention zones:
1. **Contract type** — month-to-month customers churn at 36.2% vs 7.3% for two-year contracts (29.0pp gap).
2. **Payment method** — electronic check customers churn at 23.7% vs 16.6% for auto-pay (7.1pp gap).
3. **New customer onboarding** — customers in months 0–6 churn at 35.98% vs 12.62% for 48+ month tenured customers.
4. **Service bundling** — customers with no add-ons churn at 20.45% vs 37.5% for customers with maximum add-ons.

A targeted retention programme across all segments is projected to generate a **net ROI of $1,493,319** by saving approximately **402 customers** at a campaign cost of **$67,100**.

---

## Financial Impact Analysis

### Portfolio Overview

| Metric | Value |
|---|---|
| Total customers | 7,043 |
| Churned customers (current cycle) | 1,342 |
| Overall churn rate | 19.05% |
| Total portfolio CLV | $27,338,378.78 |
| Average customer CLV | $3,881.64 |
| Estimated CLV at risk | $5,209,161 |

### Retention Campaign ROI Estimate (Overall)

| Parameter | Value | Assumption |
|---|---|---|
| At-risk customers targeted | 1,342 | All churned customers |
| Estimated customers saved | 402 | 30% conversion rate |
| Gross revenue saved | $1,560,419 | Saved customers × avg CLV |
| Campaign cost | $67,100 | $50/customer |
| **Net ROI** | **$1,493,319** | Revenue saved − campaign cost |
| ROI % | 2225.5% | Net ROI / campaign cost |

---

## Segment-Level Recommendations

Four customer segments were identified via KMeans clustering. Recommendations are calibrated to each segment's churn rate, CLV, and behavioural profile.

### Low Engagement Churn Risk  —  [CRITICAL PRIORITY]

| Metric | Value |
|---|---|
| Customers | 1,981 |
| Churn rate | 35.4% |
| Avg discounted CLV | $3,418.38 |
| Avg retention leverage | $1,727.17 |
| At-risk customers (est.) | 701 |
| Estimated customers saved | 210 |
| Net ROI of retention campaign | $682,810 |

**Headline:** Urgent intervention within 30 days

**Recommended actions:**
- Proactive outbound call with personalised retention offer
- One-time discount (15–20%) tied to 12-month contract upgrade
- Assign dedicated account manager for top 20% by CLV
- Send NPS survey to identify specific dissatisfiers

**KPI target:** Reduce churn from 35.4% to < 22% within 6 months

### High Value Loyalists  —  [HIGH PRIORITY]

| Metric | Value |
|---|---|
| Customers | 1,470 |
| Churn rate | 21.4% |
| Avg discounted CLV | $3,894.74 |
| Avg retention leverage | $1,955.87 |
| At-risk customers (est.) | 315 |
| Estimated customers saved | 94 |
| Net ROI of retention campaign | $350,356 |

**Headline:** Protect high-CLV customers from month-to-month risk

**Recommended actions:**
- Introduce loyalty pricing tier for customers > 24 months tenure
- Offer contract lock-in bonus (free month, device upgrade credit)
- Proactive annual review call with retention specialist
- Priority support queue to reinforce premium experience

**KPI target:** Reduce churn from 21.4% to < 14% within 12 months

### At-Risk New Customers  —  [HIGH PRIORITY]

| Metric | Value |
|---|---|
| Customers | 1,736 |
| Churn rate | 11.3% |
| Avg discounted CLV | $3,490.21 |
| Avg retention leverage | $1,768.55 |
| At-risk customers (est.) | 195 |
| Estimated customers saved | 58 |
| Net ROI of retention campaign | $192,682 |

**Headline:** Structured 90-day onboarding to build stickiness

**Recommended actions:**
- Automated welcome journey: day 1, 7, 30, 60, 90 touchpoints
- Free 60-day trial of one premium add-on service
- Proactive check-in call at day 45 from customer success team
- Incentivise first 12-month contract with 10% first-year discount

**KPI target:** Reduce new-customer 6-month churn from 11.3% to < 7%

### Stable Value Seekers  —  [MEDIUM PRIORITY]

| Metric | Value |
|---|---|
| Customers | 1,856 |
| Churn rate | 7.0% |
| Avg discounted CLV | $4,731.84 |
| Avg retention leverage | $2,394.59 |
| At-risk customers (est.) | 129 |
| Estimated customers saved | 38 |
| Net ROI of retention campaign | $173,360 |

**Headline:** Upsell and upgrade to maximise CLV and lock-in

**Recommended actions:**
- Annual contract renewal campaign with loyalty reward
- Bundle upgrade promotion (internet + security + tech support)
- Satisfaction survey at contract anniversary with referral incentive
- Cross-sell premium tier for high monthly-charges customers

**KPI target:** Maintain churn below 10%; grow avg CLV by 8% via upsell

---

## Contract Migration Strategy

Contract type is the single strongest structural predictor of churn. A systematic migration programme from month-to-month to longer-term contracts will structurally reduce churn independent of other factors.

| Contract Type | Customers | Churn Rate | Avg CLV | CLV Gap vs 2-Year |
|---|---|---|---|---|
| Month-to-month | 2,331 | 36.2% | $3,459.11 | $-721.60 |
| One year | 2,376 | 13.8% | $4,002.12 | $-178.59 |
| Two year | 2,336 | 7.3% | $4,180.71 | $+0.00 |

**Recommended actions:**
1. **Contract upgrade incentive:** Offer month-to-month customers a 10% discount to switch to annual. Even capturing 15% of the 2,331 month-to-month customers would yield ~349 contract upgrades, each reducing their churn probability by ~29pp.
2. **Auto-renewal default:** Default new customer contracts to 12-month with easy opt-out, rather than defaulting to month-to-month.
3. **Two-year lock-in bonus:** Offer a free premium add-on for customers who commit to two years.

---

## Payment Method Optimisation

Electronic check is a leading behavioural indicator of churn risk. Transitioning customers to auto-pay reduces friction, improves payment reliability, and correlates with lower churn.

| Payment Method | Customers | Churn Rate |
|---|---|---|
| Electronic Check | 1,755 | 23.7% |
| Other | 1,803 | 19.4% |
| Auto-Pay | 3,485 | 16.6% |

**Recommended actions:**
- **Auto-pay incentive:** Offer a $5/month bill credit for customers who switch to auto-pay. At a 7.1pp churn reduction, the cost is justified within 2–3 months per customer.
- **Default payment method:** Set auto-pay as the recommended option during onboarding.
- **E-check flag in CRM:** Flag all electronic-check customers as elevated-risk and include in proactive outreach queues.

---

## New Customer Onboarding Programme

Customers in their first 6 months represent a critical at-risk window. Structured onboarding reduces early churn by building product familiarity and perceived value.

| Tenure Band | Customers | Churn Rate |
|---|---|---|
| 0-6 months | 642 | 36.0% |
| 6-24 months | 1,752 | 21.1% |
| 24-48 months | 2,184 | 19.7% |
| 48+ months | 2,465 | 12.6% |

**Recommended 90-day onboarding journey:**
| Day | Touchpoint | Channel | Owner |
|---|---|---|---|
| 1 | Welcome call + account setup confirmation | Phone | CS Rep |
| 7 | First bill explainer + FAQ email | Email | Automated |
| 30 | 30-day check-in; offer add-on trial | Phone/App | CS Rep |
| 45 | Mid-point satisfaction survey | Email/SMS | Automated |
| 60 | Contract upgrade offer (10% discount) | Email | Retention |
| 90 | 90-day loyalty reward; referral programme intro | Email/App | Marketing |

---

## Service Bundling & Add-on Strategy

Add-on count is inversely correlated with churn — each additional service increases switching cost and deepens product dependency. Security bundle customers are notably more loyal.

| Add-on Count | Customers | Churn Rate |
|---|---|---|
| 0 | 577 | 20.4% |
| 1 | 1,842 | 21.1% |
| 2 | 2,331 | 19.0% |
| 3 | 1,559 | 18.2% |
| 4 | 600 | 14.7% |
| 5 | 126 | 14.3% |
| 6 | 8 | 37.5% |

**Security bundle impact:** Customers with the security bundle churn at 18.32% vs 22.16% without — a significant stickiness signal.

**Recommended actions:**
- **First-add-on free:** For new customers with zero add-ons, offer one add-on free for 90 days.
- **Bundle promotion:** Package online security + tech support as a discounted bundle (target zero-addon customers first).
- **In-app upsell nudges:** Show contextual upsell prompts when customers approach their monthly data/service limits.

---

## Prioritised Action Plan

Recommendations ranked by estimated net ROI and implementation feasibility:

| Rank | Initiative | Segment / Group | Est. Net ROI | Timeline | Complexity |
|---|---|---|---|---|---|
| 1 | Urgent outreach to Low Engagement Churn Risk | Low Engagement Churn Risk | $682,810 | 0–30 days | Low |
| 2 | Contract upgrade incentive campaign | Month-to-month customers | $(see note) | 30–60 days | Low |
| 3 | Loyalty protection for High Value Loyalists | High Value Loyalists | $350,356 | 30–60 days | Medium |
| 4 | 90-day structured onboarding programme | At-Risk New Customers | $192,682 | 60–90 days | Medium |
| 5 | Auto-pay migration incentive ($5/month credit) | Electronic check payers | Ongoing savings | 60–90 days | Low |
| 6 | First-add-on free for zero-addon customers | All segments | CLV growth | 90–120 days | Low |
| 7 | Annual contract renewal / upsell campaign | Stable Value Seekers | $173,360 | 90–120 days | Medium |

---

## Predictive Model Deployment Recommendations

The trained Logistic Regression model (ROC AUC = 0.7609) provides individual-level churn probability scores. Deploying it operationally enables real-time intervention triggers.

**Recommended operational integrations:**
1. **CRM churn score field:** Push `churn_risk_proxy` score into the CRM for each customer; refresh weekly via batch scoring.
2. **Retention queue automation:** Automatically route customers with `churn_risk_proxy ≥ 2.0` to the retention outreach queue.
3. **Onboarding trigger:** Flag new customers at month 1 with month-to-month contract + electronic check + zero add-ons as `high_priority_onboarding`.
4. **Monthly churn forecast:** Run the model monthly on the full customer base; track predicted churn rate vs actual to monitor model drift.
5. **A/B testing framework:** Test retention offers against control groups; measure conversion using the churn label as the outcome variable.

---

## Success Metrics & KPI Targets

| KPI | Baseline (current) | 6-Month Target | 12-Month Target |
|---|---|---|---|
| Overall churn rate | 19.1% | < 15.0% | < 12.0% |
| Month-to-month churn rate | 36.2% | < 28.0% | < 22.0% |
| Low Engagement segment churn | 35.4% | < 26.0% | < 20.0% |
| New customer (0–6m) churn rate | 35.98% | < 8.0% | < 6.0% |
| E-check customer churn rate | 23.7% | < 25.0% | < 20.0% |
| Avg portfolio CLV | $3,882 | >$4,076 | >$4,347 |
| Auto-pay adoption rate | 49% | > 45% | > 55% |

---

*Report generated automatically by `src/utils/generate_recommendations.py` from live analytics data.*