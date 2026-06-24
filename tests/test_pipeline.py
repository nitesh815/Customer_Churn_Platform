"""
Phase 14: Unit Test Suite
Customer Churn Prediction & Analytics Platform

Tests critical invariants across the data pipeline, feature engineering,
segmentation, CLV, and scoring modules.
"""

import os
import sys
import sqlite3
import unittest
import pandas as pd
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)


class TestRawDataset(unittest.TestCase):
    """Phase 2 — Raw dataset integrity."""

    @classmethod
    def setUpClass(cls):
        path = os.path.join(ROOT, "data", "raw", "telco_customer_churn.csv")
        cls.df = pd.read_csv(path)

    def test_row_count(self):
        self.assertGreater(len(self.df), 1000, "Raw dataset should have > 1,000 rows")

    def test_churn_column_exists(self):
        self.assertIn("Churn", self.df.columns)

    def test_both_churn_classes_present(self):
        vals = self.df["Churn"].unique()
        self.assertIn("Yes", vals, "Churn=Yes must be present")
        self.assertIn("No", vals, "Churn=No must be present")

    def test_churn_rate_reasonable(self):
        rate = (self.df["Churn"] == "Yes").mean()
        self.assertGreater(rate, 0.05, "Churn rate should be > 5%")
        self.assertLess(rate, 0.60, "Churn rate should be < 60%")

    def test_no_duplicate_customer_ids(self):
        self.assertEqual(self.df["customerID"].nunique(), len(self.df),
                         "customerID must be unique per row")

    def test_tenure_non_negative(self):
        self.assertTrue((self.df["tenure"] >= 0).all(), "Tenure must be non-negative")


class TestProcessedDataset(unittest.TestCase):
    """Phase 4 — Cleaned/encoded dataset."""

    @classmethod
    def setUpClass(cls):
        path = os.path.join(ROOT, "data", "processed",
                            "telco_customer_churn_processed.csv")
        cls.df = pd.read_csv(path)

    def test_churn_encoded_binary(self):
        self.assertIn("Churn_encoded", self.df.columns)
        vals = self.df["Churn_encoded"].unique()
        for v in vals:
            self.assertIn(v, [0, 1], "Churn_encoded must be 0 or 1")

    def test_normalized_columns_bounded(self):
        for col in ["tenure_normalized", "MonthlyCharges_normalized"]:
            if col in self.df.columns:
                self.assertGreaterEqual(self.df[col].min(), 0.0 - 1e-6)
                self.assertLessEqual(self.df[col].max(), 1.0 + 1e-6)

    def test_no_all_null_columns(self):
        null_cols = [c for c in self.df.columns if self.df[c].isnull().all()]
        self.assertEqual(null_cols, [], f"Fully null columns found: {null_cols}")


class TestEngineeredDataset(unittest.TestCase):
    """Phase 6 — Feature engineering."""

    @classmethod
    def setUpClass(cls):
        path = os.path.join(ROOT, "data", "processed",
                            "telco_customer_churn_engineered.csv")
        cls.df = pd.read_csv(path)

    def test_engineered_features_present(self):
        expected = [
            "is_new_customer_0_6m", "is_long_tenure_48m",
            "is_month_to_month", "addon_count", "security_bundle",
            "churn_risk_proxy",
        ]
        for col in expected:
            self.assertIn(col, self.df.columns, f"Missing engineered feature: {col}")

    def test_addon_count_bounds(self):
        self.assertGreaterEqual(self.df["addon_count"].min(), 0)
        self.assertLessEqual(self.df["addon_count"].max(), 10)

    def test_binary_flags_are_binary(self):
        for col in ["is_new_customer_0_6m", "is_long_tenure_48m",
                    "is_month_to_month", "security_bundle"]:
            if col in self.df.columns:
                vals = set(self.df[col].dropna().unique())
                self.assertTrue(vals.issubset({0, 1}), f"{col} must be binary")


class TestSegmentDataset(unittest.TestCase):
    """Phase 7 — Customer segmentation."""

    @classmethod
    def setUpClass(cls):
        path = os.path.join(ROOT, "data", "processed",
                            "telco_customer_churn_segments.csv")
        cls.df = pd.read_csv(path)

    def test_segment_label_column(self):
        self.assertIn("segment_label", self.df.columns)

    def test_exactly_four_segments(self):
        n_segs = self.df["segment_label"].nunique()
        self.assertEqual(n_segs, 4, f"Expected 4 segments, found {n_segs}")

    def test_no_unassigned_rows(self):
        nulls = self.df["segment_label"].isnull().sum()
        self.assertEqual(nulls, 0, "All rows must have a segment label")


