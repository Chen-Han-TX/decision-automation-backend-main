from fastapi import APIRouter, Depends, HTTPException
from app.services.risk_engine import RiskEngine
from app.schema.output_schema import RiskScoreRequest, RiskScoreResponse, CashflowMetrics, LiquidityMetrics, FinancialDisciplineMetrics, DebtServicingMetrics, RiskIndicators

router = APIRouter()

@router.post("/risk-score", response_model=RiskScoreResponse)
async def get_risk_score(request: RiskScoreRequest, risk_engine: RiskEngine = Depends()):
    try:
        risk_engine_output = await risk_engine.compute_risk_score(
            cashflow_metrics=request.cashflow_metrics,
            liquidity_metrics=request.liquidity_metrics,
            financial_discipline_metrics=request.financial_discipline_metrics,
            debt_servicing_metrics=request.debt_servicing_metrics,
            risk_indicators=request.risk_indicators
        )
        return RiskScoreResponse(
            document_id="",
            risk_engine_output=risk_engine_output
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

