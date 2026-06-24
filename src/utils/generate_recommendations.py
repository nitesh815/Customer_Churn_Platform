"""
Phase 13: Business Recommendations Generator
Customer Churn Prediction & Analytics Platform

Queries the SQLite analytics layer and synthesizes data-driven business
recommendations with ROI estimates and segment-specific action plans.
"""

import sqlite3
import csv
import os
from datetime import date


DB_PATH = "data/processed/churn_analytics.db"
REPORT_PATH = "reports/business_recommendations_report.md"

# Retention intervention cost and discount assumptions
INTERVENTION_COST_PER_CUSTOMER = 50      # $ per outreach/offer
RETENTION_SUCCESS_RATE = 0.30            # 30% of at-risk customers saved
AVG_MONTHLY_REVENUE = 65.0               # $ average monthly charge proxy
MONTHLY_DISCOUNT_RATE = 0.01             # 1% monthly (12% annual)


# ─────────────────────────────────────────────
#  DATA RETRIEVAL
# ─────────────────────────────────────────────

def load_analytics(db_path: str) -> dict:
    """Query all analytics views and return a dict of results."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    def q(sql):
        return [dict(r) for r in conn.execute(sql).fetchall()]

    data = {}

    data["overview"] = q("SELECT * FROM vw_churn_overview")[0]
    data["segments"] = q("SELECT * FROM vw_segment_kpis ORDER BY churn_rate_pct DESC")
    data["contracts"] = q("SELECT * FROM vw_contract_retention ORDER BY Contract_encoded")
    data["clv_bands"] = q("SELECT * FROM vw_clv_bands")
    data["top_risk"] = q("SELECT * FROM vw_top_risk_customers")

    # Payment method churn rates from base table
    data["payment"] = q("""
        SELECT
            CASE WHEN is_electronic_check = 1 THEN 'Electronic Check'
                 WHEN is_auto_pay = 1          THEN 'Auto-Pay'
                 ELSE 'Other'
            END AS payment_method,
            COUNT(*) AS customers,
            ROUND(100.0 * AVG(CAST(Churn_encoded AS REAL)), 2) AS churn_rate_pct
        FROM customer_analytics
        GROUP BY payment_method
        ORDER BY churn_rate_pct DESC
    """)

    # Tenure band churn rates (derived from available flags + normalized tenure)
    # tenure_normalized: 0=new, 1=72+ months; 6m ~= 0.083, 24m ~= 0.33, 48m ~= 0.67
    data["tenure"] = q("""
        SELECT
            CASE WHEN is_new_customer_0_6m = 1  THEN '0-6 months'
                 WHEN is_long_tenure_48m   = 1  THEN '48+ months'
                 WHEN tenure_normalized    < 0.34 THEN '6-24 months'
                 ELSE '24-48 months'
            END AS tenure_band,
            COUNT(*) AS customers,
            ROUND(100.0 * AVG(CAST(Churn_encoded AS REAL)), 2) AS churn_rate_pct
        FROM customer_analytics
        GROUP BY tenure_band
        ORDER BY churn_rate_pct DESC
    """)

    # Add-on count vs churn
    data["addons"] = q("""
        SELECT
            addon_count,
            COUNT(*) AS customers,
            ROUND(100.0 * AVG(CAST(Churn_encoded AS REAL)), 2) AS churn_rate_pct
        FROM customer_analytics
        GROUP BY addon_count
        ORDER BY addon_count
    """)

    # Security bundle impact
    data["security"] = q("""
        SELECT
            security_bundle,
            COUNT(*) AS customers,
            ROUND(100.0 * AVG(CAST(Churn_encoded AS REAL)), 2) AS churn_rate_pct
        FROM customer_analytics
        GROUP BY security_bundle
        ORDER BY security_bundle
    """)

    conn.close()
    return data


# ─────────────────────────────────────────────
#  ROI CALCULATIONS
# ─────────────────────────────────────────────

def calculate_roi(n_at_risk: int, avg_clv: float) -> dict:
    """Estimate ROI for a targeted retention campaign."""
    customers_saved = int(n_at_risk * RETENTION_SUCCESS_RATE)
    revenue_saved = customers_saved * avg_clv
    campaign_cost = n_at_risk * INTERVENTION_COST_PER_CUSTOMER
    net_roi = revenue_saved - campaign_cost
    roi_pct = (net_roi / campaign_cost * 100) if campaign_cost > 0 else 0
    return {
        "n_at_risk": n_at_risk,
        "customers_saved": customers_saved,
        "revenue_saved": revenue_saved,
        "campaign_cost": campaign_cost,
        "net_roi": net_roi,
        "roi_pct": roi_pct,
    }


# ─────────────────────────────────────────────
#  REPORT BUILDER
# ─────────────────────────────────────────────

def build_report(data: dict, report_path: str):
    ov = data["overview"]
    total = ov["customers"]
    churned = ov["churned_customers"]
    churn_rate = ov["churn_rate_pct"]
    total_clv = ov["total_discounted_clv"]
    avg_clv = ov["avg_discounted_clv"]

    # Revenue at risk = CLV of churned customers (rough estimate)
    clv_at_risk = churned * avg_clv

    # Contract delta
    mtm = next(c for c in data["contracts"] if c["Contract_encoded"] == 0)
    two_yr = next(c for c in data["contracts"] if c["Contract_encoded"] == 2)
    contract_churn_gap = mtm["churn_rate_pct"] - two_yr["churn_rate_pct"]

    # High-risk segment
    high_risk_seg = data["segments"][0]  # sorted desc by churn rate

    # Payment
    echeck = next((p for p in data["payment"] if p["payment_method"] == "Electronic Check"), None)
    autopay = next((p for p in data["payment"] if p["payment_method"] == "Auto-Pay"), None)
    pay_gap = (echeck["churn_rate_pct"] - autopay["churn_rate_pct"]) if echeck and autopay else 0

    # Tenure: new customers at highest risk
    new_cust = next((t for t in data["tenure"] if t["tenure_band"] == "0-6 months"), {})
    long_cust = next((t for t in data["tenure"] if t["tenure_band"] == "48+ months"), {})

    # Addons: zero vs max
    zero_addon = next((a for a in data["addons"] if a["addon_count"] == 0), {})
    max_addon = data["addons"][-1] if data["addons"] else {}

    # Security bundle
    no_bundle = next((s for s in data["security"] if s["security_bundle"] == 0), {})
    has_bundle = next((s for s in data["security"] if s["security_bundle"] == 1), {})

    # Segment ROIs
    seg_rois = {}
    for seg in data["segments"]:
        at_risk = int(seg["customers"] * seg["churn_rate_pct"] / 100)
        seg_rois[seg["segment_label"]] = calculate_roi(at_risk, seg["avg_discounted_clv"])

    # Overall ROI
    overall_roi = calculate_roi(churned, avg_clv)

    lines = []

    def h1(t): lines.append(f"# {t}")
    def h2(t): lines.append(f"\n## {t}")
    def h3(t): lines.append(f"\n### {t}")
    def p(t=""): lines.append(t)
    def table_row(*cols): lines.append("| " + " | ".join(str(c) for c in cols) + " |")
    def table_sep(*cols): lines.append("|" + "|".join("---" for _ in cols) + "|")

    today = date.today().isoformat()

    # ── Header ──
    h1("Business Recommendations Report")
    p(f"**Phase 13 – Customer Churn Analytics Platform**  ")
    p(f"**Generated:** {today}  ")
    p(f"**Data source:** `data/processed/churn_analytics.db`  ")
    p(f"**Audience:** Executive leadership, Retention strategy team")

    p()
    p("---")

    # ── Executive Summary ──
    h2("Executive Summary")
    p(f"Our telco customer base of **{total:,} customers** is losing **{churn_rate:.1f}% annually to churn**, "
      f"equating to approximately **{churned:,} departing customers** each cycle. "
      f"At an average customer lifetime value of **${avg_clv:,.2f}**, this translates to "
      f"**${clv_at_risk:,.0f} of revenue at risk**.")
    p()
    p(f"The analysis identifies four high-leverage intervention zones:")
    p(f"1. **Contract type** — month-to-month customers churn at {mtm['churn_rate_pct']:.1f}% vs {two_yr['churn_rate_pct']:.1f}% for two-year contracts ({contract_churn_gap:.1f}pp gap).")
    p(f"2. **Payment method** — electronic check customers churn at {echeck['churn_rate_pct']:.1f}% vs {autopay['churn_rate_pct']:.1f}% for auto-pay ({pay_gap:.1f}pp gap).")
    p(f"3. **New customer onboarding** — customers in months 0–6 churn at {new_cust.get('churn_rate_pct', 'N/A')}% vs {long_cust.get('churn_rate_pct', 'N/A')}% for 48+ month tenured customers.")
    p(f"4. **Service bundling** — customers with no add-ons churn at {zero_addon.get('churn_rate_pct', 'N/A')}% vs {max_addon.get('churn_rate_pct', 'N/A')}% for customers with maximum add-ons.")
    p()
    p(f"A targeted retention programme across all segments is projected to generate a "
      f"**net ROI of ${overall_roi['net_roi']:,.0f}** by saving approximately "
      f"**{overall_roi['customers_saved']:,} customers** at a campaign cost of "
      f"**${overall_roi['campaign_cost']:,.0f}**.")

    p()
    p("---")

    # ── Financial Impact ──
    h2("Financial Impact Analysis")

    h3("Portfolio Overview")
    p()
    table_row("Metric", "Value")
    table_sep("Metric", "Value")
    table_row("Total customers", f"{total:,}")
    table_row("Churned customers (current cycle)", f"{churned:,}")
    table_row("Overall churn rate", f"{churn_rate:.2f}%")
    table_row("Total portfolio CLV", f"${total_clv:,.2f}")
    table_row("Average customer CLV", f"${avg_clv:,.2f}")
    table_row("Estimated CLV at risk", f"${clv_at_risk:,.0f}")

    h3("Retention Campaign ROI Estimate (Overall)")
    roi = overall_roi
    p()
    table_row("Parameter", "Value", "Assumption")
    table_sep("Parameter", "Value", "Assumption")
    table_row("At-risk customers targeted", f"{roi['n_at_risk']:,}", "All churned customers")
    table_row("Estimated customers saved", f"{roi['customers_saved']:,}", f"{RETENTION_SUCCESS_RATE*100:.0f}% conversion rate")
    table_row("Gross revenue saved", f"${roi['revenue_saved']:,.0f}", "Saved customers × avg CLV")
    table_row("Campaign cost", f"${roi['campaign_cost']:,.0f}", f"${INTERVENTION_COST_PER_CUSTOMER}/customer")
    table_row("**Net ROI**", f"**${roi['net_roi']:,.0f}**", "Revenue saved − campaign cost")
    table_row("ROI %", f"{roi['roi_pct']:.1f}%", "Net ROI / campaign cost")

    p()
    p("---")

    # ── Segment Recommendations ──
    h2("Segment-Level Recommendations")
    p()
    p("Four customer segments were identified via KMeans clustering. Recommendations are "
      "calibrated to each segment's churn rate, CLV, and behavioural profile.")

    seg_playbooks = {
        "Low Engagement Churn Risk": {
            "priority": "CRITICAL",
            "headline": "Urgent intervention within 30 days",
            "actions": [
                "Proactive outbound call with personalised retention offer",
                "One-time discount (15–20%) tied to 12-month contract upgrade",
                "Assign dedicated account manager for top 20% by CLV",
                "Send NPS survey to identify specific dissatisfiers",
            ],
            "kpi_target": "Reduce churn from 35.4% to < 22% within 6 months",
        },
        "High Value Loyalists": {
            "priority": "HIGH",
            "headline": "Protect high-CLV customers from month-to-month risk",
            "actions": [
                "Introduce loyalty pricing tier for customers > 24 months tenure",
                "Offer contract lock-in bonus (free month, device upgrade credit)",
                "Proactive annual review call with retention specialist",
                "Priority support queue to reinforce premium experience",
            ],
            "kpi_target": "Reduce churn from 21.4% to < 14% within 12 months",
        },
        "At-Risk New Customers": {
            "priority": "HIGH",
            "headline": "Structured 90-day onboarding to build stickiness",
            "actions": [
                "Automated welcome journey: day 1, 7, 30, 60, 90 touchpoints",
                "Free 60-day trial of one premium add-on service",
                "Proactive check-in call at day 45 from customer success team",
                "Incentivise first 12-month contract with 10% first-year discount",
            ],
            "kpi_target": "Reduce new-customer 6-month churn from 11.3% to < 7%",
        },
        "Stable Value Seekers": {
            "priority": "MEDIUM",
            "headline": "Upsell and upgrade to maximise CLV and lock-in",
            "actions": [
                "Annual contract renewal campaign with loyalty reward",
                "Bundle upgrade promotion (internet + security + tech support)",
                "Satisfaction survey at contract anniversary with referral incentive",
                "Cross-sell premium tier for high monthly-charges customers",
            ],
            "kpi_target": "Maintain churn below 10%; grow avg CLV by 8% via upsell",
        },
    }

    for seg in data["segments"]:
        label = seg["segment_label"]
        roi = seg_rois[label]
        pb = seg_playbooks.get(label, {})

        h3(f"{label}  —  [{pb.get('priority', 'MEDIUM')} PRIORITY]")
        p()
        table_row("Metric", "Value")
        table_sep("Metric", "Value")
        table_row("Customers", f"{seg['customers']:,}")
        table_row("Churn rate", f"{seg['churn_rate_pct']:.1f}%")
        table_row("Avg discounted CLV", f"${seg['avg_discounted_clv']:,.2f}")
        table_row("Avg retention leverage", f"${seg['avg_retention_leverage']:,.2f}")
        table_row("At-risk customers (est.)", f"{roi['n_at_risk']:,}")
        table_row("Estimated customers saved", f"{roi['customers_saved']:,}")
        table_row("Net ROI of retention campaign", f"${roi['net_roi']:,.0f}")

        p()
        p(f"**Headline:** {pb.get('headline', '')}")
        p()
        p("**Recommended actions:**")
        for action in pb.get("actions", []):
            p(f"- {action}")
        p()
        p(f"**KPI target:** {pb.get('kpi_target', '')}")

    p()
    p("---")

    # ── Contract Strategy ──
    h2("Contract Migration Strategy")
    p()
    p("Contract type is the single strongest structural predictor of churn. "
      "A systematic migration programme from month-to-month to longer-term contracts "
      "will structurally reduce churn independent of other factors.")
    p()
    table_row("Contract Type", "Customers", "Churn Rate", "Avg CLV", "CLV Gap vs 2-Year")
    table_sep("Contract Type", "Customers", "Churn Rate", "Avg CLV", "CLV Gap vs 2-Year")
    for c in data["contracts"]:
        gap = c["avg_discounted_clv"] - two_yr["avg_discounted_clv"]
        gap_str = f"${gap:+,.2f}"
        table_row(c["contract_type"], f"{c['customers']:,}", f"{c['churn_rate_pct']:.1f}%",
                  f"${c['avg_discounted_clv']:,.2f}", gap_str)

    p()
    p("**Recommended actions:**")
    p(f"1. **Contract upgrade incentive:** Offer month-to-month customers a 10% discount to switch to annual. "
      f"Even capturing 15% of the {mtm['customers']:,} month-to-month customers would yield "
      f"~{int(mtm['customers'] * 0.15):,} contract upgrades, each reducing their churn probability by ~{contract_churn_gap:.0f}pp.")
    p("2. **Auto-renewal default:** Default new customer contracts to 12-month with easy opt-out, "
      "rather than defaulting to month-to-month.")
    p("3. **Two-year lock-in bonus:** Offer a free premium add-on for customers who commit to two years.")

    p()
    p("---")

    # ── Payment Method ──
    h2("Payment Method Optimisation")
    p()
    p("Electronic check is a leading behavioural indicator of churn risk. "
      "Transitioning customers to auto-pay reduces friction, improves payment reliability, "
      "and correlates with lower churn.")
    p()
    table_row("Payment Method", "Customers", "Churn Rate")
    table_sep("Payment Method", "Customers", "Churn Rate")
    for pm in data["payment"]:
        table_row(pm["payment_method"], f"{pm['customers']:,}", f"{pm['churn_rate_pct']:.1f}%")

    p()
    p("**Recommended actions:**")
    p(f"- **Auto-pay incentive:** Offer a $5/month bill credit for customers who switch to auto-pay. "
      f"At a {pay_gap:.1f}pp churn reduction, the cost is justified within 2–3 months per customer.")
    p("- **Default payment method:** Set auto-pay as the recommended option during onboarding.")
    p("- **E-check flag in CRM:** Flag all electronic-check customers as elevated-risk and include in "
      "proactive outreach queues.")

    p()
    p("---")

    # ── Onboarding ──
    h2("New Customer Onboarding Programme")
    p()
    p("Customers in their first 6 months represent a critical at-risk window. "
      "Structured onboarding reduces early churn by building product familiarity and perceived value.")
    p()
    table_row("Tenure Band", "Customers", "Churn Rate")
    table_sep("Tenure Band", "Customers", "Churn Rate")
    for t in data["tenure"]:
        table_row(t["tenure_band"], f"{t['customers']:,}", f"{t['churn_rate_pct']:.1f}%")

    p()
    p("**Recommended 90-day onboarding journey:**")
    p("| Day | Touchpoint | Channel | Owner |")
    p("|---|---|---|---|")
    p("| 1 | Welcome call + account setup confirmation | Phone | CS Rep |")
    p("| 7 | First bill explainer + FAQ email | Email | Automated |")
    p("| 30 | 30-day check-in; offer add-on trial | Phone/App | CS Rep |")
    p("| 45 | Mid-point satisfaction survey | Email/SMS | Automated |")
    p("| 60 | Contract upgrade offer (10% discount) | Email | Retention |")
    p("| 90 | 90-day loyalty reward; referral programme intro | Email/App | Marketing |")

    p()
    p("---")

    # ── Service Bundling ──
    h2("Service Bundling & Add-on Strategy")
    p()
    p("Add-on count is inversely correlated with churn — each additional service increases switching "
      "cost and deepens product dependency. Security bundle customers are notably more loyal.")
    p()
    table_row("Add-on Count", "Customers", "Churn Rate")
    table_sep("Add-on Count", "Customers", "Churn Rate")
    for a in data["addons"]:
        table_row(a["addon_count"], f"{a['customers']:,}", f"{a['churn_rate_pct']:.1f}%")

    p()
    bundle_no = no_bundle.get("churn_rate_pct", "N/A")
    bundle_yes = has_bundle.get("churn_rate_pct", "N/A")
    p(f"**Security bundle impact:** Customers with the security bundle churn at {bundle_yes}% "
      f"vs {bundle_no}% without — a significant stickiness signal.")
    p()
    p("**Recommended actions:**")
    p("- **First-add-on free:** For new customers with zero add-ons, offer one add-on free for 90 days.")
    p("- **Bundle promotion:** Package online security + tech support as a discounted bundle "
      "(target zero-addon customers first).")
    p("- **In-app upsell nudges:** Show contextual upsell prompts when customers approach their "
      "monthly data/service limits.")

    p()
    p("---")

    # ── Prioritised Action Plan ──
    h2("Prioritised Action Plan")
    p()
    p("Recommendations ranked by estimated net ROI and implementation feasibility:")
    p()
    table_row("Rank", "Initiative", "Segment / Group", "Est. Net ROI", "Timeline", "Complexity")
    table_sep("Rank", "Initiative", "Segment / Group", "Est. Net ROI", "Timeline", "Complexity")
    table_row("1", "Urgent outreach to Low Engagement Churn Risk",
              "Low Engagement Churn Risk",
              f"${seg_rois['Low Engagement Churn Risk']['net_roi']:,.0f}", "0–30 days", "Low")
    table_row("2", "Contract upgrade incentive campaign",
              "Month-to-month customers",
              "$(see note)", "30–60 days", "Low")
    table_row("3", "Loyalty protection for High Value Loyalists",
              "High Value Loyalists",
              f"${seg_rois['High Value Loyalists']['net_roi']:,.0f}", "30–60 days", "Medium")
    table_row("4", "90-day structured onboarding programme",
              "At-Risk New Customers",
              f"${seg_rois['At-Risk New Customers']['net_roi']:,.0f}", "60–90 days", "Medium")
    table_row("5", "Auto-pay migration incentive ($5/month credit)",
              "Electronic check payers",
              "Ongoing savings", "60–90 days", "Low")
    table_row("6", "First-add-on free for zero-addon customers",
              "All segments", "CLV growth", "90–120 days", "Low")
    table_row("7", "Annual contract renewal / upsell campaign",
              "Stable Value Seekers",
              f"${seg_rois['Stable Value Seekers']['net_roi']:,.0f}", "90–120 days", "Medium")

    p()
    p("---")

    # ── Model Deployment ──
    h2("Predictive Model Deployment Recommendations")
    p()
    p("The trained Logistic Regression model (ROC AUC = 0.7609) provides individual-level "
      "churn probability scores. Deploying it operationally enables real-time intervention triggers.")
    p()
    p("**Recommended operational integrations:**")
    p("1. **CRM churn score field:** Push `churn_risk_proxy` score into the CRM for each customer; "
      "refresh weekly via batch scoring.")
    p("2. **Retention queue automation:** Automatically route customers with `churn_risk_proxy ≥ 2.0` "
      "to the retention outreach queue.")
    p("3. **Onboarding trigger:** Flag new customers at month 1 with month-to-month contract + "
      "electronic check + zero add-ons as `high_priority_onboarding`.")
    p("4. **Monthly churn forecast:** Run the model monthly on the full customer base; track "
      "predicted churn rate vs actual to monitor model drift.")
    p("5. **A/B testing framework:** Test retention offers against control groups; measure conversion "
      "using the churn label as the outcome variable.")

    p()
    p("---")

    # ── KPI Targets ──
    h2("Success Metrics & KPI Targets")
    p()
    table_row("KPI", "Baseline (current)", "6-Month Target", "12-Month Target")
    table_sep("KPI", "Baseline (current)", "6-Month Target", "12-Month Target")
    table_row("Overall churn rate", f"{churn_rate:.1f}%", "< 15.0%", "< 12.0%")
    table_row("Month-to-month churn rate", f"{mtm['churn_rate_pct']:.1f}%", "< 28.0%", "< 22.0%")
    table_row("Low Engagement segment churn", f"{high_risk_seg['churn_rate_pct']:.1f}%", "< 26.0%", "< 20.0%")
    table_row("New customer (0–6m) churn rate",
              f"{new_cust.get('churn_rate_pct', 'N/A')}%", "< 8.0%", "< 6.0%")
    table_row("E-check customer churn rate",
              f"{echeck['churn_rate_pct']:.1f}%", "< 25.0%", "< 20.0%")
    table_row("Avg portfolio CLV", f"${avg_clv:,.0f}", f">${avg_clv * 1.05:,.0f}", f">${avg_clv * 1.12:,.0f}")
    table_row("Auto-pay adoption rate",
              f"{int(autopay['customers'] / total * 100)}%", "> 45%", "> 55%")

    p()
    p("---")
    p()
    p("*Report generated automatically by `src/utils/generate_recommendations.py` from live analytics data.*")

    # ── Write ──
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"✓ Business recommendations report written to: {report_path}")


# ─────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────

def run_phase13(db_path: str = DB_PATH, report_path: str = REPORT_PATH):
    print("Loading analytics data...")
    data = load_analytics(db_path)
    ov = data["overview"]
    print(f"  Total customers : {ov['customers']:,}")
    print(f"  Churned         : {ov['churned_customers']:,}")
    print(f"  Churn rate      : {ov['churn_rate_pct']}%")
    print(f"  Total CLV       : ${ov['total_discounted_clv']:,.2f}")
    print("Building recommendations report...")
    build_report(data, report_path)
    print("✓ Phase 13 complete: Business recommendations generated.")


if __name__ == "__main__":
    run_phase13()
