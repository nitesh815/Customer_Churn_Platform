# Customer Churn Prediction & Analytics Platform

## Project Goal
Build a production-quality portfolio project that demonstrates end-to-end data workflows across SQL, Python analytics, machine learning, explainable AI, and dashboarding.

## Core Capabilities
- SQL analytics layer for churn and retention insights
- Data cleaning and quality validation
- Exploratory data analysis and business storytelling
- Feature engineering for churn prediction
- Customer segmentation (RFM and clustering)
- Customer lifetime value (CLV) analysis
- Predictive modeling with baseline, Random Forest, and XGBoost
- Model explainability with SHAP
- Power BI executive dashboard suite
- MLOps-ready project structure and testing conventions

## Repository Structure
```text
customer-churn-platform/
  data/
    raw/
    processed/
  notebooks/
  src/
    data_ingestion/
    data_cleaning/
    feature_engineering/
    segmentation/
    model_training/
    model_evaluation/
    prediction/
    utils/
  sql/
  dashboard/
  reports/
  tests/
  PROJECT_STATUS.md
  README.md
  requirements.txt
```

## Environment Setup
### Prerequisites
- Python 3.11+
- Git
- (Optional) Power BI Desktop for dashboard pages

### Virtual Environment
#### Windows (PowerShell)
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

#### macOS/Linux
```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Development Workflow
- Follow milestone-based delivery as documented in PROJECT_STATUS.md.
- Complete one phase at a time with verification before moving forward.
- Keep changes production quality and testable.