class TestCLVDataset(unittest.TestCase):
    """Phase 8 — CLV analysis."""

    @classmethod
    def setUpClass(cls):
        path = os.path.join(ROOT, "data", "processed",
                            "telco_customer_churn_clv.csv")
        cls.df = pd.read_csv(path)

    def test_clv_column_present(self):
        self.assertIn("discounted_lifetime_value", self.df.columns)

    def test_clv_non_negative(self):
        self.assertTrue(
            (self.df["discounted_lifetime_value"] >= 0).all(),
            "CLV values must be non-negative",
        )

    def test_retention_leverage_present(self):
        self.assertIn("retention_leverage_score", self.df.columns)

    def test_row_count_consistent(self):
        raw_path = os.path.join(ROOT, "data", "raw", "telco_customer_churn.csv")
        raw = pd.read_csv(raw_path)
        self.assertEqual(len(self.df), len(raw),
                         "CLV dataset row count must match raw dataset")


class TestSQLAnalyticsLayer(unittest.TestCase):
    """Phase 11 — SQLite analytics layer."""

    @classmethod
    def setUpClass(cls):
        db_path = os.path.join(ROOT, "data", "processed", "churn_analytics.db")
        cls.conn = sqlite3.connect(db_path)

    @classmethod
    def tearDownClass(cls):
        cls.conn.close()

    def test_base_table_exists(self):
        tables = [r[0] for r in
                  self.conn.execute("SELECT name FROM sqlite_master WHERE type='table'")]
        self.assertIn("customer_analytics", tables)

    def test_all_views_exist(self):
        views = [r[0] for r in
                 self.conn.execute("SELECT name FROM sqlite_master WHERE type='view'")]
        for v in ["vw_churn_overview", "vw_segment_kpis", "vw_contract_retention",
                  "vw_clv_bands", "vw_top_risk_customers"]:
            self.assertIn(v, views, f"View missing: {v}")

    def test_row_count_consistent(self):
        n = self.conn.execute("SELECT COUNT(*) FROM customer_analytics").fetchone()[0]
        self.assertGreater(n, 1000, "analytics DB should have > 1,000 rows")

    def test_churn_rate_in_range(self):
        rate = self.conn.execute(
            "SELECT churn_rate_pct FROM vw_churn_overview"
        ).fetchone()[0]
        self.assertGreater(rate, 5, "Churn rate should be > 5%")
        self.assertLess(rate, 60, "Churn rate should be < 60%")

    def test_four_segments_in_view(self):
        n = self.conn.execute(
            "SELECT COUNT(*) FROM vw_segment_kpis"
        ).fetchone()[0]
        self.assertEqual(n, 4, "vw_segment_kpis should have 4 rows")

    def test_clv_bands_sum_to_total(self):
        band_total = self.conn.execute(
            "SELECT SUM(customers) FROM vw_clv_bands"
        ).fetchone()[0]
        base_total = self.conn.execute(
            "SELECT COUNT(*) FROM customer_analytics"
        ).fetchone()[0]
        self.assertEqual(band_total, base_total,
                         "CLV band customer counts must sum to base table total")


class TestScoringModule(unittest.TestCase):
    """Phase 14 — Batch scoring output."""

    @classmethod
    def setUpClass(cls):
        path = os.path.join(ROOT, "data", "processed", "customer_churn_scores.csv")
        cls.df = pd.read_csv(path) if os.path.exists(path) else None

    def test_scored_file_exists(self):
        path = os.path.join(ROOT, "data", "processed", "customer_churn_scores.csv")
        self.assertTrue(os.path.isfile(path), "Scored CSV must exist")

    def test_probability_bounded(self):
        if self.df is None:
            self.skipTest("Scored file not yet generated")
        self.assertTrue((self.df["churn_probability"] >= 0).all())
        self.assertTrue((self.df["churn_probability"] <= 1).all())

    def test_prediction_binary(self):
        if self.df is None:
            self.skipTest("Scored file not yet generated")
        vals = set(self.df["churn_predicted"].unique())
        self.assertTrue(vals.issubset({0, 1}), "churn_predicted must be 0 or 1")

    def test_risk_tiers_valid(self):
        if self.df is None:
            self.skipTest("Scored file not yet generated")
        valid = {"Critical", "High", "Medium", "Low"}
        actual = set(self.df["risk_tier"].unique())
        self.assertTrue(actual.issubset(valid), f"Unexpected risk tiers: {actual - valid}")

    def test_row_count_matches_clv(self):
        if self.df is None:
            self.skipTest("Scored file not yet generated")
        clv_path = os.path.join(ROOT, "data", "processed",
                                "telco_customer_churn_clv.csv")
        clv = pd.read_csv(clv_path)
        self.assertEqual(len(self.df), len(clv),
                         "Scored file must have same row count as CLV dataset")


if __name__ == "__main__":
    unittest.main(verbosity=2)
