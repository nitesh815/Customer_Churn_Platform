"""
Explainable AI module for customer churn analytics platform.

This module handles:
1. Candidate model retraining for explainability consistency
2. Champion selection by validation ROC AUC
3. Feature attribution via permutation importance and model-specific signals
4. Generation of Phase 10 explainability artifacts
"""

from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.inspection import permutation_importance
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

TARGET_COLUMN = 'Churn_encoded'


def load_modeling_data(csv_path: str) -> pd.DataFrame:
    """Load the CLV-enriched dataset used for model explainability."""
    df = pd.read_csv(csv_path)
    if df.empty:
        raise ValueError('Modeling dataset is empty')
    return df


def split_features_target(df: pd.DataFrame):
    """Split dataframe into model features and target."""
    y = df[TARGET_COLUMN].astype(int)
    feature_columns = [
        column
        for column in df.columns
        if column not in {TARGET_COLUMN, 'customerID', 'risk_proxy_bucket', 'segment_label'}
    ]
    X = df[feature_columns].copy()
    return X, y


def train_candidate_models(X: pd.DataFrame, y: pd.Series):
    """Train candidate models and return train/validation artifacts."""
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
            random_state=42,
            n_jobs=-1,
            class_weight='balanced_subsample',
        ),
    }

    scores = []
    fitted_models = {}
    for name, model in models.items():
        model.fit(X_train, y_train)
        y_prob = model.predict_proba(X_valid)[:, 1]
        auc = roc_auc_score(y_valid, y_prob)
        scores.append({'model': name, 'roc_auc': round(float(auc), 4)})
        fitted_models[name] = model

    scores_df = pd.DataFrame(scores).sort_values('roc_auc', ascending=False)
    champion_name = scores_df.iloc[0]['model']
    champion_model = fitted_models[champion_name]

    return {
        'X_train': X_train,
        'X_valid': X_valid,
        'y_train': y_train,
        'y_valid': y_valid,
        'scores_df': scores_df,
        'champion_name': champion_name,
        'champion_model': champion_model,
    }


def compute_feature_explanations(champion_name: str, champion_model, X_valid: pd.DataFrame, y_valid: pd.Series) -> pd.DataFrame:
    """Compute explanation table with permutation and model-specific signals."""
    perm = permutation_importance(
        champion_model,
        X_valid,
        y_valid,
        scoring='roc_auc',
        n_repeats=5,
        random_state=42,
        n_jobs=-1,
    )

    explanation_df = pd.DataFrame(
        {
            'feature': X_valid.columns,
            'permutation_importance_mean': perm.importances_mean,
            'permutation_importance_std': perm.importances_std,
        }
    )

    if champion_name == 'Logistic Regression':
        coef = champion_model.named_steps['model'].coef_[0]
        explanation_df['model_specific_importance'] = coef
        explanation_df['model_specific_abs_importance'] = abs(coef)
    else:
        explanation_df['model_specific_importance'] = champion_model.feature_importances_
        explanation_df['model_specific_abs_importance'] = champion_model.feature_importances_

    explanation_df = explanation_df.sort_values(
        ['permutation_importance_mean', 'model_specific_abs_importance'],
        ascending=False,
    )
    return explanation_df


def compute_local_reason_codes(champion_name: str, champion_model, X_all: pd.DataFrame, top_n_customers: int = 50) -> pd.DataFrame:
    """Create local reason codes for highest-risk customers."""
    if not hasattr(champion_model, 'predict_proba'):
        raise ValueError('Champion model must support predict_proba for local reason codes')

    risk_scores = champion_model.predict_proba(X_all)[:, 1]
    scored_df = pd.DataFrame({'row_id': np.arange(len(X_all)), 'predicted_churn_risk': risk_scores})
    top_rows = scored_df.nlargest(top_n_customers, 'predicted_churn_risk')

    reasons = []

    if champion_name == 'Logistic Regression':
        scaler = champion_model.named_steps['scaler']
        model = champion_model.named_steps['model']
        X_scaled = scaler.transform(X_all)
        coef = model.coef_[0]

        for _, row in top_rows.iterrows():
            idx = int(row['row_id'])
            contrib = X_scaled[idx] * coef
            feature_order = np.argsort(-contrib)
            for rank, feat_idx in enumerate(feature_order[:3], start=1):
                reasons.append(
                    {
                        'row_id': idx,
                        'predicted_churn_risk': round(float(row['predicted_churn_risk']), 6),
                        'reason_rank': rank,
                        'feature': X_all.columns[int(feat_idx)],
                        'feature_contribution': round(float(contrib[int(feat_idx)]), 6),
                    }
                )
    else:
        importances = None
        if hasattr(champion_model, 'feature_importances_'):
            importances = champion_model.feature_importances_
        if importances is None:
            raise ValueError('Cannot derive local reason codes for this champion model type')

        top_feature_idx = np.argsort(-importances)[:3]
        for _, row in top_rows.iterrows():
            idx = int(row['row_id'])
            for rank, feat_idx in enumerate(top_feature_idx, start=1):
                reasons.append(
                    {
                        'row_id': idx,
                        'predicted_churn_risk': round(float(row['predicted_churn_risk']), 6),
                        'reason_rank': rank,
                        'feature': X_all.columns[int(feat_idx)],
                        'feature_contribution': round(float(importances[int(feat_idx)]), 6),
                    }
                )

    return pd.DataFrame(reasons).sort_values(['predicted_churn_risk', 'reason_rank'], ascending=[False, True])


