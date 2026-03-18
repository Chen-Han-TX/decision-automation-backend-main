import yaml
from typing import Dict, Any, List
from app.schema.output_schema import CashflowMetrics, LiquidityMetrics, FinancialDisciplineMetrics, DebtServicingMetrics, RiskIndicators, RiskEngineOutput
from pathlib import Path

class RiskEngine:
    def __init__(self):
        self.rules = self._load_rules()

    def _load_rules(self) -> List[Dict[str, Any]]:
        rules_path = Path(__file__).parent.parent / "rules" / "rules.yaml"
        with open(rules_path, "r") as f:
            config = yaml.safe_load(f)
        return config.get("rules", [])

    async def compute_risk_score(self, 
                                 cashflow_metrics: CashflowMetrics,
                                 liquidity_metrics: LiquidityMetrics,
                                 financial_discipline_metrics: FinancialDisciplineMetrics,
                                 debt_servicing_metrics: DebtServicingMetrics,
                                 risk_indicators: RiskIndicators) -> RiskEngineOutput:
        score = 0
        rationale = []

        # Safely access metrics, defaulting to 0 if None to prevent errors
        net_cashflow = getattr(cashflow_metrics, 'net_cashflow', 0.0) or 0.0
        current_ratio = getattr(liquidity_metrics, 'current_ratio', 0.0) or 0.0
        overdraft_frequency = getattr(financial_discipline_metrics, 'overdraft_frequency', 0) or 0
        dscr = getattr(debt_servicing_metrics, 'dscr', 0.0) or 0.0
        bankruptcy_flags = getattr(risk_indicators, 'bankruptcy_flags', False) or False

        if net_cashflow < 0:
            score += 20
            rationale.append("Negative net cashflow indicates financial distress.")

        if current_ratio < 1.0:
            score += 15
            rationale.append("Current ratio below 1.0 suggests poor short-term liquidity.")

        if overdraft_frequency > 0:
            score += overdraft_frequency * 5
            rationale.append(f"Frequent overdrafts ({overdraft_frequency}) indicate poor financial management.")
        
        # Only apply DSCR rule if dscr is not zero (to avoid penalizing for missing data that defaults to 0)
        if dscr > 0 and dscr < 1.2: 
            score += 25
            rationale.append(f"Debt Service Coverage Ratio ({dscr:.2f}) is below acceptable levels.")

        if bankruptcy_flags:
            score += 50
            rationale.append("Bankruptcy flags detected, indicating severe financial risk.")

        score = max(0, min(100, score))

        if score < 30:
            bin_category = "low"
            decision = "Approved"
        elif 30 <= score < 70:
            bin_category = "medium"
            decision = "Review Required"
        else:
            bin_category = "high"
            decision = "Rejected"

        if not rationale:
            rationale.append("No specific rules triggered. Base assessment.")

        return RiskEngineOutput(
            score=float(score),
            bin=bin_category,
            decision=decision,
            rationale=rationale
        )

