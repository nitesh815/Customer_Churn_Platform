"""
Phase 15: Portfolio Optimization Module
Synthesizes churn predictions, CLV, segmentation, and explainability into strategic
customer portfolio management with resource allocation and ROI modeling.
"""

import pandas as pd
import numpy as np
import sqlite3
from pathlib import Path
import json
from datetime import datetime


class PortfolioOptimizer:
    """Strategic portfolio optimization and customer prioritization engine."""
    
    def __init__(self, project_root: str):
        """Initialize portfolio optimizer with project paths."""
        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "processed"
        self.reports_dir = self.project_root / "reports"
        self.db_path = self.data_dir / "churn_analytics.db"
        
        # Portfolio strategy constants
        self.PORTFOLIO_BUCKETS = {
            "GROW": {"clv_threshold": 0.7, "churn_prob_max": 0.3, "priority": 1},
            "RETAIN": {"clv_threshold": 0.5, "churn_prob_min": 0.3, "priority": 2},
            "OPTIMIZE": {"clv_threshold": 0.3, "churn_prob_min": 0.5, "priority": 3},
            "HARVEST": {"clv_threshold": 0.0, "churn_prob_max": 0.2, "priority": 4},
        }
        
    def load_data(self) -> dict:
        """Load all required datasets for portfolio analysis."""
        print("[Portfolio] Loading data...")
        
        # Load CLV and segmentation
        clv_df = pd.read_csv(self.data_dir / "telco_customer_churn_clv.csv")
        
        # Load local explanations for top drivers
        explanations_df = pd.read_csv(self.reports_dir / "local_reason_codes.csv")
        
        print(f"  [OK] CLV data: {len(clv_df)} customers")
        print(f"  [OK] Explanations: {len(explanations_df)} reasons")
        
        return {
            "clv": clv_df,
            "explanations": explanations_df,
        }
    
    def compute_portfolio_scores(self, data: dict) -> pd.DataFrame:
        """
        Compute multi-dimensional portfolio scores for each customer.
        Combines CLV, churn risk, segment, and value concentration metrics.
        """
        print("[Portfolio] Computing portfolio scores...")
        
        clv_df = data["clv"].copy()
        
        # Use discounted_lifetime_value as main CLV metric
        clv_df["CLV"] = clv_df["discounted_lifetime_value"]
        
        # Normalize CLV to [0, 1] percentile rank
        clv_df["clv_percentile"] = clv_df["CLV"].rank(pct=True)
        
        # Derive churn probability from actual churn rate by segment
        segment_churn = clv_df.groupby("segment_label")["Churn_encoded"].mean()
        clv_df["churn_probability"] = clv_df["segment_label"].map(segment_churn)
        
        # Compute retention opportunity: CLV * (1 - churn_probability)
        clv_df["retention_opportunity"] = (
            clv_df["CLV"] * (1 - clv_df["churn_probability"])
        )
        
        # Normalize retention opportunity to [0, 1]
        max_opp = clv_df["retention_opportunity"].max()
        clv_df["retention_opportunity_score"] = (
            clv_df["retention_opportunity"] / max_opp
            if max_opp > 0 else 0
        )
        
        # Intervention ROI: higher CLV and higher churn = higher ROI
        clv_df["intervention_roi_score"] = (
            clv_df["clv_percentile"] * clv_df["churn_probability"]
        )
        
        # Value concentration: how much of customer base value do they represent
        total_clv = clv_df["CLV"].sum()
        clv_df["value_concentration"] = clv_df["CLV"] / total_clv
        
        # Lifetime stage: based on expected lifetime months
        clv_df["lifetime_stage"] = pd.cut(
            clv_df["expected_lifetime_months"],
            bins=[0, 12, 36, 60, float("inf")],
            labels=["New", "Growth", "Mature", "Established"],
        )
        
        # Rename segment column for consistency
        clv_df["Customer_Segment"] = clv_df["segment_label"]
        
        print(f"  [OK] Computed scores for {len(clv_df)} customers")
        print(f"  [OK] Total portfolio value: ${total_clv:,.0f}")
        
        return clv_df
    
    def assign_portfolio_buckets(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Assign customers to strategic portfolio buckets:
        - GROW: High CLV, low churn → expand relationship
        - RETAIN: Medium-high CLV, high churn → prevent loss
        - OPTIMIZE: Low-medium CLV, high churn → optimize terms or migrate
        - HARVEST: Low CLV, low churn → maintain at cost efficiency
        """
        print("[Portfolio] Assigning portfolio buckets...")
        
        df["portfolio_bucket"] = "HARVEST"  # Default
        
        # GROW: High value + Low churn risk
        grow_mask = (df["clv_percentile"] >= 0.7) & (df["churn_probability"] <= 0.3)
        df.loc[grow_mask, "portfolio_bucket"] = "GROW"
        
        # RETAIN: Medium+ value + High churn risk
        retain_mask = (
            (df["clv_percentile"] >= 0.5) &
            (df["churn_probability"] > 0.3) &
            (df["churn_probability"] <= 0.65)
        )
        df.loc[retain_mask, "portfolio_bucket"] = "RETAIN"
        
        # OPTIMIZE: Lower value + Very high churn risk
        optimize_mask = (
            (df["clv_percentile"] < 0.7) &
            (df["churn_probability"] > 0.65)
        )
        df.loc[optimize_mask, "portfolio_bucket"] = "OPTIMIZE"
        
        bucket_counts = df["portfolio_bucket"].value_counts()
        print(f"  [OK] Portfolio bucket assignment:")
        for bucket, count in bucket_counts.items():
            pct = 100 * count / len(df)
            print(f"    {bucket}: {count} customers ({pct:.1f}%)")
        
        return df
    
    def compute_intervention_scenarios(self, df: pd.DataFrame) -> dict:
        """
        Model retention investment scenarios and expected ROI:
        - Base case: no intervention
        - Conservative: 5% churn reduction @ 10% spend
        - Target: 15% churn reduction @ 25% spend
        - Aggressive: 25% churn reduction @ 40% spend
        """
        print("[Portfolio] Modeling intervention scenarios...")
        
        scenarios = {}
        
        # Calculate current portfolio risk
        current_at_risk = (df["CLV"] * df["churn_probability"]).sum()
        current_lost_annual = current_at_risk
        
        scenarios["base_case"] = {
            "name": "No Intervention",
            "portfolio_value": df["CLV"].sum(),
            "annual_churn_value": current_lost_annual,
            "intervention_spend": 0,
            "retained_customers": 0,
            "net_roi": current_lost_annual * -1,
        }
        
        for scenario_name, params in [
            ("conservative", {"churn_reduction": 0.05, "spend_pct": 0.10}),
            ("target", {"churn_reduction": 0.15, "spend_pct": 0.25}),
            ("aggressive", {"churn_reduction": 0.25, "spend_pct": 0.40}),
        ]:
            # Calculate intervention spend
            total_clv = df["CLV"].sum()
            spend = total_clv * params["spend_pct"]
            
            # Apply churn reduction by bucket
            df_scenario = df.copy()
            df_scenario["churn_probability_reduced"] = df_scenario["churn_probability"] * (
                1 - params["churn_reduction"]
            )
            
            retained_value = (
                (df_scenario["churn_probability"] - df_scenario["churn_probability_reduced"]) *
                df_scenario["CLV"]
            ).sum()
            
            net_roi = retained_value - spend
            
            scenarios[scenario_name] = {
                "name": scenario_name.replace("_", " ").title(),
                "churn_reduction_pct": params["churn_reduction"] * 100,
                "intervention_spend": spend,
                "retained_annual_value": retained_value,
                "net_roi": net_roi,
                "roi_ratio": retained_value / spend if spend > 0 else 0,
            }
        
        for scenario_name, details in scenarios.items():
            print(f"  [OK] {details['name']}: ROI = ${details.get('net_roi', details.get('net_roi', 0)):,.0f}")
        
        return scenarios
    
    def compute_segment_playbooks(self, df: pd.DataFrame) -> dict:
        """
        Generate segment-specific intervention playbooks with:
        - Segment profile and metrics
        - Key churn drivers
        - Recommended actions
        - Expected outcomes
        """
        print("[Portfolio] Generating segment playbooks...")
        
        playbooks = {}
        
        for segment in df["Customer_Segment"].unique():
            seg_df = df[df["Customer_Segment"] == segment]
            
            playbooks[segment] = {
                "segment_name": segment,
                "customer_count": len(seg_df),
                "avg_clv": seg_df["CLV"].mean(),
                "total_clv": seg_df["CLV"].sum(),
                "churn_rate": seg_df["churn_probability"].mean(),
                "at_risk_value": (seg_df["CLV"] * seg_df["churn_probability"]).sum(),
                "portfolio_distribution": {
                    "grow": len(seg_df[seg_df["portfolio_bucket"] == "GROW"]),
                    "retain": len(seg_df[seg_df["portfolio_bucket"] == "RETAIN"]),
                    "optimize": len(seg_df[seg_df["portfolio_bucket"] == "OPTIMIZE"]),
                    "harvest": len(seg_df[seg_df["portfolio_bucket"] == "HARVEST"]),
                },
                "recommended_tactics": self._get_segment_tactics(segment),
            }
        
        print(f"  [OK] Generated {len(playbooks)} segment playbooks")
        return playbooks
    
    def _get_segment_tactics(self, segment: str) -> list:
        """Return segment-specific intervention tactics."""
        tactics = {
            "High Value Loyalists": [
                "White-glove account management",
                "Exclusive upgrade pathways",
                "Proactive service excellence",
                "Executive relationship building",
            ],
            "High Value Churners": [
                "Retention offers and discounts",
                "Problem resolution task forces",
                "Service quality audits",
                "Contract upgrade incentives",
            ],
            "At-Risk New Customers": [
                "Intensive onboarding program",
                "Early success metrics tracking",
                "Proactive support engagement",
                "Quick-win delivery targets",
            ],
            "Stable Low-Value": [
                "Cost-efficient maintenance",
                "Automation and self-service",
                "Predictable renewal processes",
                "Upsell opportunity identification",
            ],
        }
        return tactics.get(segment, ["Standard retention tactics"])
    
    def generate_portfolio_strategy(self, df: pd.DataFrame, scenarios: dict) -> dict:
        """Synthesize portfolio optimization strategy."""
        print("[Portfolio] Synthesizing portfolio strategy...")
        
        strategy = {
            "timestamp": datetime.now().isoformat(),
            "total_customers": len(df),
            "total_portfolio_value": float(df["CLV"].sum()),
            "total_annual_churn_risk": float((df["CLV"] * df["churn_probability"]).sum()),
            "portfolio_diversity": {
                "grow": len(df[df["portfolio_bucket"] == "GROW"]),
                "retain": len(df[df["portfolio_bucket"] == "RETAIN"]),
                "optimize": len(df[df["portfolio_bucket"] == "OPTIMIZE"]),
                "harvest": len(df[df["portfolio_bucket"] == "HARVEST"]),
            },
            "recommended_scenario": "target",
            "key_insights": self._generate_key_insights(df, scenarios),
        }
        
        return strategy
    
    def _generate_key_insights(self, df: pd.DataFrame, scenarios: dict) -> list:
        """Extract actionable portfolio insights."""
        insights = []
        
        # Top insight: portfolio concentration
        top_10_pct = df.nlargest(int(len(df) * 0.1), "CLV")["CLV"].sum()
        total = df["CLV"].sum()
        concentration = 100 * top_10_pct / total if total > 0 else 0
        insights.append(
            f"Top 10% of customers represent {concentration:.1f}% of portfolio value "
            f"(concentration risk)"
        )
        
        # Churn risk concentration
        high_churn = df[df["churn_probability"] > 0.5]
        at_risk_value = (high_churn["CLV"] * high_churn["churn_probability"]).sum()
        insights.append(
            f"High-churn segment represents ${at_risk_value:,.0f} "
            f"in annual churn risk ({100*len(high_churn)/len(df):.1f}% of customers)"
        )
        
        # GROW opportunity
        grow_customers = df[df["portfolio_bucket"] == "GROW"]
        grow_value = grow_customers["CLV"].sum()
        insights.append(
            f"GROW segment: {len(grow_customers)} high-value, low-risk customers "
            f"representing ${grow_value:,.0f} in expansion opportunity"
        )
        
        # Segment insights
        best_segment = df.groupby("Customer_Segment")["CLV"].sum().idxmax()
        insights.append(
            f"Highest-value segment is '{best_segment}' - "
            f"prioritize for growth and account expansion"
        )
        
        return insights
    
    def export_results(self, df: pd.DataFrame, scenarios: dict, playbooks: dict,
                      strategy: dict) -> str:
        """Export portfolio optimization results to CSV and JSON."""
        print("[Portfolio] Exporting results...")
        
        # Export customer-level portfolio strategy
        export_cols = [
            "customerID", "Customer_Segment", "expected_lifetime_months", "CLV",
            "churn_probability", "clv_percentile", "retention_opportunity_score",
            "intervention_roi_score", "portfolio_bucket", "lifetime_stage",
        ]
        export_df = df[[col for col in export_cols if col in df.columns]].copy()
        
        output_csv = self.data_dir / "customer_portfolio_strategy.csv"
        export_df.to_csv(output_csv, index=False)
        print(f"  [OK] Exported portfolio dataset: {output_csv}")
        
        # Export scenario summary as JSON
        output_json = self.reports_dir / "portfolio_scenarios.json"
        with open(output_json, "w") as f:
            json.dump({
                "scenarios": scenarios,
                "strategy": strategy,
                "playbooks": playbooks,
            }, f, indent=2, default=str)
        print(f"  [OK] Exported scenarios: {output_json}")
        
        return str(output_csv)
    
    def run(self) -> dict:
        """Execute full portfolio optimization pipeline."""
        print("\n" + "="*70)
        print("PHASE 15: PORTFOLIO OPTIMIZATION")
        print("="*70 + "\n")
        
        # Load data
        data = self.load_data()
        
        # Compute scores
        df = self.compute_portfolio_scores(data)
        
        # Assign portfolio buckets
        df = self.assign_portfolio_buckets(df)
        
        # Model intervention scenarios
        scenarios = self.compute_intervention_scenarios(df)
        
        # Generate playbooks
        playbooks = self.compute_segment_playbooks(df)
        
        # Synthesize strategy
        strategy = self.generate_portfolio_strategy(df, scenarios)
        
        # Export
        output_csv = self.export_results(df, scenarios, playbooks, strategy)
        
        print("\n" + "="*70)
        print("PHASE 15 COMPLETE")
        print("="*70 + "\n")
        
        return {
            "df": df,
            "scenarios": scenarios,
            "playbooks": playbooks,
            "strategy": strategy,
            "output_csv": output_csv,
        }


def main():
    """Execute portfolio optimization as standalone script."""
    project_root = Path(__file__).parent.parent.parent
    optimizer = PortfolioOptimizer(str(project_root))
    results = optimizer.run()
    return results


if __name__ == "__main__":
    main()
