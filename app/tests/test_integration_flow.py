import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from io import BytesIO
import pandas as pd

from app.main import app
from app.schema.output_schema import UnifiedDocumentResponse, CashflowMetrics, RiskEngineOutput, FinancialDisciplineMetrics, DebtServicingMetrics, LiquidityMetrics, RiskIndicators

client = TestClient(app)

def test_full_excel_analysis_flow(monkeypatch):
    # Mock data to be returned by pd.read_excel
    mock_data = {
        'Date': ['2023-01-01', '2023-01-02', '2023-01-03'],
        'Description': ['Rent', 'Salary', 'Groceries'],
        'Amount': [1000.0, 2000.0, 150.0],
        'Type': ['debit', 'credit', 'debit'],
        'Balance': [5000.0, 7000.0, 6850.0]
    }
    mock_df = pd.DataFrame(mock_data)

    # Mock pd.read_excel to return our mock DataFrame
    def mock_read_excel(*args, **kwargs):
        return mock_df

    monkeypatch.setattr(pd, 'read_excel', mock_read_excel)

    # Create a dummy Excel file content as bytes
    dummy_excel_content = b"dummy excel content for testing"

    response = client.post(
        "/document/upload-file-for-analysis",
        files={
            "file": ("bank.xlsx", dummy_excel_content, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        }
    )

    assert response.status_code == 200
    response_data = response.json()

    # Validate against UnifiedDocumentResponse schema
    unified_response = UnifiedDocumentResponse(**response_data)

    assert unified_response.document_type == "bank_statement"
    assert unified_response.cashflow_metrics is not None
    assert isinstance(unified_response.cashflow_metrics, CashflowMetrics)
    assert unified_response.risk_score is not None
    assert isinstance(unified_response.risk_score, float)
    assert unified_response.risk_factors is not None
    assert isinstance(unified_response.risk_factors, list)

    # Further assertions on specific metrics and risk output can be added here
    # For example, check expected values for cashflow_metrics, liquidity_metrics etc.
    assert unified_response.cashflow_metrics.total_inflow == 2000.0
    assert unified_response.cashflow_metrics.total_outflow == 1150.0
    assert unified_response.cashflow_metrics.net_cashflow == 850.0

    # Assuming default risk engine behavior without specific rules for now
    assert unified_response.risk_score >= 0.0
    assert unified_response.risk_score <= 100.0

    # Verify other metrics are present and of correct type
    assert isinstance(unified_response.liquidity_metrics, LiquidityMetrics)
    assert isinstance(unified_response.financial_discipline_metrics, FinancialDisciplineMetrics)
    assert isinstance(unified_response.debt_servicing_metrics, DebtServicingMetrics)
    assert isinstance(unified_response.risk_indicators, RiskIndicators)
