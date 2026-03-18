import re
from typing import Dict, Any, List
from datetime import date
import pandas as pd
from app.schema.bank_statement_schema import BankStatementInput, Transaction
from app.schema.credit_bureau_schema import CreditBureauInput
from app.schema.kyb_kyc_schema import KybKycInput
from app.core.bank_statement_fields import CANONICAL_BANK_STATEMENT_FIELDS
from app.services.header_standardization_service import HeaderStandardizationService

class StandardizationService:
    def __init__(self):
        self.header_standardization_service = HeaderStandardizationService(CANONICAL_BANK_STATEMENT_FIELDS)

    def standardize_bank_statement(self, df: pd.DataFrame) -> BankStatementInput:
        # Ensure we are working on a copy to avoid SettingWithCopyWarning
        df = df.copy()

        # 1. Rename headers to canonical fields, handling potential duplicates
        raw_headers = df.columns.tolist()
        mapped_headers = self.header_standardization_service.map_headers_to_canonical(raw_headers)
        
        new_columns_map = {}
        seen_canonical_names = set()
        for raw_col in raw_headers:
            canonical_name = mapped_headers.get(raw_col)
            if canonical_name and canonical_name not in seen_canonical_names:
                new_columns_map[raw_col] = canonical_name
                seen_canonical_names.add(canonical_name)
            else:
                # If no canonical match or canonical name already seen, keep original name (or drop if it's junk)
                # We will drop non-canonical and non-mapped columns later
                new_columns_map[raw_col] = raw_col
        
        df = df.rename(columns=new_columns_map) # Assign back to df after rename

        # Drop any columns that are not canonical fields for bank statements and are not 'type'
        # After renaming, we can safely filter based on canonical names
        canonical_names = list(CANONICAL_BANK_STATEMENT_FIELDS.keys())
        # Ensure 'type' is included if it exists and is not a canonical field name
        cols_to_keep = [col for col in df.columns if col in canonical_names or col == 'type']
        df = df[cols_to_keep].copy() # Explicitly create a copy after filtering

        # 2. Drop junk rows (rows where all relevant canonical fields are NaN)
        df.dropna(how='all', subset=[col for col in canonical_names if col in df.columns], inplace=True)
        
        if df.empty:
            raise ValueError("No valid transaction data found after standardization.")

        # Ensure all canonical columns exist, fill missing with None or appropriate default
        for field in canonical_names:
            if field not in df.columns:
                df[field] = None

        # Convert text-based canonical fields to string type to prevent Pydantic validation errors
        text_fields = ['description'] # Add other text fields if needed
        for field in text_fields:
            if field in df.columns:
                df[field] = df[field].astype(str).replace('nan', '') # Convert NaNs to empty string

        # 3. Normalize dates and amounts
        # Debug print to check columns before date conversion
        # print(f"DataFrame columns before date conversion: {df.columns.tolist()}") # Keep for debugging if needed

        if 'date' in df.columns and not df['date'].empty:
            # Use .loc for explicit assignment to avoid SettingWithCopyWarning
            df.loc[:, 'date'] = pd.to_datetime(df['date'], errors='coerce').dt.date
        if 'debit' in df.columns and not df['debit'].empty:
            df.loc[:, 'debit'] = pd.to_numeric(df['debit'], errors='coerce')
        if 'credit' in df.columns and not df['credit'].empty:
            df.loc[:, 'credit'] = pd.to_numeric(df['credit'], errors='coerce')
        if 'balance' in df.columns and not df['balance'].empty:
            df.loc[:, 'balance'] = pd.to_numeric(df['balance'], errors='coerce')
        
        # Handle debit/credit to single amount and type
        if 'debit' in df.columns and 'credit' in df.columns:
            df.loc[:, 'amount'] = df['credit'].fillna(0) - df['debit'].fillna(0)
            df.loc[:, 'type'] = df.apply(lambda row: 'credit' if row['credit'] > 0 else ('debit' if row['debit'] > 0 else 'unknown'), axis=1)
        elif 'debit' in df.columns:
            df.loc[:, 'amount'] = -df['debit'].fillna(0)
            df.loc[:, 'type'] = df.apply(lambda row: 'debit' if row['debit'] > 0 else 'unknown', axis=1)
        elif 'credit' in df.columns:
            df.loc[:, 'amount'] = df['credit'].fillna(0)
            df.loc[:, 'type'] = df.apply(lambda row: 'credit' if row['credit'] > 0 else 'unknown', axis=1)
        else:
            df.loc[:, 'amount'] = None
            df.loc[:, 'type'] = 'unknown'

        # Drop original debit/credit columns
        df.drop(columns=['debit', 'credit'], errors='ignore', inplace=True)

        # Filter out rows where 'date' is NaT (Not a Time) after coercion
        df.dropna(subset=['date'], inplace=True)

        # Ensure numerical columns have proper None values instead of NaN before Pydantic conversion
        for col in ['amount', 'balance']:
            if col in df.columns:
                # Explicitly convert to float, then handle NaN to None
                df.loc[:, col] = df[col].apply(lambda x: float(x) if pd.notna(x) else None)

        # 4. Produce a clean schema matching Pydantic BankStatementInput
        transactions: List[Transaction] = []
        for index, row in df.iterrows():
            # Retrieve values, ensuring they are strictly float or None
            amount_val_raw = row.get('amount')
            balance_val_raw = row.get('balance')

            amount_for_transaction = float(amount_val_raw) if pd.notna(amount_val_raw) else None
            balance_for_transaction = float(balance_val_raw) if pd.notna(balance_val_raw) else None

            transactions.append(
                Transaction(
                    date=row['date'],
                    description=str(row.get('description', 'N/A')), # Ensure description is string
                    amount=amount_for_transaction, 
                    type=row.get('type', 'unknown'),
                    balance=balance_for_transaction
                )
            )
        
        # Infer start_date and end_date from transactions
        start_date = min(t.date for t in transactions) if transactions else date.min
        end_date = max(t.date for t in transactions) if transactions else date.max

        return BankStatementInput(
            account_holder_name="Default Account Holder",  # Placeholder
            account_number="XXXX-XXXX-XXXX-1234",  # Placeholder
            bank_name="Generic Bank",  # Placeholder
            start_date=start_date,
            end_date=end_date,
            transactions=transactions,
            currency="USD"  # Placeholder
        )

    @staticmethod
    def standardize_credit_bureau(raw_data: Dict[str, Any]) -> CreditBureauInput:
        return CreditBureauInput(**raw_data)

    @staticmethod
    def standardize_kyb_kyc(raw_data: Dict[str, Any]) -> KybKycInput:
        return KybKycInput(**raw_data)
