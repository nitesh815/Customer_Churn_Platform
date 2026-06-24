"""
Phase 11 SQL analytics layer builder.

This utility:
1. Loads CLV-enriched data into SQLite
2. Applies SQL analytics views from sql/analytics_layer.sql
3. Runs representative SQL queries
4. Writes a markdown report with query outputs
"""

from pathlib import Path
import sqlite3

import pandas as pd


def load_clv_data(csv_path: str) -> pd.DataFrame:
    """Load CLV-enriched dataset for SQL layer materialization."""
    df = pd.read_csv(csv_path)
    if df.empty:
        raise ValueError('CLV dataset is empty')
    return df


def build_sqlite_layer(df: pd.DataFrame, db_path: str, sql_path: str) -> None:
    """Create SQLite table and analytics views."""
    db_file = Path(db_path)
    db_file.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(db_file) as conn:
        df.to_sql('customer_analytics', conn, if_exists='replace', index=False)
        sql_text = Path(sql_path).read_text(encoding='utf-8')
        conn.executescript(sql_text)


def query_to_markdown(conn: sqlite3.Connection, query: str, title: str) -> list[str]:
    """Run SQL query and return markdown block lines."""
    df = pd.read_sql_query(query, conn)
    lines = [f'## {title}', '']

    if df.empty:
        lines.extend(['_No rows returned._', ''])
        return lines

    lines.append('| ' + ' | '.join(df.columns) + ' |')
    lines.append('|' + '|'.join(['---'] * len(df.columns)) + '|')

    for _, row in df.iterrows():
        values = []
        for value in row.values:
            if isinstance(value, float):
                values.append(f'{value:.4f}'.rstrip('0').rstrip('.'))
            else:
                values.append(str(value))
        lines.append('| ' + ' | '.join(values) + ' |')

    lines.append('')
    return lines


def run_sql_quality_checks(conn: sqlite3.Connection) -> pd.DataFrame:
    """Run SQL validation checks for view consistency and data integrity."""
    checks = [
        (
            'row_count_match_overview',
            'SELECT (SELECT COUNT(*) FROM customer_analytics) = (SELECT customers FROM vw_churn_overview) AS passed;',
            'Base table row count matches churn overview total.',
        ),
        (
            'segment_sum_matches_base',
            'SELECT (SELECT SUM(customers) FROM vw_segment_kpis) = (SELECT COUNT(*) FROM customer_analytics) AS passed;',
            'Sum of segment customers matches base row count.',
        ),
        (
            'contract_sum_matches_base',
            'SELECT (SELECT SUM(customers) FROM vw_contract_retention) = (SELECT COUNT(*) FROM customer_analytics) AS passed;',
            'Sum of contract customers matches base row count.',
        ),
        (
            'clv_band_sum_matches_base',
            'SELECT (SELECT SUM(customers) FROM vw_clv_bands) = (SELECT COUNT(*) FROM customer_analytics) AS passed;',
            'Sum of CLV band customers matches base row count.',
        ),
        (
            'churn_rate_bounds',
            'SELECT (SELECT churn_rate_pct FROM vw_churn_overview) BETWEEN 0 AND 100 AS passed;',
            'Overall churn rate is within 0-100%.',
        ),
        (
            'non_null_customer_id',
            'SELECT (SELECT COUNT(*) FROM customer_analytics WHERE customerID IS NULL OR customerID = "") = 0 AS passed;',
            'No NULL/blank customer IDs in base table.',
        ),
    ]

    rows = []
    for check_name, query, description in checks:
        value = pd.read_sql_query(query, conn).iloc[0, 0]
        passed = bool(value)
        rows.append(
            {
                'check_name': check_name,
                'status': 'PASS' if passed else 'FAIL',
                'description': description,
            }
        )

    return pd.DataFrame(rows)


def quality_checks_to_markdown(df: pd.DataFrame) -> list[str]:
    """Render quality check results as markdown."""
    lines = ['## SQL Quality Checks', '']
    lines.append('| Check | Status | Description |')
    lines.append('|---|---|---|')
    for _, row in df.iterrows():
        lines.append(f"| {row['check_name']} | {row['status']} | {row['description']} |")
    lines.append('')
    return lines


