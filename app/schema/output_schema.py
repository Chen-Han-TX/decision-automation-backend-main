from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from datetime import date

class CashflowMetrics(BaseModel):
    total_inflow: Optional[float] = None
    total_outflow: Optional[float] = None
    net_cashflow: Optional[float] = None
    average_monthly_cashflow: Optional[float] = None
    cashflow_volatility: Optional[float] = None

class LiquidityMetrics(BaseModel):
    current_ratio: Optional[float] = None
    quick_ratio: Optional[float] = None
    cash_conversion_cycle: Optional[float] = None
    days_cash_on_hand: Optional[float] = None

class FinancialDisciplineMetrics(BaseModel):
    overdraft_frequency: Optional[int] = None # Assuming this could be None if no data
    late_payment_count: Optional[int] = None # Assuming this could be None if no data
    bounced_cheque_count: Optional[int] = None # Assuming this could be None if no data
    savings_rate: Optional[float] = None

class DebtServicingMetrics(BaseModel):
    dscr: Optional[float] = None
    debt_to_income_ratio: Optional[float] = None
    loan_payment_to_income_ratio: Optional[float] = None

class RiskIndicators(BaseModel):
    high_risk_transactions: List[Dict[str, Any]] = Field(default_factory=list)
    credit_score_change: Optional[float] = None
    negative_news_mentions: Optional[int] = None # Assuming this could be None
    bankruptcy_flags: Optional[bool] = None # Assuming this could be None

class LlmSummaryOutput(BaseModel):
    summary_text: str
    key_insights: List[str]
    red_flags_identified: List[str]

class ForecastOutputs(BaseModel):
    short_term_cashflow_forecast: Dict[date, Optional[float]]
    long_term_revenue_projection: Dict[date, Optional[float]]
    liquidity_stress_test_results: Dict[str, Any]

class UnifiedDocumentResponse(BaseModel):
    document_type: str
    extracted_data: Dict[str, Any]
    cashflow_metrics: Optional[CashflowMetrics] = None
    liquidity_metrics: Optional[LiquidityMetrics] = None
    financial_discipline_metrics: Optional[FinancialDisciplineMetrics] = None
    debt_servicing_metrics: Optional[DebtServicingMetrics] = None
    risk_indicators: Optional[RiskIndicators] = None
    llm_summary: Optional[LlmSummaryOutput] = None
    forecasts: Optional[ForecastOutputs] = None
    risk_score: Optional[float] = None
    risk_factors: Optional[List[str]] = None

class RiskEngineOutput(BaseModel):
    score: float = Field(..., ge=0, le=100)
    bin: str
    decision: str
    rationale: List[str]

class RiskScoreRequest(BaseModel):
    cashflow_metrics: CashflowMetrics
    liquidity_metrics: LiquidityMetrics
    financial_discipline_metrics: FinancialDisciplineMetrics
    debt_servicing_metrics: DebtServicingMetrics
    risk_indicators: RiskIndicators

class RiskScoreResponse(BaseModel):
    document_id: Optional[str] = None
    risk_engine_output: RiskEngineOutput