def evaluate_explanation_stability(X: pd.DataFrame, y: pd.Series, seeds: tuple[int, ...] = (7, 42, 99)) -> pd.DataFrame:
    """Measure stability of top global explanations across alternate random splits."""
    rows = []
    seed_top_features = {}

    for seed in seeds:
        X_train, X_valid, y_train, y_valid = train_test_split(
            X,
            y,
            test_size=0.20,
            random_state=seed,
            stratify=y,
        )

        model = Pipeline(
            steps=[
                ('scaler', StandardScaler()),
                ('model', LogisticRegression(max_iter=1000, random_state=seed)),
            ]
        )
        model.fit(X_train, y_train)
        y_prob = model.predict_proba(X_valid)[:, 1]
        auc = roc_auc_score(y_valid, y_prob)

        perm = permutation_importance(
            model,
            X_valid,
            y_valid,
            scoring='roc_auc',
            n_repeats=3,
            random_state=seed,
            n_jobs=-1,
        )
        perm_df = pd.DataFrame({'feature': X_valid.columns, 'importance': perm.importances_mean})
        top_features = perm_df.sort_values('importance', ascending=False).head(10)['feature'].tolist()
        seed_top_features[seed] = set(top_features)

        rows.append({'seed': seed, 'roc_auc': round(float(auc), 4), 'top10_features': ', '.join(top_features)})

    baseline_seed = seeds[0]
    baseline_features = seed_top_features[baseline_seed]

    for row in rows:
        current_features = seed_top_features[row['seed']]
        union = baseline_features.union(current_features)
        jaccard = (len(baseline_features.intersection(current_features)) / len(union)) if union else 1.0
        row['jaccard_vs_seed_' + str(baseline_seed)] = round(float(jaccard), 4)

    return pd.DataFrame(rows)


def save_explanations(df: pd.DataFrame, output_csv: str) -> None:
    """Save feature explanation table."""
    out_path = Path(output_csv)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_path, index=False)


def save_local_reason_codes(df: pd.DataFrame, output_csv: str) -> None:
    """Save local explanation reason codes."""
    out_path = Path(output_csv)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_path, index=False)


def save_stability_results(df: pd.DataFrame, output_csv: str) -> None:
    """Save explanation stability metrics."""
    out_path = Path(output_csv)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_path, index=False)


