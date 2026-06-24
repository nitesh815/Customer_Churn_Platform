"""
Predictive modeling module for customer churn analytics platform.

This module handles:
1. Modeling readiness checks on the CLV-enriched dataset
2. Train/validation splitting when the target contains both classes
3. Baseline model training and comparison
4. Generation of a Phase 9 markdown report
"""

from pathlib import Path

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

try:
    from xgboost import XGBClassifier
    HAS_XGBOOST = True
except ImportError:
    HAS_XGBOOST = False


TARGET_COLUMN = 'Churn_encoded'


def load_modeling_data(csv_path: str) -> pd.DataFrame:
    """Load the CLV-enriched modeling dataset."""
    df = pd.read_csv(csv_path)
    if df.empty:
        raise ValueError('Modeling dataset is empty')
    return df


def split_features_target(df: pd.DataFrame):
    """Split dataframe into features and target, dropping leakage-prone identifiers."""
    if TARGET_COLUMN not in df.columns:
        raise KeyError(f'Missing target column: {TARGET_COLUMN}')

    y = df[TARGET_COLUMN].astype(int)
    feature_columns = [
        column
        for column in df.columns
        if column not in {TARGET_COLUMN, 'customerID', 'risk_proxy_bucket', 'segment_label'}
    ]
    X = df[feature_columns].copy()
    return X, y


def validate_target_classes(y: pd.Series) -> dict:
    """Validate target class counts and return a summary."""
    class_counts = y.value_counts().to_dict()
    unique_classes = len(class_counts)
    return {
        'class_counts': class_counts,
        'unique_classes': unique_classes,
        'has_positive_class': 1 in class_counts,
        'has_negative_class': 0 in class_counts,
    }


def train_baseline_models(X: pd.DataFrame, y: pd.Series) -> pd.DataFrame:
    """Train baseline models and return comparison metrics."""
    X_train, X_valid, y_train, y_valid = train_test_split(
        X,
        y,
        test_size=0.20,
        random_state=42,
        stratify=y,
    )

    models = {
        'Logistic Regression': Pipeline(
            steps=[
                ('scaler', StandardScaler()),
                ('model', LogisticRegression(max_iter=1000, random_state=42)),
            ]
        ),
        'Random Forest': RandomForestClassifier(
            n_estimators=300,
            max_depth=None,
            random_state=42,
            n_jobs=-1,
            class_weight='balanced_subsample',
        ),
    }

    if HAS_XGBOOST:
        models['XGBoost'] = XGBClassifier(
            n_estimators=300,
            max_depth=6,
            learning_rate=0.05,
            subsample=0.9,
            colsample_bytree=0.9,
            objective='binary:logistic',
            eval_metric='logloss',
            random_state=42,
            n_jobs=-1,
        )

    rows = []
    for model_name, model in models.items():
        model.fit(X_train, y_train)
        y_pred = model.predict(X_valid)

        if hasattr(model, 'predict_proba'):
            y_prob = model.predict_proba(X_valid)[:, 1]
            auc = roc_auc_score(y_valid, y_prob)
        else:
            auc = float('nan')

        rows.append(
            {
                'model': model_name,
                'accuracy': round(float(accuracy_score(y_valid, y_pred)), 4),
                'precision': round(float(precision_score(y_valid, y_pred, zero_division=0)), 4),
                'recall': round(float(recall_score(y_valid, y_pred, zero_division=0)), 4),
                'f1': round(float(f1_score(y_valid, y_pred, zero_division=0)), 4),
                'roc_auc': round(float(auc), 4),
            }
        )

    return pd.DataFrame(rows).sort_values('roc_auc', ascending=False)


