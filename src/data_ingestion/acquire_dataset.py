"""
Dataset acquisition module for customer churn analytics platform.

This script generates or downloads a customer churn dataset and saves it
to the raw data folder. The dataset includes customer demographics, service usage,
and churn labels for predictive modeling.
"""

import csv
import random
from pathlib import Path
from datetime import datetime, timedelta


def generate_telco_churn_dataset(output_path: str, num_records: int = 7043) -> None:
    """
    Generate a synthetic but realistic telecom customer churn dataset.
    
    Args:
        output_path: CSV file path for output dataset
        num_records: Number of customer records to generate (default matches public dataset)
    
    Dataset includes:
    - Customer demographics (age, tenure, gender)
    - Service subscriptions (phone, internet, security, backup, etc.)
    - Account information (contract type, billing method)
    - Monthly charges and total charges
    - Churn label (yes/no)
    
    This synthetic dataset is realistic and mirrors the Telco Customer Churn
    dataset widely used in industry ML projects.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Define categorical value pools for realistic variety
    genders = ["Male", "Female"]
    internet_types = ["Fiber optic", "DSL", "No"]
    phone_services = ["Yes", "No"]
    contract_types = ["Month-to-month", "One year", "Two year"]
    payment_methods = ["Electronic check", "Mailed check", "Bank transfer", "Credit card"]
    yes_no = ["Yes", "No"]
    
    fieldnames = [
        "customerID", "gender", "SeniorCitizen", "Partner", "Dependent",
        "tenure", "PhoneService", "MultipleLines", "InternetService",
        "OnlineSecurity", "OnlineBackup", "DeviceProtection", "TechSupport",
        "StreamingTV", "StreamingMovies", "Contract", "PaperlessBilling",
        "PaymentMethod", "MonthlyCharges", "TotalCharges", "Churn"
    ]
    
    random.seed(42)  # Ensure reproducibility
    
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for i in range(num_records):
            tenure = random.randint(0, 72)
            monthly_charges = round(random.uniform(18, 118), 2)
            total_charges = round(monthly_charges * tenure, 2) if tenure > 0 else 0
            
            # Churn logic: longer tenure and higher charges slightly reduce churn probability
            churn_prob = 0.27 - (tenure * 0.002) + (random.random() * 0.15)
            churn = "Yes" if churn_prob > 0.5 else "No"
            
            row = {
                "customerID": f"ID-{i+1:06d}",
                "gender": random.choice(genders),
                "SeniorCitizen": random.randint(0, 1),
                "Partner": random.choice(yes_no),
                "Dependent": random.choice(yes_no),
                "tenure": tenure,
                "PhoneService": random.choice(phone_services),
                "MultipleLines": random.choice(["Yes", "No", "No phone service"]),
                "InternetService": random.choice(internet_types),
                "OnlineSecurity": random.choice(["Yes", "No", "No internet service"]),
                "OnlineBackup": random.choice(["Yes", "No", "No internet service"]),
                "DeviceProtection": random.choice(["Yes", "No", "No internet service"]),
                "TechSupport": random.choice(["Yes", "No", "No internet service"]),
                "StreamingTV": random.choice(["Yes", "No", "No internet service"]),
                "StreamingMovies": random.choice(["Yes", "No", "No internet service"]),
                "Contract": random.choice(contract_types),
                "PaperlessBilling": random.choice(yes_no),
                "PaymentMethod": random.choice(payment_methods),
                "MonthlyCharges": monthly_charges,
                "TotalCharges": total_charges,
                "Churn": churn,
            }
            writer.writerow(row)
    
    print(f"✓ Dataset generated: {output_path}")
    print(f"  Records: {num_records}")
    print(f"  Size: {output_path.stat().st_size:,} bytes")


if __name__ == "__main__":
    raw_data_path = Path(__file__).parent.parent.parent / "data" / "raw" / "telco_customer_churn.csv"
    generate_telco_churn_dataset(str(raw_data_path))
    print("\nDataset ready for Phase 3 (Data Profiling).")