def build_explainability_report(
    scores_df: pd.DataFrame,
    champion_name: str,
    explanation_df: pd.DataFrame,
    local_reasons_df: pd.DataFrame,
    stability_df: pd.DataFrame,
    report_path: str,
) -> None:
    """Generate a markdown explainability report for Phase 10."""
    out_path = Path(report_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    top_features = explanation_df.head(15)

    lines = [
        '# Explainable AI Report',
        '## Phase 10 - Model Interpretability',
        '',
        '**Generated:** 2026-06-24  ',
        '**Input Dataset:** `data/processed/telco_customer_churn_clv.csv`  ',
        '**Output Artifacts:** `reports/feature_explanations.csv`, `reports/local_reason_codes.csv`, `reports/explanation_stability.csv`  ',
        '**Status:** In Progress - Global and local explanations generated',
        '',
        '---',
        '',
        '## Candidate Model Performance',
        '',
        '| Model | ROC AUC |',
        '|---|---:|',
    ]

    for _, row in scores_df.iterrows():
        lines.append(f'| {row["model"]} | {row["roc_auc"]:.4f} |')

    lines.extend(
        [
            '',
            f'- Champion model: **{champion_name}**',
            '',
            '## Top Feature Explanations',
            '',
            '| Feature | Permutation Importance | Model-Specific Importance |',
            '|---|---:|---:|',
        ]
    )

    for _, row in top_features.iterrows():
        lines.append(
            f'| {row["feature"]} | {row["permutation_importance_mean"]:.6f} | {row["model_specific_importance"]:.6f} |'
        )

    lines.extend(
        [
            '',
            '## Local Reason Codes (Top 10 High-Risk Customers)',
            '',
            '| Row ID | Predicted Risk | Reason Rank | Feature | Contribution |',
            '|---:|---:|---:|---|---:|',
        ]
    )

    preview_rows = local_reasons_df.head(30)
    for _, row in preview_rows.iterrows():
        lines.append(
            f'| {int(row["row_id"])} | {row["predicted_churn_risk"]:.6f} | {int(row["reason_rank"])} | {row["feature"]} | {row["feature_contribution"]:.6f} |'
        )

    lines.extend(
        [
            '',
            '## Explanation Stability Across Alternate Splits',
            '',
            '| Seed | ROC AUC | Jaccard vs Seed 7 |',
            '|---:|---:|---:|',
        ]
    )

    for _, row in stability_df.iterrows():
        lines.append(
            f'| {int(row["seed"])} | {row["roc_auc"]:.4f} | {row["jaccard_vs_seed_7"]:.4f} |'
        )

    lines.extend(
        [
            '',
            '## Interpretation Guidance',
            '',
            '- Features with consistently high permutation and model-specific importance are strongest global drivers.',
            '- Positive logistic coefficients increase churn risk score; negative coefficients reduce risk.',
            '- Local reason codes can be attached to customer records for intervention workflows.',
            '- Stability table shows whether top drivers are robust across alternate splits.',
            '',
            '## Next Steps',
            '',
            '1. Validate stability across time windows in addition to random split seeds.',
            '2. Publish model cards and explanation summaries for business stakeholders.',
            '3. Connect reason codes into dashboard and retention operations workflows.',
        ]
    )

    out_path.write_text('\n'.join(lines), encoding='utf-8')


def run_explainability_pipeline(
    modeling_csv: str,
    explanation_csv: str,
    local_reason_codes_csv: str,
    stability_csv: str,
    report_path: str,
) -> None:
    """Run full explainability workflow for Phase 10."""
    print('Loading modeling dataset...')
    df = load_modeling_data(modeling_csv)
    print(f'  Records loaded: {len(df):,}')

    X, y = split_features_target(df)
    class_count = y.nunique()
    print(f'  Target classes detected: {class_count}')
    if class_count < 2:
        raise ValueError('Explainability requires a trainable two-class target')

    print('Training candidate models for explainability...')
    outputs = train_candidate_models(X, y)
    print(outputs['scores_df'].to_string(index=False))

    print('Computing feature explanations...')
    explanation_df = compute_feature_explanations(
        champion_name=outputs['champion_name'],
        champion_model=outputs['champion_model'],
        X_valid=outputs['X_valid'],
        y_valid=outputs['y_valid'],
    )

    print('Computing local reason codes...')
    local_reasons_df = compute_local_reason_codes(
        champion_name=outputs['champion_name'],
        champion_model=outputs['champion_model'],
        X_all=X,
        top_n_customers=50,
    )

    print('Evaluating explanation stability...')
    stability_df = evaluate_explanation_stability(X, y)

    print('Saving explanation artifacts...')
    save_explanations(explanation_df, explanation_csv)
    save_local_reason_codes(local_reasons_df, local_reason_codes_csv)
    save_stability_results(stability_df, stability_csv)
    build_explainability_report(
        scores_df=outputs['scores_df'],
        champion_name=outputs['champion_name'],
        explanation_df=explanation_df,
        local_reasons_df=local_reasons_df,
        stability_df=stability_df,
        report_path=report_path,
    )

    print('✓ Phase 10 started: explainability artifacts generated')


if __name__ == '__main__':
    run_explainability_pipeline(
        modeling_csv='data/processed/telco_customer_churn_clv.csv',
        explanation_csv='reports/feature_explanations.csv',
        local_reason_codes_csv='reports/local_reason_codes.csv',
        stability_csv='reports/explanation_stability.csv',
        report_path='reports/explainable_ai_report.md',
    )