def save_quality_checks(df: pd.DataFrame, output_csv: str) -> None:
    """Persist SQL quality-check results."""
    out_path = Path(output_csv)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_path, index=False)


def load_sql_templates(template_sql_path: str) -> str:
    """Load dashboard SQL template text for documentation/reporting."""
    return Path(template_sql_path).read_text(encoding='utf-8')


def build_sql_report(db_path: str, report_path: str, quality_df: pd.DataFrame, template_sql_text: str) -> None:
    """Generate SQL analytics report from SQLite views."""
    report_file = Path(report_path)
    report_file.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(db_path) as conn:
        lines = [
            '# SQL Analytics Layer Report',
            '## Phase 11 - Relational KPI Views',
            '',
            '**Generated:** 2026-06-24  ',
            '**Database:** `data/processed/churn_analytics.db`  ',
            '**Source Table:** `customer_analytics`  ',
            '**Status:** In Progress - Views, quality checks, and templates generated',
            '',
            '---',
            '',
            '## View Inventory',
            '',
            '- `vw_churn_overview`',
            '- `vw_segment_kpis`',
            '- `vw_contract_retention`',
            '- `vw_clv_bands`',
            '- `vw_top_risk_customers`',
            '',
        ]

        lines.extend(
            query_to_markdown(
                conn,
                'SELECT * FROM vw_churn_overview;',
                'Churn Overview',
            )
        )

        lines.extend(
            query_to_markdown(
                conn,
                'SELECT * FROM vw_segment_kpis;',
                'Segment KPIs',
            )
        )

        lines.extend(
            query_to_markdown(
                conn,
                'SELECT * FROM vw_contract_retention;',
                'Contract Retention',
            )
        )

        lines.extend(
            query_to_markdown(
                conn,
                'SELECT * FROM vw_clv_bands;',
                'CLV Bands',
            )
        )

        lines.extend(
            query_to_markdown(
                conn,
                'SELECT * FROM vw_top_risk_customers LIMIT 10;',
                'Top Risk Customers (Top 10)',
            )
        )

        lines.extend(quality_checks_to_markdown(quality_df))

        lines.extend(
            [
                '## Parameterized Dashboard Query Templates',
                '',
                'The following templates are available in `sql/dashboard_query_templates.sql` for dashboard filters and drill-downs:',
                '',
                '```sql',
                template_sql_text.strip(),
                '```',
                '',
            ]
        )

        lines.extend(
            [
                '## Next Steps',
                '',
                '1. Connect SQL views and parameterized templates to Power BI semantic model.',
                '2. Add refresh monitoring checks for production readiness.',
                '3. Add dashboard-level query performance benchmarks.',
            ]
        )

    report_file.write_text('\n'.join(lines), encoding='utf-8')


def run_phase11(
    clv_csv: str,
    db_path: str,
    sql_path: str,
    template_sql_path: str,
    quality_checks_csv: str,
    report_path: str,
) -> None:
    """Execute Phase 11 SQL layer build and reporting workflow."""
    print('Loading CLV dataset...')
    df = load_clv_data(clv_csv)
    print(f'  Records loaded: {len(df):,}')

    print('Building SQLite analytics layer...')
    build_sqlite_layer(df, db_path, sql_path)

    print('Running SQL quality checks...')
    with sqlite3.connect(db_path) as conn:
        quality_df = run_sql_quality_checks(conn)
    save_quality_checks(quality_df, quality_checks_csv)

    print('Loading dashboard query templates...')
    template_sql_text = load_sql_templates(template_sql_path)

    print('Generating SQL analytics report...')
    build_sql_report(db_path, report_path, quality_df, template_sql_text)

    print('✓ Phase 11 started: SQL analytics layer and report generated')


if __name__ == '__main__':
    run_phase11(
        clv_csv='data/processed/telco_customer_churn_clv.csv',
        db_path='data/processed/churn_analytics.db',
        sql_path='sql/analytics_layer.sql',
        template_sql_path='sql/dashboard_query_templates.sql',
        quality_checks_csv='reports/sql_quality_checks.csv',
        report_path='reports/sql_analytics_report.md',
    )