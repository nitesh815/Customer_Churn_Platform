"""
Customer lifetime value analysis module for the churn analytics platform.

This module handles:
1. CLV proxy calculation from segmented customer data
2. Segment-level value profiling
3. Output of a customer-level CLV dataset
4. Generation of a Phase 8 markdown report
"""

from pathlib import Path

import pandas as pd


def load_segmented_data(csv_path: str) -> pd.DataFrame:
    """Load segmented customer dataset."""
    df = pd.read_csv(csv_path)
    if df.empty:
        raise ValueError('Segmented dataset is empty')
    return df


def compute_clv_features(df: pd.DataFrame) -> pd.DataFrame:
    """Compute explainable CLV proxy features."""
    result = df.copy()

    # Convert normalized charges back into a comparable business-scale proxy.
    result['monthly_value_proxy'] = result['MonthlyCharges_normalized'] * 100.0 + 18.0
    result['total_value_proxy'] = result['TotalCharges_normalized'] * 8500.0

    # Risk-adjusted service horizon: longer tenure and lower risk imply longer projected retention.
    base_horizon = 72.0 - (result['tenure_normalized'] * 72.0)
    risk_adjustment = (
        10.0 * (1.5 - result['churn_risk_proxy']).clip(lower=-5.0, upper=5.0)
    )
    segment_adjustment = result['segment_label'].map(
        {
            'High Value Loyalists': 12.0,
            'Stable Value Seekers': 4.0,
            'Low Engagement Churn Risk': -2.0,
            'At-Risk New Customers': -8.0,
        }
    ).fillna(0.0)

    result['projected_remaining_months'] = (
        base_horizon + risk_adjustment + segment_adjustment
    ).clip(lower=3.0, upper=72.0).round(2)

    # Expected lifetime is current tenure plus projected remaining horizon.
    current_tenure_months = result['tenure_normalized'] * 72.0
    result['expected_lifetime_months'] = (
        current_tenure_months + result['projected_remaining_months']
    ).clip(lower=3.0, upper=144.0).round(2)

    # Discounted CLV proxy using a simple monthly discount factor.
    monthly_discount_rate = 0.01
    discounted_months = (
        1 - (1 + monthly_discount_rate) ** (-result['expected_lifetime_months'])
    ) / monthly_discount_rate
    result['discounted_lifetime_value'] = (
        result['monthly_value_proxy'] * discounted_months
    ).round(2)

    # Retention leverage score rewards high value and stable retention signals.
    result['retention_leverage_score'] = (
        0.5 * result['discounted_lifetime_value']
        + 20.0 * result['security_bundle']
        + 10.0 * result['is_auto_pay']
        - 15.0 * result['is_electronic_check']
        + 8.0 * result['is_long_tenure_48m']
    ).round(2)

    return result


def save_clv_dataset(df: pd.DataFrame, output_csv: str) -> None:
    """Save customer-level CLV dataset."""
    out_path = Path(output_csv)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_path, index=False)


