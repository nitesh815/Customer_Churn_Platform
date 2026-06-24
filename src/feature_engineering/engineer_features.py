"""
Feature engineering module for customer churn analytics platform.

This module handles:
1. Generation of behavior and value proxy features
2. Risk-oriented interaction features from EDA insights
3. Output of a modeling-ready engineered dataset
4. Auto-generation of a Phase 6 summary report
"""

from pathlib import Path
from typing import Tuple

import pandas as pd


def load_datasets(raw_csv: str, processed_csv: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Load raw and processed datasets."""
    raw_df = pd.read_csv(raw_csv)
    processed_df = pd.read_csv(processed_csv)

    if raw_df.empty or processed_df.empty:
        raise ValueError('Input dataset is empty')

    return raw_df, processed_df


def create_engineered_features(raw_df: pd.DataFrame, processed_df: pd.DataFrame) -> pd.DataFrame:
    """Create engineered features using both raw context and processed numeric base."""
    df = processed_df.merge(
        raw_df[
            [
                'customerID',
                'tenure',
                'MonthlyCharges',
                'TotalCharges',
                'Contract',
                'InternetService',
                'PaymentMethod',
            ]
        ],
        on='customerID',
        how='left',
        validate='one_to_one',
    )

    if df[['tenure', 'MonthlyCharges', 'TotalCharges']].isna().any().any():
        raise ValueError('Join failure detected while adding raw features')

    # Tenure lifecycle flags
    df['is_new_customer_0_6m'] = (df['tenure'] <= 6).astype(int)
    df['is_established_customer_24m'] = (df['tenure'] >= 24).astype(int)
    df['is_long_tenure_48m'] = (df['tenure'] >= 48).astype(int)

    # Contract + payment behavior flags
    df['is_month_to_month'] = (df['Contract_encoded'] == 0).astype(int)
    df['is_auto_pay'] = df['PaymentMethod'].isin(['Bank transfer', 'Credit card']).astype(int)
    df['is_electronic_check'] = (df['PaymentMethod'] == 'Electronic check').astype(int)

    # Internet and add-on adoption proxies
    df['has_internet'] = (df['InternetService'] != 'No').astype(int)
    df['security_bundle'] = (
        (df['OnlineSecurity_Yes'] == 1)
        | (df['OnlineBackup_Yes'] == 1)
        | (df['DeviceProtection_Yes'] == 1)
        | (df['TechSupport_Yes'] == 1)
    ).astype(int)

    df['addon_count'] = (
        df['OnlineSecurity_Yes']
        + df['OnlineBackup_Yes']
        + df['DeviceProtection_Yes']
        + df['TechSupport_Yes']
        + df['StreamingTV_Yes']
        + df['StreamingMovies_Yes']
    )

    df['internet_addon_adoption_rate'] = (
        df['addon_count'] / 6.0
    ).round(4)
    df.loc[df['has_internet'] == 0, 'internet_addon_adoption_rate'] = 0.0

    # Revenue/value behavior
    df['charges_per_tenure_month'] = (
        df['TotalCharges'] / df['tenure'].clip(lower=1)
    ).round(4)
    df['high_monthly_charge'] = (df['MonthlyCharges'] >= 80).astype(int)
    df['high_total_value'] = (df['TotalCharges'] >= 3000).astype(int)

    # EDA-informed churn risk proxy (non-target feature)
    risk_score = (
        2.0 * df['is_month_to_month']
        + 1.5 * df['is_new_customer_0_6m']
        + 1.0 * df['is_electronic_check']
        + 0.8 * (df['InternetService_encoded'] == 2).astype(int)
        - 1.2 * (df['Contract_encoded'] == 2).astype(int)
        - 0.8 * df['security_bundle']
        - 0.5 * df['is_auto_pay']
    )
    df['churn_risk_proxy'] = risk_score.round(4)

    # Interaction effects for tree-based and linear models
    df['tenure_x_monthlycharges'] = (
        df['tenure_normalized'] * df['MonthlyCharges_normalized']
    ).round(4)
    df['mtm_x_echeck'] = (df['is_month_to_month'] * df['is_electronic_check']).astype(int)
    df['new_x_fiber'] = (
        df['is_new_customer_0_6m'] * (df['InternetService_encoded'] == 2).astype(int)
    ).astype(int)

    # Drop raw columns after engineered signals are materialized.
    df = df.drop(
        columns=['Contract', 'InternetService', 'PaymentMethod', 'tenure', 'MonthlyCharges', 'TotalCharges']
    )

    return df


def save_dataset(df: pd.DataFrame, output_csv: str) -> None:
    """Save engineered dataset."""
    out_path = Path(output_csv)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_path, index=False)


def build_report(engineered_df: pd.DataFrame, report_path: str) -> None:
    """Build a concise markdown report for Phase 6 outputs."""
    out_path = Path(report_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    total_cols = engineered_df.shape[1]
    engineered_cols = [
        'is_new_customer_0_6m',
        'is_established_customer_24m',
        'is_long_tenure_48m',
        'is_month_to_month',
        'is_auto_pay',
        'is_electronic_check',
        'has_internet',
        'security_bundle',
        'addon_count',
        'internet_addon_adoption_rate',
        'charges_per_tenure_month',
        'high_monthly_charge',
        'high_total_value',
        'churn_risk_proxy',
        'tenure_x_monthlycharges',
        'mtm_x_echeck',
        'new_x_fiber',
    ]

    churn_counts = engineered_df['Churn_encoded'].value_counts().to_dict()
    churn_no = int(churn_counts.get(0, 0))
    churn_yes = int(churn_counts.get(1, 0))
    churn_rate = (churn_yes / max(len(engineered_df), 1)) * 100
    high_risk_rate = (engineered_df['churn_risk_proxy'] >= 2.0).mean() * 100
    new_customer_rate = engineered_df['is_new_customer_0_6m'].mean() * 100
    avg_addon = engineered_df['addon_count'].mean()

    lines = [
        '# Feature Engineering Report',
        '## Phase 6 - Derived Feature Construction',
        '',
        '**Generated:** 2026-06-24  ',
        '**Input Dataset:** `data/processed/telco_customer_churn_processed.csv`  ',
        '**Output Dataset:** `data/processed/telco_customer_churn_engineered.csv`  ',
        '**Status:** In Progress - Core engineered feature set generated',
        '',
        '---',
        '',
        '## Summary',
        '',
        f'- Records processed: {engineered_df.shape[0]:,}',
        f'- Total output features: {total_cols}',
        f'- New engineered features added: {len(engineered_cols)}',
        f'- Churn base rate (reference): {churn_rate:.2f}%',
        f'- Target distribution: No={churn_no:,}, Yes={churn_yes:,}',
        '',
        '## Engineered Features Added',
        '',
    ]

    for feature in engineered_cols:
        lines.append(f'- `{feature}`')

    lines.extend(
        [
            '',
            '## Quick Diagnostics',
            '',
            f'- High risk proxy customers (`churn_risk_proxy >= 2.0`): {high_risk_rate:.2f}%',
            f'- New customers (`is_new_customer_0_6m = 1`): {new_customer_rate:.2f}%',
            f'- Average add-on count: {avg_addon:.2f} / 6',
            '',
            '## Notes',
            '',
            '- Features are numeric and compatible with scikit-learn/XGBoost training pipelines.',
            '- Risk proxy is a business-informed composite signal and does not use target leakage.',
            '- Interaction features are included to improve nonlinear separation in churn models.',
            '- Current dataset snapshot has single-class target if `Yes = 0`, which blocks supervised churn modeling until resolved.',
            '',
            '## Next Steps',
            '',
            '1. Run feature importance screening and collinearity checks.',
            '2. Build train/validation split with stratification for Phase 9 modeling.',
            '3. Benchmark baseline vs engineered-feature model lift.',
        ]
    )

    out_path.write_text('\n'.join(lines), encoding='utf-8')


def run_feature_engineering(
    raw_csv: str,
    processed_csv: str,
    output_csv: str,
    report_path: str,
) -> None:
    """Run the full feature engineering workflow."""
    print('Loading datasets...')
    raw_df, processed_df = load_datasets(raw_csv, processed_csv)
    print(f'  Raw records: {len(raw_df):,}')
    print(f'  Processed records: {len(processed_df):,}')

    print('Creating engineered features...')
    engineered_df = create_engineered_features(raw_df, processed_df)

    target_yes = int((engineered_df['Churn_encoded'] == 1).sum())
    if target_yes == 0:
        print('! Warning: Churn target has no positive class in current dataset snapshot')

    print(f'  Output shape: {engineered_df.shape[0]:,} rows x {engineered_df.shape[1]} columns')
    print('Saving engineered dataset...')
    save_dataset(engineered_df, output_csv)

    print('Building Phase 6 report...')
    build_report(engineered_df, report_path)

    print('✓ Phase 6 started: engineered dataset and report generated')


if __name__ == '__main__':
    run_feature_engineering(
        raw_csv='data/raw/telco_customer_churn.csv',
        processed_csv='data/processed/telco_customer_churn_processed.csv',
        output_csv='data/processed/telco_customer_churn_engineered.csv',
        report_path='reports/feature_engineering_report.md',
    )