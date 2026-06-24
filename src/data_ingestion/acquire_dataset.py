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

            # Generate key service/account attributes before churn scoring.
            contract = random.choice(contract_types)
            payment_method = random.choice(payment_methods)
            internet_service = random.choice(internet_types)
            online_security = random.choice(["Yes", "No", "No internet service"])
            tech_support = random.choice(["Yes", "No", "No internet service"])
            paperless_billing = random.choice(yes_no)
            senior_citizen = random.randint(0, 1)

            # Churn logic: business-driven risk score with bounded probability.
            churn_prob = 0.20

            if contract == "Month-to-month":
                churn_prob += 0.20
            elif contract == "One year":
                churn_prob -= 0.05
            else:  # Two year
                churn_prob -= 0.15

            if tenure <= 6:
                churn_prob += 0.18
            elif tenure <= 12:
                churn_prob += 0.08
            elif tenure >= 48:
                churn_prob -= 0.10

            if internet_service == "Fiber optic":
                churn_prob += 0.06
            elif internet_service == "No":
                churn_prob -= 0.04

            if payment_method == "Electronic check":
                churn_prob += 0.08
            elif payment_method in ("Bank transfer", "Credit card"):
                churn_prob -= 0.04

            if online_security == "Yes":
                churn_prob -= 0.06
            if tech_support == "Yes":
                churn_prob -= 0.08
            if paperless_billing == "Yes":
                churn_prob += 0.02
            if senior_citizen == 1:
                churn_prob += 0.03

            churn_prob += random.uniform(-0.04, 0.04)
            churn_prob = max(0.03, min(0.80, churn_prob))
            churn = "Yes" if random.random() < churn_prob else "No"
            
            row = {
                "customerID": f"ID-{i+1:06d}",
                "gender": random.choice(genders),
                "SeniorCitizen": senior_citizen,
                "Partner": random.choice(yes_no),
                "Dependent": random.choice(yes_no),
                "tenure": tenure,
                "PhoneService": random.choice(phone_services),
                "MultipleLines": random.choice(["Yes", "No", "No phone service"]),
                "InternetService": internet_service,
                "OnlineSecurity": online_security,
                "OnlineBackup": random.choice(["Yes", "No", "No internet service"]),
                "DeviceProtection": random.choice(["Yes", "No", "No internet service"]),
                "TechSupport": tech_support,
                "StreamingTV": random.choice(["Yes", "No", "No internet service"]),
                "StreamingMovies": random.choice(["Yes", "No", "No internet service"]),
                "Contract": contract,
                "PaperlessBilling": paperless_billing,
                "PaymentMethod": payment_method,
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