def build_readiness_report(
    df: pd.DataFrame,
    target_summary: dict,
    report_path: str,
    results_df: pd.DataFrame | None = None,
) -> None:
    """Write a Phase 9 readiness report to disk."""
    out_path = Path(report_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    class_counts = target_summary['class_counts']
    total_rows = len(df)
    feature_count = len([column for column in df.columns if column not in {'Churn_encoded'}])
    positive_count = int(class_counts.get(1, 0))
    negative_count = int(class_counts.get(0, 0))
    is_trainable = target_summary['unique_classes'] >= 2
    has_results = results_df is not None and not results_df.empty
    status_line = (
        'In Progress - Baseline models trained'
        if has_results
        else ('In Progress - Ready for baseline model training' if is_trainable else 'Blocked - Target class imbalance unresolved')
    )
    class_check = '[x]' if is_trainable else '[ ]'
    train_check = '[x]' if has_results else '[ ]'
    compare_check = '[x]' if has_results else '[ ]'

    lines = [
        '# Predictive Modeling Readiness Report',
        '## Phase 9 - Baseline Modeling Gate',
        '',
        '**Generated:** 2026-06-24  ',
        '**Input Dataset:** `data/processed/telco_customer_churn_clv.csv`  ',
        f'**Status:** {status_line}',
        '',
        '---',
        '',
        '## Summary',
        '',
        f'- Records evaluated: {total_rows:,}',
        f'- Candidate features: {feature_count}',
        f'- Target classes present: {target_summary["unique_classes"]}',
        f'- Class 0 count: {negative_count:,}',
        f'- Class 1 count: {positive_count:,}',
        '',
        '## Readiness Checks',
        '',
        '- [x] Modeling dataset loaded successfully',
        '- [x] Leakage-prone identifiers can be excluded from feature matrix',
        '- [x] Target distribution validated',
        f'- {class_check} Both churn classes available for supervised training',
        f'- {train_check} Baseline model training',
        f'- {compare_check} Model comparison and selection',
        '',
        '## Blocking Issue',
        '',
        (
            'No blocking issue detected for target classes. Supervised model training can proceed.'
            if is_trainable
            else 'The current workspace snapshot contains only class 0 for `Churn_encoded`, so no supervised classifier can be trained without regenerating the source dataset with positive churn examples.'
        ),
        '',
        '## Planned Model Stack',
        '',
        '- Logistic Regression baseline',
        '- Random Forest classifier',
        '- XGBoost classifier',
    ]

    if has_results:
        champion = results_df.iloc[0]
        lines.extend(
            [
                '',
                '## Baseline Model Results',
                '',
                '| Model | Accuracy | Precision | Recall | F1 | ROC AUC |',
                '|---|---:|---:|---:|---:|---:|',
            ]
        )

        for _, row in results_df.iterrows():
            lines.append(
                f'| {row["model"]} | {row["accuracy"]:.4f} | {row["precision"]:.4f} | {row["recall"]:.4f} | {row["f1"]:.4f} | {row["roc_auc"]:.4f} |'
            )

        lines.extend(
            [
                '',
                f'- Current champion by ROC AUC: **{champion["model"]}** ({champion["roc_auc"]:.4f})',
                '',
            ]
        )

    lines.extend(
        [
            '## Next Steps',
            '',
            '1. Tune top model hyperparameters with cross-validation.',
            '2. Add threshold analysis for recall/precision trade-offs.',
            '3. Promote champion model into Phase 10 explainability workflow.',
        ]
    )

    out_path.write_text('\n'.join(lines), encoding='utf-8')


def run_modeling_gate(modeling_csv: str, report_path: str) -> None:
    """Run Phase 9 readiness checks and write a report."""
    print('Loading modeling dataset...')
    df = load_modeling_data(modeling_csv)
    print(f'  Records loaded: {len(df):,}')

    print('Checking target distribution...')
    X, y = split_features_target(df)
    target_summary = validate_target_classes(y)
    class_counts = target_summary['class_counts']
    print(f"  Target distribution: {class_counts}")

    if target_summary['unique_classes'] < 2:
        build_readiness_report(df, target_summary, report_path)
        print('! Phase 9 blocked: supervised training requires both churn classes')
        return

    print('Training baseline models...')
    results_df = train_baseline_models(X, y)
    if not HAS_XGBOOST:
        print('  Note: xgboost is not installed in the current environment; skipped XGBoost model')
    print(results_df.to_string(index=False))

    build_readiness_report(df, target_summary, report_path, results_df)
    print('✓ Phase 9 baseline model training complete')


if __name__ == '__main__':
    run_modeling_gate(
        modeling_csv='data/processed/telco_customer_churn_clv.csv',
        report_path='reports/predictive_modeling_readiness_report.md',
    )