def build_clv_report(df: pd.DataFrame, report_path: str) -> None:
    """Generate a markdown report summarizing CLV findings."""
    out_path = Path(report_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    segment_summary = (
        df.groupby('segment_label')
        .agg(
            customers=('customerID', 'count'),
            avg_monthly_value=('monthly_value_proxy', 'mean'),
            avg_expected_lifetime=('expected_lifetime_months', 'mean'),
            avg_discounted_clv=('discounted_lifetime_value', 'mean'),
            avg_retention_leverage=('retention_leverage_score', 'mean'),
            avg_risk=('churn_risk_proxy', 'mean'),
        )
        .reset_index()
        .sort_values('avg_discounted_clv', ascending=False)
    )

    top_customers = df.nlargest(10, 'discounted_lifetime_value')[
        ['customerID', 'segment_label', 'monthly_value_proxy', 'expected_lifetime_months', 'discounted_lifetime_value']
    ]

    total_customers = len(df)
    total_clv = df['discounted_lifetime_value'].sum()
    avg_clv = df['discounted_lifetime_value'].mean()

    lines = [
        '# Customer Lifetime Value Report',
        '## Phase 8 - CLV Proxy Analysis',
        '',
        '**Generated:** 2026-06-24  ',
        '**Input Dataset:** `data/processed/telco_customer_churn_segments.csv`  ',
        '**Output Dataset:** `data/processed/telco_customer_churn_clv.csv`  ',
        '**Status:** In Progress - CLV dataset generated',
        '',
        '---',
        '',
        '## Summary',
        '',
        f'- Customers analyzed: {total_customers:,}',
        f'- Total discounted CLV proxy: ${total_clv:,.2f}',
        f'- Average CLV proxy per customer: ${avg_clv:,.2f}',
        '',
        '## CLV Features',
        '',
        '- `monthly_value_proxy`',
        '- `projected_remaining_months`',
        '- `expected_lifetime_months`',
        '- `discounted_lifetime_value`',
        '- `retention_leverage_score`',
        '',
        '## Segment Summary',
        '',
    ]

    for _, row in segment_summary.iterrows():
        lines.extend(
            [
                f'### {row["segment_label"]}',
                '',
                f'- Customers: {int(row["customers"]):,}',
                f'- Average monthly value proxy: ${row["avg_monthly_value"]:,.2f}',
                f'- Average expected lifetime: {row["avg_expected_lifetime"]:.2f} months',
                f'- Average discounted CLV: ${row["avg_discounted_clv"]:,.2f}',
                f'- Average retention leverage: {row["avg_retention_leverage"]:.2f}',
                f'- Average risk proxy: {row["avg_risk"]:.4f}',
                '',
            ]
        )

    lines.extend(
        [
            '## Top Customers by CLV',
            '',
            '| Customer ID | Segment | Monthly Value | Expected Lifetime (Months) | Discounted CLV |',
            '|---|---|---:|---:|---:|',
        ]
    )

    for _, row in top_customers.iterrows():
        lines.append(
            f'| {row["customerID"]} | {row["segment_label"]} | ${row["monthly_value_proxy"]:,.2f} | {row["expected_lifetime_months"]:.2f} | ${row["discounted_lifetime_value"]:,.2f} |'
        )

    lines.extend(
        [
            '',
            '## Notes',
            '',
            '- CLV is intentionally explainable and proxy-based because supervised churn probabilities are not available from the current snapshot.',
            '- The model rewards longer projected lifetimes, higher monthly value, and lower operational risk.',
            '- Segment-level results can be used to prioritize retention investment and upsell strategy.',
            '',
            '## Next Steps',
            '',
            '1. Validate CLV sensitivity against alternate discount rates and retention horizons.',
            '2. Build CLV threshold bands for executive dashboarding.',
            '3. Use segment-specific CLV to refine retention playbooks and marketing offers.',
        ]
    )

    out_path.write_text('\n'.join(lines), encoding='utf-8')


def run_clv_analysis(
    segmented_csv: str,
    output_csv: str,
    report_path: str,
) -> None:
    """Run the full CLV workflow."""
    print('Loading segmented dataset...')
    df = load_segmented_data(segmented_csv)
    print(f'  Records loaded: {len(df):,}')

    print('Computing CLV features...')
    clv_df = compute_clv_features(df)
    print(f'  Output shape: {clv_df.shape[0]:,} rows x {clv_df.shape[1]} columns')

    print('Saving CLV dataset...')
    save_clv_dataset(clv_df, output_csv)

    print('Building Phase 8 report...')
    build_clv_report(clv_df, report_path)

    print('✓ Phase 8 started: CLV dataset and report generated')


if __name__ == '__main__':
    run_clv_analysis(
        segmented_csv='data/processed/telco_customer_churn_segments.csv',
        output_csv='data/processed/telco_customer_churn_clv.csv',
        report_path='reports/customer_lifetime_value_report.md',
    )