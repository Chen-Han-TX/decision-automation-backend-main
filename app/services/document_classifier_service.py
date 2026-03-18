from typing import Dict, Any, List
import pandas as pd
from app.core.bank_statement_fields import CANONICAL_BANK_STATEMENT_FIELDS, CANONICAL_DOCUMENT_TYPES
from app.services.header_standardization_service import HeaderStandardizationService
from rapidfuzz import fuzz

class DocumentClassifierService:
    def __init__(self):
        self.header_standardization_service = HeaderStandardizationService(CANONICAL_BANK_STATEMENT_FIELDS)
        self.document_type_classifier = HeaderStandardizationService(CANONICAL_DOCUMENT_TYPES, threshold=75)

    def classify_document(self, document_content: Dict[str, Any]) -> str:
        # Assuming document_content can contain 'text_content' or 'excel_data'
        # Prioritize structured data if available
        if "excel_data" in document_content and isinstance(document_content["excel_data"], list):
            df = pd.DataFrame(document_content["excel_data"])
            return self._classify_from_dataframe(df)
        elif "text_content" in document_content and isinstance(document_content["text_content"], str):
            return self._classify_from_text(document_content["text_content"])
        # Add other content types as needed (e.g., PDF text, image OCR text)
        return "unknown"

    def _classify_from_dataframe(self, df: pd.DataFrame) -> str:
        """Classify document type based on DataFrame headers and structure."""
        raw_headers = df.columns.tolist()
        matched_canonical_fields = self.header_standardization_service.map_headers_to_canonical(raw_headers)

        # Heuristic 1: Check for a significant number of canonical bank statement fields
        bank_statement_field_count = len([f for f in matched_canonical_fields.values() if f in CANONICAL_BANK_STATEMENT_FIELDS.keys()])
        if bank_statement_field_count >= 3:  # e.g., date, description, amount/debit/credit
            # Further check for row structure indicative of transactions
            if self._has_transactional_structure(df, matched_canonical_fields):
                return "bank_statement"

        # Heuristic 2: Fuzzy match document type keywords in headers or first few rows
        # This part could be expanded to look into cell content as well.
        document_type_scores = {}
        for doc_type, synonyms in CANONICAL_DOCUMENT_TYPES.items():
            highest_score = 0
            for header in raw_headers:
                normalized_header = self.document_type_classifier._normalize_header(header)
                match = self.document_type_classifier.fuzzy_match_header(normalized_header) # Use the document type classifier
                if match == doc_type: # Direct match from a header to a document type synonym
                    highest_score = 100 # Strong match
                    break
            document_type_scores[doc_type] = highest_score
        
        # Determine the best document type based on scores
        if document_type_scores:
            best_doc_type = max(document_type_scores, key=document_type_scores.get)
            if document_type_scores[best_doc_type] >= 75: # A lower threshold for document type keywords
                return best_doc_type

        return "unknown"

    def _classify_from_text(self, text_content: str) -> str:
        """Classify document type based on raw text content."""
        # This can be similar to the old string-based heuristics, but improved with fuzzy matching
        # and potentially more advanced NLP techniques if available.
        normalized_text = self.document_type_classifier._normalize_header(text_content) # Reuse normalization
        
        document_type_scores = {}
        for doc_type, synonyms in CANONICAL_DOCUMENT_TYPES.items():
            best_match_score = 0
            # Check for presence of normalized synonyms in the text
            for syn in synonyms:
                normalized_syn = self.document_type_classifier._normalize_header(syn)
                # Using token_set_ratio for substring matching within the document content
                score = fuzz.token_set_ratio(normalized_syn, normalized_text)
                if score > best_match_score:
                    best_match_score = score
            document_type_scores[doc_type] = best_match_score
        
        if document_type_scores:
            best_doc_type = max(document_type_scores, key=document_type_scores.get)
            if document_type_scores[best_doc_type] >= 75: # Threshold for text content matching
                return best_doc_type

        return "unknown"

    def _has_transactional_structure(self, df: pd.DataFrame, matched_canonical_fields: Dict[str, str]) -> bool:
        """Checks for row structure indicative of bank statement transactions."""
        # Look for a mix of numerical and date-like columns, typical of transactions
        has_date = any(field == 'date' for field in matched_canonical_fields.values())
        has_amount = any(field in ['debit', 'credit'] for field in matched_canonical_fields.values())
        has_balance = any(field == 'balance' for field in matched_canonical_fields.values())
        has_description = any(field == 'description' for field in matched_canonical_fields.values())

        if not (has_date and (has_amount or has_balance) and has_description):
            return False
        
        # Further check: at least a few rows should have valid-looking data in these columns
        # For simplicity, let's just check for non-nulls in assumed key columns
        key_columns = [k for k, v in matched_canonical_fields.items() if v in ['date', 'description', 'debit', 'credit', 'balance']]
        if not key_columns:
            return False
        
        # Check if at least 50% of the rows have non-null values in at least 3 key columns
        valid_rows_count = df[key_columns].notna().sum(axis=1).ge(3).sum()
        return valid_rows_count / len(df) > 0.5 if len(df) > 0 else False
