from app.schema.bank_statement_schema import BankStatementInput
from app.schema.credit_bureau_schema import CreditBureauInput
from app.schema.kyb_kyc_schema import KybKycInput
from app.schema.output_schema import UnifiedDocumentResponse, CashflowMetrics, LiquidityMetrics, FinancialDisciplineMetrics, DebtServicingMetrics, RiskIndicators, LlmSummaryOutput, ForecastOutputs, RiskEngineOutput
from app.core.models import DocumentAnalysisRequest, CvOutput, RagOutput, AnomalyOutput

import pandas as pd

from app.services.cv_service import CvService
from app.services.rag_service import RagService
from app.services.anomaly_service import AnomalyService
from app.services.forecast_service import ForecastService
from app.services.risk_engine import RiskEngine
from app.services.document_classifier_service import DocumentClassifierService
from app.services.standardization_service import StandardizationService
from app.services.metrics_service import MetricsService


class IngestionService:
    def __init__(self):
        self.cv_service = CvService()
        self.rag_service = RagService()
        self.anomaly_service = AnomalyService()
        self.forecast_service = ForecastService()
        self.risk_engine = RiskEngine()
        self.document_classifier = DocumentClassifierService()
        self.standardization_service = StandardizationService()
        self.metrics_service = MetricsService()

    async def process_document(self, request: DocumentAnalysisRequest) -> UnifiedDocumentResponse:
        document_id = request.document.document_id
        raw_content = request.document.content

        # Prepare content for classification and standardization
        # Assuming raw_content can be a dict with 'excel_data' (list of dicts) or 'text_content' (str)
        document_type = self.document_classifier.classify_document(raw_content)

        if document_type == "bank_statement":
            return await self._process_bank_statement(document_id, raw_content)
        elif document_type == "credit_bureau":
            return await self._process_credit_bureau(document_id, raw_content)
        elif document_type == "kyb_kyc":
            return await self._process_kyb_kyc(document_id, raw_content)
        else:
            return UnifiedDocumentResponse(
                document_type="unknown",
                extracted_data=raw_content,
                llm_summary=LlmSummaryOutput(summary_text="Could not classify document type.", key_insights=[], red_flags_identified=[])
            )

    async def _process_bank_statement(self, document_id: str, raw_content: dict) -> UnifiedDocumentResponse:
        df = pd.DataFrame(raw_content["excel_data"]) if "excel_data" in raw_content else pd.DataFrame()
        bank_statement_input = self.standardization_service.standardize_bank_statement(df)

        cashflow_metrics = self.metrics_service.calculate_cashflow_metrics(bank_statement_input)
        liquidity_metrics = self.metrics_service.calculate_liquidity_metrics(bank_statement_input)
        financial_discipline_metrics = self.metrics_service.calculate_financial_discipline_metrics(bank_statement_input)
        debt_servicing_metrics = self.metrics_service.calculate_debt_servicing_metrics(bank_statement_input)
        risk_indicators = self.metrics_service.identify_risk_indicators(bank_statement_input)

        # cv_output = await self.cv_service.analyze_document(raw_content)
        # rag_output = await self.rag_service.process_document(raw_content)
        # anomaly_output = await self.anomaly_service.detect_anomaly(raw_content)
        
        # Ensure time_series_data values are float or None
        time_series_data = {
            t.date: (float(t.amount) if pd.notna(t.amount) else None) if t.type == 'credit'
                      else (float(-t.amount) if pd.notna(t.amount) else None)
            for t in bank_statement_input.transactions
        }
        forecast_outputs = await self.forecast_service.get_forecast(time_series_data)

        risk_engine_output = await self.risk_engine.compute_risk_score(
            cashflow_metrics, liquidity_metrics, financial_discipline_metrics, debt_servicing_metrics, risk_indicators
        )

        # Explicitly ensure risk_score is float or None before passing to UnifiedDocumentResponse
        final_risk_score = float(risk_engine_output.score) if pd.notna(risk_engine_output.score) else None

        llm_summary = LlmSummaryOutput(
            summary_text="Bank statement analysis complete.",
            key_insights=["Positive cashflow", "Good liquidity"],
            red_flags_identified=[]
        )

        return UnifiedDocumentResponse(
            document_type="bank_statement",
            extracted_data=raw_content,
            cashflow_metrics=cashflow_metrics,
            liquidity_metrics=liquidity_metrics,
            financial_discipline_metrics=financial_discipline_metrics,
            debt_servicing_metrics=debt_servicing_metrics,
            risk_indicators=risk_indicators,
            llm_summary=llm_summary,
            forecasts=forecast_outputs,
            risk_score=final_risk_score, # Use the strictly converted value
            risk_factors=risk_engine_output.rationale
        )

    async def _process_credit_bureau(self, document_id: str, raw_content: dict) -> UnifiedDocumentResponse:
        credit_bureau_input = self.standardization_service.standardize_credit_bureau(raw_content)

        risk_indicators = RiskIndicators(
            high_risk_transactions=[],
            credit_score_change=0.0,
            negative_news_mentions=0,
            bankruptcy_flags=False
        )
        llm_summary = LlmSummaryOutput(
            summary_text="Credit bureau analysis complete.",
            key_insights=[],
            red_flags_identified=[]
        )
        risk_engine_output = RiskEngineOutput(score=50.0, bin="medium", decision="Review Required", rationale=["Default credit bureau analysis."])

        return UnifiedDocumentResponse(
            document_type="credit_bureau",
            extracted_data=raw_content,
            risk_indicators=risk_indicators,
            llm_summary=llm_summary,
            risk_score=risk_engine_output.score,
            risk_factors=risk_engine_output.rationale
        )

    async def _process_kyb_kyc(self, document_id: str, raw_content: dict) -> UnifiedDocumentResponse:
        kyb_kyc_input = self.standardization_service.standardize_kyb_kyc(raw_content)

        risk_indicators = RiskIndicators(
            high_risk_transactions=[],
            credit_score_change=0.0,
            negative_news_mentions=0,
            bankruptcy_flags=False
        )
        llm_summary = LlmSummaryOutput(
            summary_text="KYB/KYC analysis complete.",
            key_insights=[],
            red_flags_identified=[]
        )
        risk_engine_output = RiskEngineOutput(score=20.0, bin="low", decision="Approved", rationale=["Default KYB/KYC analysis."])

        return UnifiedDocumentResponse(
            document_type="kyb_kyc",
            extracted_data=raw_content,
            risk_indicators=risk_indicators,
            llm_summary=llm_summary,
            risk_score=risk_engine_output.score,
            risk_factors=risk_engine_output.rationale
        )

