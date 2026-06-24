# Telco Customer Churn Dataset - Data Dictionary

## Dataset Overview
- **Source**: Synthetic but realistic telecom customer dataset (mirrors public Telco Customer Churn dataset)
- **Records**: 7,043 customers
- **Columns**: 21 features + 1 target variable (Churn)
- **File**: `data/raw/telco_customer_churn.csv`
- **File Size**: ~1 MB
- **Generated**: 2026-06-24

## Target Variable
| Column | Type | Description | Values |
|--------|------|-------------|--------|
| **Churn** | Categorical | Whether customer left the company | Yes, No |

## Demographic Features
| Column | Type | Description | Example |
|--------|------|-------------|---------|
| customerID | String | Unique customer identifier | ID-000001 |
| gender | Categorical | Customer gender | Male, Female |
| SeniorCitizen | Binary | Whether customer is senior (65+) | 0, 1 |
| Partner | Categorical | Whether customer has a partner | Yes, No |
| Dependent | Categorical | Whether customer has dependents | Yes, No |
| tenure | Numeric | Months customer has been with company | 0-72 |

## Service Subscription Features
| Column | Type | Description | Values |
|--------|------|-------------|--------|
| PhoneService | Categorical | Whether customer has phone service | Yes, No |
| MultipleLines | Categorical | Whether customer has multiple phone lines | Yes, No, No phone service |
| InternetService | Categorical | Type of internet service | Fiber optic, DSL, No |
| OnlineSecurity | Categorical | Whether customer has online security add-on | Yes, No, No internet service |
| OnlineBackup | Categorical | Whether customer has online backup add-on | Yes, No, No internet service |
| DeviceProtection | Categorical | Whether customer has device protection add-on | Yes, No, No internet service |
| TechSupport | Categorical | Whether customer has tech support add-on | Yes, No, No internet service |
| StreamingTV | Categorical | Whether customer has streaming TV service | Yes, No, No internet service |
| StreamingMovies | Categorical | Whether customer has streaming movies service | Yes, No, No internet service |

## Account Features
| Column | Type | Description | Values |
|--------|------|-------------|--------|
| Contract | Categorical | Customer contract type | Month-to-month, One year, Two year |
| PaperlessBilling | Categorical | Whether customer uses paperless billing | Yes, No |
| PaymentMethod | Categorical | Customer payment method | Electronic check, Mailed check, Bank transfer, Credit card |

## Financial Features
| Column | Type | Description | Range |
|--------|------|-------------|--------|
| MonthlyCharges | Numeric | Monthly service charges (USD) | $18.00 - $118.00 |
| TotalCharges | Numeric | Total charges to date (USD) | $0.00 - $8,500.00 |

## Data Quality Notes
- No missing values by design (synthetic generation ensures completeness)
- Churn rate: ~27% (realistic for telecom industry)
- Tenure distribution: 0-72 months (6 years max)
- All categorical features validated against predefined value sets
- TotalCharges = MonthlyCharges × tenure (mathematically consistent)

## Usage in Pipeline
This dataset is designed for the following analytical phases:
1. **Phase 3**: Data profiling and exploratory statistics
2. **Phase 4**: Data cleaning and quality validation
3. **Phase 5**: Exploratory data analysis and visualization
4. **Phase 6**: Feature engineering and derived metrics
5. **Phase 9**: Predictive modeling (Churn prediction)

## Key Analytical Opportunities
- **Churn drivers**: Identify which services/contracts reduce churn risk
- **Customer segmentation**: Cluster customers by usage patterns and tenure
- **Revenue impact**: Calculate lifetime value and churn revenue loss
- **Retention strategy**: Target at-risk customer segments for intervention
