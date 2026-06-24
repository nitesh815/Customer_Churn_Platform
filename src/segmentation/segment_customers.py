"""
Customer segmentation module for customer churn analytics platform.

This module handles:
1. RFM-style feature derivation from engineered customer data
2. Unsupervised clustering for customer segment discovery
3. Segment profiling and summary report generation
4. Export of a segment-labeled dataset for downstream analysis
"""

from pathlib import Path
from typing import Tuple

import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler


def load_engineered_data(csv_path: str) -> pd.DataFrame:
    """Load engineered customer dataset."""
    df = pd.read_csv(csv_path)
    if df.empty:
        raise ValueError('Engineered dataset is empty')
    return df


def create_segmentation_features(df: pd.DataFrame) -> pd.DataFrame:
    """Create segmentation features inspired by RFM and retention behavior."""
    result = df.copy()

    # Recency proxy: lower tenure implies more recent customers
    result['recency_proxy'] = (1.0 - result['tenure_normalized']).round(4)

    # Frequency proxy: number of adopted add-on services plus internet adoption
    result['frequency_proxy'] = (
        result['addon_count'] + result['has_internet'] + result['security_bundle']
    ).round(4)

    # Monetary proxy: blend monthly and total normalized value
    result['monetary_proxy'] = (
        0.6 * result['MonthlyCharges_normalized'] + 0.4 * result['TotalCharges_normalized']
    ).round(4)

    # Service depth and commitment behavior
    result['service_depth_proxy'] = (
        result['addon_count'] + result['security_bundle'] + result['has_internet']
    ).round(4)
    result['commitment_proxy'] = (
        result['Contract_encoded'] + result['is_auto_pay'] + result['is_long_tenure_48m']
    ).round(4)

    # Risk behavior already derived in Phase 6; reused here for profiling
    result['risk_proxy_bucket'] = pd.cut(
        result['churn_risk_proxy'],
        bins=[-10, -0.5, 1.0, 2.5, 10],
        labels=['Low Risk', 'Moderate Risk', 'High Risk', 'Critical Risk'],
        include_lowest=True,
    )

    return result


def run_clustering(df: pd.DataFrame, n_clusters: int = 4) -> pd.DataFrame:
    """Cluster customers using standardized segmentation features."""
    feature_cols = [
        'recency_proxy',
        'frequency_proxy',
        'monetary_proxy',
        'service_depth_proxy',
        'commitment_proxy',
        'churn_risk_proxy',
    ]

    scaler = StandardScaler()
    scaled_features = scaler.fit_transform(df[feature_cols])

    model = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    cluster_ids = model.fit_predict(scaled_features)

    result = df.copy()
    result['segment_id'] = cluster_ids
    result['segment_label'] = result['segment_id'].map(
        {
            0: 'Stable Value Seekers',
            1: 'At-Risk New Customers',
            2: 'High Value Loyalists',
            3: 'Low Engagement Churn Risk',
        }
    )

    return result


def evaluate_cluster_stability(df: pd.DataFrame, cluster_range: Tuple[int, ...] = (3, 4, 5)) -> pd.DataFrame:
    """Evaluate alternate cluster counts using inertia and silhouette score."""
    feature_cols = [
        'recency_proxy',
        'frequency_proxy',
        'monetary_proxy',
        'service_depth_proxy',
        'commitment_proxy',
        'churn_risk_proxy',
    ]

    scaler = StandardScaler()
    scaled_features = scaler.fit_transform(df[feature_cols])

    rows = []
    for n_clusters in cluster_range:
        model = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        labels = model.fit_predict(scaled_features)
        score = silhouette_score(scaled_features, labels) if n_clusters > 1 else 0.0
        rows.append(
            {
                'n_clusters': n_clusters,
                'inertia': round(float(model.inertia_), 4),
                'silhouette_score': round(float(score), 4),
            }
        )

    return pd.DataFrame(rows)


