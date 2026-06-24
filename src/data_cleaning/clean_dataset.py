"""
Data cleaning module for customer churn analytics platform.

This module handles:
1. Feature encoding (categorical → numeric)
2. Feature scaling (normalization)
3. Data validation and consistency checks
4. Processed dataset generation
"""

import csv
from pathlib import Path
from collections import OrderedDict


def load_raw_data(csv_path: str) -> tuple:
    """Load raw dataset and return headers and rows."""
    path = Path(csv_path)
    rows = []
    headers = None
    
    with open(path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames
        for row in reader:
            rows.append(row)
    
    return headers, rows


def encode_binary_feature(value: str) -> int:
    """Encode binary Yes/No features to 0/1."""
    if value in ('Yes', '1'):
        return 1
    elif value in ('No', '0'):
        return 0
    else:
        return int(value) if value.isdigit() else 0


def encode_contract_type(contract: str) -> int:
    """Encode contract type: Month-to-month=0, One year=1, Two year=2."""
    mapping = {
        'Month-to-month': 0,
        'One year': 1,
        'Two year': 2
    }
    return mapping.get(contract, 0)


def encode_internet_service(service: str) -> int:
    """Encode internet service: No=0, DSL=1, Fiber optic=2."""
    mapping = {
        'No': 0,
        'DSL': 1,
        'Fiber optic': 2
    }
    return mapping.get(service, 0)


def encode_payment_method(method: str) -> int:
    """Encode payment method: 0-3."""
    mapping = {
        'Electronic check': 0,
        'Mailed check': 1,
        'Bank transfer': 2,
        'Credit card': 3
    }
    return mapping.get(method, 0)


def encode_gender(gender: str) -> int:
    """Encode gender: Female=0, Male=1."""
    return 1 if gender == 'Male' else 0


def normalize_numeric(value: str, min_val: float, max_val: float) -> float:
    """Min-max normalize numeric value."""
    try:
        num = float(value)
        if max_val == min_val:
            return 0.5
        normalized = (num - min_val) / (max_val - min_val)
        return round(normalized, 4)
    except (ValueError, TypeError):
        return 0.0


def create_one_hot_features(value: str, feature_name: str) -> dict:
    """Create one-hot encoded features for multi-class categorical."""
    features = {}
    
    if feature_name == 'MultipleLines':
        options = ['MultipleLines_No', 'MultipleLines_Yes', 'MultipleLines_NoPhoneService']
        mapping = {'No': 0, 'Yes': 1, 'No phone service': 2}
    elif feature_name == 'OnlineSecurity':
        options = ['OnlineSecurity_No', 'OnlineSecurity_Yes', 'OnlineSecurity_NoInternet']
        mapping = {'No': 0, 'Yes': 1, 'No internet service': 2}
    elif feature_name == 'OnlineBackup':
        options = ['OnlineBackup_No', 'OnlineBackup_Yes', 'OnlineBackup_NoInternet']
        mapping = {'No': 0, 'Yes': 1, 'No internet service': 2}
    elif feature_name == 'DeviceProtection':
        options = ['DeviceProtection_No', 'DeviceProtection_Yes', 'DeviceProtection_NoInternet']
        mapping = {'No': 0, 'Yes': 1, 'No internet service': 2}
    elif feature_name == 'TechSupport':
        options = ['TechSupport_No', 'TechSupport_Yes', 'TechSupport_NoInternet']
        mapping = {'No': 0, 'Yes': 1, 'No internet service': 2}
    elif feature_name == 'StreamingTV':
        options = ['StreamingTV_No', 'StreamingTV_Yes', 'StreamingTV_NoInternet']
        mapping = {'No': 0, 'Yes': 1, 'No internet service': 2}
    elif feature_name == 'StreamingMovies':
        options = ['StreamingMovies_No', 'StreamingMovies_Yes', 'StreamingMovies_NoInternet']
        mapping = {'No': 0, 'Yes': 1, 'No internet service': 2}
    else:
        return features
    
    idx = mapping.get(value, 0)
    for i, opt in enumerate(options):
        features[opt] = 1 if i == idx else 0
    
    return features


def clean_and_encode_dataset(raw_csv: str, output_csv: str) -> None:
    """
    Load raw data, apply encoding and scaling, save processed dataset.
    
    Transformations:
    1. Binary features (Yes/No) → 0/1
    2. Categorical features → label encoded or one-hot encoded
    3. Numeric features → min-max normalized to [0, 1]
    4. Target variable (Churn) → 0/1
    """
    print('Loading raw dataset...')
    headers, rows = load_raw_data(raw_csv)
    
    if not rows:
        raise ValueError('No data rows found in raw dataset')
    
    # Calculate normalization bounds from numeric columns
    tenure_vals = [float(row['tenure']) for row in rows]
    monthly_vals = [float(row['MonthlyCharges']) for row in rows]
    total_vals = [float(row['TotalCharges']) for row in rows if row['TotalCharges']]
    
    tenure_min, tenure_max = min(tenure_vals), max(tenure_vals)
    monthly_min, monthly_max = min(monthly_vals), max(monthly_vals)
    total_min, total_max = min(total_vals) if total_vals else 0, max(total_vals) if total_vals else 1
    
    print(f'  Raw records: {len(rows)}')
    print(f'  Normalizing tenure [{tenure_min}, {tenure_max}]')
    print(f'  Normalizing MonthlyCharges [${monthly_min:.2f}, ${monthly_max:.2f}]')
    print(f'  Normalizing TotalCharges [${total_min:.2f}, ${total_max:.2f}]')
    
    # Define encoded columns
    encoded_headers = [
        'customerID',
        'gender',
        'SeniorCitizen',
        'Partner',
        'Dependent',
        'tenure_normalized',
        'PhoneService',
        'MultipleLines_No',
        'MultipleLines_Yes',
        'MultipleLines_NoPhoneService',
        'InternetService_encoded',
        'OnlineSecurity_No',
        'OnlineSecurity_Yes',
        'OnlineSecurity_NoInternet',
        'OnlineBackup_No',
        'OnlineBackup_Yes',
        'OnlineBackup_NoInternet',
        'DeviceProtection_No',
        'DeviceProtection_Yes',
        'DeviceProtection_NoInternet',
        'TechSupport_No',
        'TechSupport_Yes',
        'TechSupport_NoInternet',
        'StreamingTV_No',
        'StreamingTV_Yes',
        'StreamingTV_NoInternet',
        'StreamingMovies_No',
        'StreamingMovies_Yes',
        'StreamingMovies_NoInternet',
        'Contract_encoded',
        'PaperlessBilling',
        'PaymentMethod_encoded',
        'MonthlyCharges_normalized',
        'TotalCharges_normalized',
        'Churn_encoded'
    ]
    
    print(f'\nEncoding {len(rows)} records...')
    encoded_rows = []
    
    for idx, row in enumerate(rows):
        encoded_row = OrderedDict()
        
        # Keep customerID as-is
        encoded_row['customerID'] = row['customerID']
        
        # Binary/ordinal encoding
        encoded_row['gender'] = encode_gender(row['gender'])
        encoded_row['SeniorCitizen'] = int(row['SeniorCitizen'])
        encoded_row['Partner'] = encode_binary_feature(row['Partner'])
        encoded_row['Dependent'] = encode_binary_feature(row['Dependent'])
        encoded_row['PhoneService'] = encode_binary_feature(row['PhoneService'])
        
        # Normalized numeric
        encoded_row['tenure_normalized'] = normalize_numeric(row['tenure'], tenure_min, tenure_max)
        
        # One-hot encoded multi-class
        ml_features = create_one_hot_features(row['MultipleLines'], 'MultipleLines')
        encoded_row.update(ml_features)
        
        # Internet service encoding
        encoded_row['InternetService_encoded'] = encode_internet_service(row['InternetService'])
        
        # Add-on services (one-hot)
        for service in ['OnlineSecurity', 'OnlineBackup', 'DeviceProtection', 'TechSupport', 'StreamingTV', 'StreamingMovies']:
            features = create_one_hot_features(row[service], service)
            encoded_row.update(features)
        
        # Contract and payment
        encoded_row['Contract_encoded'] = encode_contract_type(row['Contract'])
        encoded_row['PaperlessBilling'] = encode_binary_feature(row['PaperlessBilling'])
        encoded_row['PaymentMethod_encoded'] = encode_payment_method(row['PaymentMethod'])
        
        # Normalized financials
        encoded_row['MonthlyCharges_normalized'] = normalize_numeric(row['MonthlyCharges'], monthly_min, monthly_max)
        encoded_row['TotalCharges_normalized'] = normalize_numeric(row['TotalCharges'], total_min, total_max)
        
        # Target variable
        encoded_row['Churn_encoded'] = 1 if row['Churn'] == 'Yes' else 0
        
        encoded_rows.append(encoded_row)
    
    # Save processed dataset
    output_path = Path(output_csv)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    print(f'\nSaving processed dataset to {output_csv}...')
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=encoded_headers)
        writer.writeheader()
        writer.writerows(encoded_rows)
    
    print(f'✓ Processed dataset saved')
    print(f'  Records: {len(encoded_rows)}')
    print(f'  Features: {len(encoded_headers)}')
    print(f'  File size: {output_path.stat().st_size:,} bytes')


if __name__ == '__main__':
    raw_path = 'data/raw/telco_customer_churn.csv'
    processed_path = 'data/processed/telco_customer_churn_processed.csv'
    
    print('='*80)
    print('PHASE 4: DATA CLEANING')
    print('='*80)
    print()
    
    clean_and_encode_dataset(raw_path, processed_path)
    
    print(f'\n✓ Phase 4 Complete: Data cleaning and encoding finished')
    print(f'\nNext: Phase 5 - Exploratory Data Analysis')
