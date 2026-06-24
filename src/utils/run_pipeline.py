"""
Phase 14: End-to-End Pipeline Runner
Customer Churn Prediction & Analytics Platform

Runs every phase script in sequence and records pass/fail status for each.
Produces a production readiness report summarising the full run.
"""

import subprocess
import sys
import os
import time
from datetime import date

PYTHON = sys.executable
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REPORT_PATH = os.path.join(ROOT, "reports", "production_readiness_report.md")

STAGES = [
    {
        "name": "Data Acquisition",
        "phase": 2,
        "script": "src/data_ingestion/acquire_dataset.py",
        "output_check": "data/raw/telco_customer_churn.csv",
    },
    {
        "name": "Data Cleaning",
        "phase": 4,
        "script": "src/data_cleaning/clean_dataset.py",
        "output_check": "data/processed/telco_customer_churn_processed.csv",
    },
    {
        "name": "Feature Engineering",
        "phase": 6,
        "script": "src/feature_engineering/engineer_features.py",
        "output_check": "data/processed/telco_customer_churn_engineered.csv",
    },
    {
        "name": "Customer Segmentation",
        "phase": 7,
        "script": "src/segmentation/segment_customers.py",
        "output_check": "data/processed/telco_customer_churn_segments.csv",
    },
    {
        "name": "CLV Analysis",
        "phase": 8,
        "script": "src/customer_lifetime_value/analyze_clv.py",
        "output_check": "data/processed/telco_customer_churn_clv.csv",
    },
    {
        "name": "Model Training",
        "phase": 9,
        "script": "src/model_training/train_churn_models.py",
        "output_check": "reports/predictive_modeling_readiness_report.md",
    },
    {
        "name": "Explainable AI",
        "phase": 10,
        "script": "src/model_evaluation/explain_models.py",
        "output_check": "reports/feature_explanations.csv",
    },
    {
        "name": "SQL Analytics Layer",
        "phase": 11,
        "script": "src/utils/build_sql_analytics_layer.py",
        "output_check": "data/processed/churn_analytics.db",
    },
    {
        "name": "Business Recommendations",
        "phase": 13,
        "script": "src/utils/generate_recommendations.py",
        "output_check": "reports/business_recommendations_report.md",
    },
    {
        "name": "Batch Scoring",
        "phase": 14,
        "script": "src/prediction/score_customers.py",
        "output_check": "data/processed/customer_churn_scores.csv",
    },
]


def run_stage(stage: dict, cwd: str) -> dict:
    """Run a single pipeline stage, return result dict."""
    script = os.path.join(cwd, stage["script"])
    output = os.path.join(cwd, stage["output_check"])

    start = time.time()
    try:
        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "utf-8"
        result = subprocess.run(
            [PYTHON, script],
            capture_output=True,
            text=True,
            cwd=cwd,
            timeout=300,
            env=env,
        )
        elapsed = time.time() - start
        exit_ok = result.returncode == 0
        output_ok = os.path.isfile(output) and os.path.getsize(output) > 0
        status = "PASS" if (exit_ok and output_ok) else "FAIL"
        detail = ""
        if not exit_ok:
            last_err = result.stderr.strip().splitlines()
            detail = last_err[-1] if last_err else "non-zero exit"
        elif not output_ok:
            detail = f"output missing or empty: {stage['output_check']}"
    except subprocess.TimeoutExpired:
        elapsed = time.time() - start
        status = "TIMEOUT"
        detail = "stage exceeded 300s limit"
    except Exception as exc:
        elapsed = time.time() - start
        status = "ERROR"
        detail = str(exc)

    return {
        "phase": stage["phase"],
        "name": stage["name"],
        "script": stage["script"],
        "status": status,
        "elapsed_s": round(elapsed, 1),
        "detail": detail,
        "output_check": stage["output_check"],
    }