def build_segment_report(df: pd.DataFrame, report_path: str) -> None:
    """Create a markdown report describing the discovered segments."""
    out_path = Path(report_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    segment_summary = (
        df.groupby(['segment_id', 'segment_label'])
        .agg(
            customers=('customerID', 'count'),
            avg_tenure=('tenure_normalized', 'mean'),
            avg_monthly=('MonthlyCharges_normalized', 'mean'),
            avg_total=('TotalCharges_normalized', 'mean'),
            avg_addons=('addon_count', 'mean'),
            avg_risk=('churn_risk_proxy', 'mean'),
            churn_rate=('Churn_encoded', 'mean'),
        )
        .reset_index()
        .sort_values('customers', ascending=False)
    )

    total_customers = len(df)
    churn_count = int(df['Churn_encoded'].sum())
    segment_count = int(df['segment_id'].nunique())
    stability = evaluate_cluster_stability(df)
    best_cluster_row = stability.sort_values(['silhouette_score', 'inertia'], ascending=[False, True]).iloc[0]

    playbooks = {
        'At-Risk New Customers': [
            'Trigger: tenure under 6 months or low add-on adoption.',
            'Action: launch a guided onboarding sequence with first-30-day check-ins.',
            'Action: push auto-pay adoption and simplify first-bill resolution.',
            'KPI: reduce early-stage churn exposure and increase addon_count within 60 days.',
        ],
        'Low Engagement Churn Risk': [
            'Trigger: moderate tenure with weak bundle adoption and elevated risk proxy.',
            'Action: run targeted engagement nudges and service-bundle offers.',
            'Action: review support friction and unresolved service issues.',
            'KPI: lift service_depth_proxy and lower churn_risk_proxy over 90 days.',
        ],
        'High Value Loyalists': [
            'Trigger: long tenure, higher monetary value, and strong service adoption.',
            'Action: provide loyalty rewards, premium support, and proactive renewal outreach.',
            'Action: cross-sell value-added services instead of discount-led interventions.',
            'KPI: preserve retention while expanding average add-on count and value.',
        ],
        'Stable Value Seekers': [
            'Trigger: stable tenure and moderate value with balanced service usage.',
            'Action: maintain price transparency and promote low-friction self-service.',
            'Action: cross-sell carefully to avoid churn-inducing complexity.',
            'KPI: sustain retention and gradually increase service adoption efficiency.',
        ],
    }

    lines = [
        '# Customer Segmentation Report',
        '## Phase 7 - RFM-Style Clustering',
        '',
        '**Generated:** 2026-06-24  ',
        '**Input Dataset:** `data/processed/telco_customer_churn_engineered.csv`  ',
        '**Output Dataset:** `data/processed/telco_customer_churn_segments.csv`  ',
        '**Status:** In Progress - Segment profiles generated',
        '',
        '---',
        '',
        '## Summary',
        '',
        f'- Customers segmented: {total_customers:,}',
        f'- Churn labels available in snapshot: {churn_count:,}',
        f'- Segment count: {segment_count}',
        '',
        '## Segmentation Features',
        '',
        '- `recency_proxy`',
        '- `frequency_proxy`',
        '- `monetary_proxy`',
        '- `service_depth_proxy`',
        '- `commitment_proxy`',
        '- `churn_risk_proxy`',
        '',
        '## Segment Profiles',
        '',
    ]

    for _, row in segment_summary.iterrows():
        lines.extend(
            [
                f'### {row["segment_label"]}',
                '',
                f'- Segment ID: {int(row["segment_id"])}',
                f'- Customers: {int(row["customers"]):,}',
                f'- Average tenure proxy: {row["avg_tenure"]:.4f}',
                f'- Average monthly charge proxy: {row["avg_monthly"]:.4f}',
                f'- Average total charge proxy: {row["avg_total"]:.4f}',
                f'- Average add-on count: {row["avg_addons"]:.2f}',
                f'- Average risk proxy: {row["avg_risk"]:.4f}',
                f'- Churn rate: {row["churn_rate"] * 100:.2f}%',
                '',
            ]
        )

    lines.extend(
        [
            '## Stability Check',
            '',
        ]
    )

    for _, row in stability.iterrows():
        lines.extend(
            [
                f'- k={int(row["n_clusters"])} | inertia={row["inertia"]:.4f} | silhouette={row["silhouette_score"]:.4f}',
            ]
        )

    lines.extend(
        [
            '',
            '## Retention Playbooks',
            '',
        ]
    )

    for segment_label, actions in playbooks.items():
        lines.extend([f'### {segment_label}', ''])
        for action in actions:
            lines.append(f'- {action}')
        lines.append('')

    lines.extend(
        [
            '',
            f'- Best balance observed at k={int(best_cluster_row["n_clusters"])} by silhouette score.',
            '',
            '## Notes',
            '',
            '- Segment labels are business-friendly summaries mapped from clustering output.',
            '- Recency and monetary proxies preserve ordering for behavioral interpretation.',
            '- Churn rate is shown only as an exploratory snapshot because the current dataset has no positive churn cases.',
            '',
            '## Next Steps',
            '',
            '1. Validate segment stability across alternate cluster counts.',
            '2. Use retention playbooks to drive segment-level interventions and dashboard views.',
            '3. Use segmentation output as a feature for CLV and recommendation analyses.',
        ]
    )

    out_path.write_text('\n'.join(lines), encoding='utf-8')


def save_segments(df: pd.DataFrame, output_csv: str) -> None:
    """Save segmented dataset."""
    out_path = Path(output_csv)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_path, index=False)


def run_segmentation(
    engineered_csv: str,
    output_csv: str,
    report_path: str,
) -> None:
    """Run the full segmentation workflow."""
    print('Loading engineered dataset...')
    df = load_engineered_data(engineered_csv)
    print(f'  Records loaded: {len(df):,}')

    print('Creating segmentation features...')
    seg_df = create_segmentation_features(df)

    print('Evaluating cluster stability...')
    stability = evaluate_cluster_stability(seg_df)
    for _, row in stability.iterrows():
        print(f"  k={int(row['n_clusters'])}: inertia={row['inertia']:.4f}, silhouette={row['silhouette_score']:.4f}")

    print('Running clustering...')
    clustered_df = run_clustering(seg_df)
    print(f'  Segments discovered: {clustered_df["segment_id"].nunique()}')

    print('Saving segmented dataset...')
    save_segments(clustered_df, output_csv)

    print('Building Phase 7 report...')
    build_segment_report(clustered_df, report_path)

    print('✓ Phase 7 started: segmentation dataset and report generated')


if __name__ == '__main__':
    run_segmentation(
        engineered_csv='data/processed/telco_customer_churn_engineered.csv',
        output_csv='data/processed/telco_customer_churn_segments.csv',
        report_path='reports/customer_segmentation_report.md',
    )