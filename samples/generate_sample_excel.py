"""
Generate a sample bank-statement-style Excel file for testing document upload.
Run from project root: python samples/generate_sample_excel.py
"""
import pandas as pd
from pathlib import Path

# Columns compatible with backend canonical fields (date, description, debit, credit, balance)
SAMPLE_DATA = [
    {"Date": "2025-10-27", "Description": "Salary deposit", "Credit": 5500.00, "Debit": None, "Balance": 34587.86},
    {"Date": "2025-10-27", "Description": "Amazon purchase", "Credit": None, "Debit": 4685.33, "Balance": 29902.53},
    {"Date": "2025-10-28", "Description": "Starbucks", "Credit": None, "Debit": 45.50, "Balance": 17638.30},
    {"Date": "2025-10-28", "Description": "Netflix subscription", "Credit": None, "Debit": 15.99, "Balance": 17622.31},
    {"Date": "2025-10-29", "Description": "Grocery store", "Credit": None, "Debit": 127.45, "Balance": 22957.87},
    {"Date": "2025-10-30", "Description": "Electric bill", "Credit": None, "Debit": 185.00, "Balance": 22772.87},
]

def main():
    script_dir = Path(__file__).resolve().parent
    out_path = script_dir / "sample_bank_statement.xlsx"
    df = pd.DataFrame(SAMPLE_DATA)
    df.to_excel(out_path, index=False, engine="openpyxl")
    print(f"Created: {out_path}")
    print("Upload this file via the frontend or at http://127.0.0.1:8000/docs (POST /document/upload-file-for-analysis).")

if __name__ == "__main__":
    main()
