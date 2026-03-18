from typing import List, Dict, Any
from datetime import date
from app.schema.output_schema import CashflowMetrics, LiquidityMetrics, FinancialDisciplineMetrics, DebtServicingMetrics, RiskIndicators
from app.schema.bank_statement_schema import BankStatementInput, Transaction

class MetricsService:
    @staticmethod
    def calculate_cashflow_metrics(bank_statement: BankStatementInput) -> CashflowMetrics:
        transactions = bank_statement.transactions
        if not transactions:
            return CashflowMetrics(
                total_inflow=None, total_outflow=None, net_cashflow=None,
                average_monthly_cashflow=None, cashflow_volatility=None
            )

        total_inflow = sum(t.amount for t in transactions if t.type == 'credit' and t.amount is not None)
        total_outflow = sum(t.amount for t in transactions if t.type == 'debit' and t.amount is not None)
        net_cashflow = total_inflow - total_outflow
        
        # For average monthly cashflow and volatility, need to consider periods
        # For simplicity, if no data, default to None
        num_transactions = len(transactions)
        average_monthly_cashflow = net_cashflow / num_transactions if num_transactions > 0 else None

        # Placeholder for actual volatility calculation
        cashflow_volatility = 0.0 # Or None if no meaningful calculation

        return CashflowMetrics(
            total_inflow=total_inflow,
            total_outflow=total_outflow,
            net_cashflow=net_cashflow,
            average_monthly_cashflow=average_monthly_cashflow,
            cashflow_volatility=cashflow_volatility
        )

    @staticmethod
    def calculate_liquidity_metrics(bank_statement: BankStatementInput) -> LiquidityMetrics:
        transactions = bank_statement.transactions
        if not transactions:
            return LiquidityMetrics(
                current_ratio=None, quick_ratio=None, cash_conversion_cycle=None, days_cash_on_hand=None
            )

        # Assuming balance in transactions represents current assets/liabilities
        # This might need more sophisticated logic based on actual balance sheet items
        current_assets_list = [t.balance for t in transactions if t.balance is not None and t.type == 'credit']
        current_liabilities_list = [t.balance for t in transactions if t.balance is not None and t.type == 'debit']

        current_assets = current_assets_list[-1] if current_assets_list else 0.0 # Assuming last credit balance is current asset
        current_liabilities = current_liabilities_list[-1] if current_liabilities_list else 0.0 # Assuming last debit balance is current liability

        current_ratio = current_assets / current_liabilities if current_liabilities > 0 else (0.0 if current_assets == 0 else None)
        quick_ratio = current_assets / current_liabilities if current_liabilities > 0 else (0.0 if current_assets == 0 else None)
            
        days_cash_on_hand = current_assets # Simplified for now

        return LiquidityMetrics(
            current_ratio=current_ratio,
            quick_ratio=quick_ratio,
            cash_conversion_cycle=None, # Placeholder
            days_cash_on_hand=days_cash_on_hand
        )

    @staticmethod
    def calculate_financial_discipline_metrics(bank_statement: BankStatementInput) -> FinancialDisciplineMetrics:
        transactions = bank_statement.transactions
        if not transactions:
            return FinancialDisciplineMetrics(
                overdraft_frequency=None, late_payment_count=None, bounced_cheque_count=None, savings_rate=None
            )

        overdraft_frequency = 0
        late_payment_count = 0
        bounced_cheque_count = 0
        
        total_inflow = sum(t.amount for t in transactions if t.type == 'credit' and t.amount is not None)
        # Placeholder for actual savings calculation
        savings = 0.0
        savings_rate = savings / total_inflow if total_inflow > 0 else (0.0 if savings == 0 else None)

        return FinancialDisciplineMetrics(
            overdraft_frequency=overdraft_frequency,
            late_payment_count=late_payment_count,
            bounced_cheque_count=bounced_cheque_count,
            savings_rate=savings_rate
        )
    
    @staticmethod
    def calculate_debt_servicing_metrics(bank_statement: BankStatementInput, total_debt: float = 0.0) -> DebtServicingMetrics:
        transactions = bank_statement.transactions
        if not transactions:
            return DebtServicingMetrics(
                dscr=None, debt_to_income_ratio=None, loan_payment_to_income_ratio=None
            )

        total_outflow = sum(t.amount for t in transactions if t.type == 'debit' and t.amount is not None)
        total_inflow = sum(t.amount for t in transactions if t.type == 'credit' and t.amount is not None)

        # Annual debt payments (simplified)
        annual_debt_payments = total_outflow * 0.1
        # EBITDA (simplified)
        ebitda = total_inflow * 0.5
        
        dscr = ebitda / annual_debt_payments if annual_debt_payments > 0 else (0.0 if ebitda == 0 else None)
            
        debt_to_income_ratio = total_debt / total_inflow if total_inflow > 0 else (0.0 if total_debt == 0 else None)
        loan_payment_to_income_ratio = annual_debt_payments / total_inflow if total_inflow > 0 else (0.0 if annual_debt_payments == 0 else None)

        return DebtServicingMetrics(
            dscr=dscr,
            debt_to_income_ratio=debt_to_income_ratio,
            loan_payment_to_income_ratio=loan_payment_to_income_ratio
        )

    @staticmethod
    def identify_risk_indicators(bank_statement: BankStatementInput, credit_score_change: float = 0.0, negative_news_mentions: int = 0, bankruptcy_flags: bool = False) -> RiskIndicators:
        transactions = bank_statement.transactions
        if not transactions:
            return RiskIndicators(
                high_risk_transactions=[], credit_score_change=None, negative_news_mentions=None, bankruptcy_flags=None
            )

        high_risk_transactions = []

        debit_transactions = [t.amount for t in transactions if t.type == 'debit' and t.amount is not None]
        if debit_transactions:
            average_debit = sum(debit_transactions) / len(debit_transactions)
            for t in transactions:
                if t.type == 'debit' and t.amount is not None and t.amount > average_debit * 2:
                    high_risk_transactions.append(t.dict())
        
        return RiskIndicators(
            high_risk_transactions=high_risk_transactions,
            credit_score_change=credit_score_change,
            negative_news_mentions=negative_news_mentions,
            bankruptcy_flags=bankruptcy_flags
        )
