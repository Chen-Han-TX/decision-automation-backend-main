import pytest
import pandas as pd
from io import BytesIO
from unittest.mock import MagicMock

from app.services.excel_processing_service import ExcelProcessingService

def test_process_excel_file_bank_statement_columns(monkeypatch):
    # Mock data to be returned by pd.read_excel
    mock_data = {
        'Date': ['2023-01-01', '2023-01-02'],
        'Description': ['Rent', 'Salary'],
        'Amount': [1000.0, 2000.0],
        'Type': ['debit', 'credit'],
        'Balance': [5000.0, 6000.0]
    }
    mock_df = pd.DataFrame(mock_data)

    # Mock pd.read_excel to return our mock DataFrame
    def mock_read_excel(*args, **kwargs):
        return mock_df

    monkeypatch.setattr(pd, 'read_excel', mock_read_excel)

    # Create a dummy file content (BytesIO is sufficient as it won't be read)
    dummy_file_content = b'dummy excel content'

    # Call the service method
    result = ExcelProcessingService.process_excel_file(dummy_file_content)

    # Assert the expected output structure based on the new logic
    # The new logic returns a dict with 'excel_data' containing a list of dicts
    assert 'excel_data' in result
    assert isinstance(result['excel_data'], list)
    assert len(result['excel_data']) == 2
    assert result['excel_data'][0] == {
        'Date': '2023-01-01',
        'Description': 'Rent',
        'Amount': 1000.0,
        'Type': 'debit',
        'Balance': 5000.0
    }
    assert result['excel_data'][1] == {
        'Date': '2023-01-02',
        'Description': 'Salary',
        'Amount': 2000.0,
        'Type': 'credit',
        'Balance': 6000.0
    }