def build_readiness_report(results: list, report_path: str):
    passed = sum(1 for r in results if r["status"] == "PASS")
    total = len(results)
    overall = "ALL PASS" if passed == total else f"{passed}/{total} PASSED"
    today = date.today().isoformat()

    lines = [
        "# Production Readiness Report",
        f"## Phase 14 – Customer Churn Analytics Platform",
        "",
        f"**Generated:** {today}  ",
        f"**Python:** {sys.version.split()[0]}  ",
        f"**Overall result:** {overall}",
        "",
        "---",
        "",
        "## Pipeline Stage Results",
        "",
        "| Phase | Stage | Status | Time (s) | Detail |",
        "|---|---|---|---|---|",
    ]

    for r in results:
        status_icon = "✅ PASS" if r["status"] == "PASS" else f"❌ {r['status']}"
        lines.append(
            f"| {r['phase']} | {r['name']} | {status_icon} | {r['elapsed_s']} | {r['detail'] or '—'} |"
        )

    lines += [
        "",
        "---",
        "",
        "## Artifact Inventory",
        "",
        "| Artifact | Present | Size |",
        "|---|---|---|",
    ]

    artifacts = [
        "data/raw/telco_customer_churn.csv",
        "data/processed/telco_customer_churn_processed.csv",
        "data/processed/telco_customer_churn_engineered.csv",
        "data/processed/telco_customer_churn_segments.csv",
        "data/processed/telco_customer_churn_clv.csv",
        "data/processed/customer_churn_scores.csv",
        "data/processed/churn_analytics.db",
        "reports/profiling_report.md",
        "reports/data_cleaning_report.md",
        "reports/eda_report.md",
        "reports/feature_engineering_report.md",
        "reports/customer_segmentation_report.md",
        "reports/customer_lifetime_value_report.md",
        "reports/predictive_modeling_readiness_report.md",
        "reports/explainable_ai_report.md",
        "reports/feature_explanations.csv",
        "reports/local_reason_codes.csv",
        "reports/explanation_stability.csv",
        "reports/sql_analytics_report.md",
        "reports/sql_quality_checks.csv",
        "reports/business_recommendations_report.md",
        "reports/production_readiness_report.md",
        "dashboard/dax_measures.dax",
        "dashboard/data_model_spec.md",
        "dashboard/dashboard_blueprint.md",
        "sql/analytics_layer.sql",
        "sql/dashboard_query_templates.sql",
    ]

    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    for artifact in artifacts:
        full_path = os.path.join(root, artifact)
        if os.path.isfile(full_path):
            size_kb = os.path.getsize(full_path) / 1024
            lines.append(f"| `{artifact}` | ✅ | {size_kb:.1f} KB |")
        else:
            lines.append(f"| `{artifact}` | ❌ Missing | — |")

    lines += [
        "",
        "---",
        "",
        "## Environment",
        "",
        f"- Python version: `{sys.version}`",
        f"- Platform: `{sys.platform}`",
        "",
        "---",
        "",
        "*Report generated by `src/utils/run_pipeline.py`.*",
    ]

    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"✓ Production readiness report written to: {report_path}")


def run_pipeline():
    cwd = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    print("=" * 60)
    print("  Customer Churn Platform — End-to-End Pipeline")
    print("=" * 60)

    results = []
    for stage in STAGES:
        print(f"\n[Phase {stage['phase']}] {stage['name']}...", end=" ", flush=True)
        result = run_stage(stage, cwd)
        results.append(result)
        print(f"{result['status']} ({result['elapsed_s']}s)"
              + (f"  → {result['detail']}" if result["detail"] else ""))

    passed = sum(1 for r in results if r["status"] == "PASS")
    total = len(results)
    print(f"\n{'='*60}")
    print(f"  Pipeline complete: {passed}/{total} stages passed")
    print(f"{'='*60}")

    build_readiness_report(results, REPORT_PATH)
    return passed == total


if __name__ == "__main__":
    success = run_pipeline()
    sys.exit(0 if success else 1)
