from typing import List, Dict, Any, Optional
from app.schema.output_schema import ForecastOutputs
from datetime import date
import pandas as pd

class ForecastService:

    async def get_forecast(self, time_series_data: Dict[date, float]) -> ForecastOutputs:
        if not time_series_data:
            return ForecastOutputs(
                short_term_cashflow_forecast={},
                long_term_revenue_projection={},
                liquidity_stress_test_results={}
            )
            
        dates = sorted(time_series_data.keys())
        values = [time_series_data[d] for d in dates]

        # Helper to convert float to None if it's NaN
        def to_none_if_nan(val: float) -> Optional[float]:
            return val if pd.notna(val) else None

        short_term_forecast = {}
        if len(values) >= 3:
            for i in range(len(values)):
                if i + 1 < len(values):
                    forecast_value = None
                    if i >= 2:
                        # Calculate average, then convert to None if NaN
                        avg = sum(v for v in values[i-2:i+1] if pd.notna(v)) / len([v for v in values[i-2:i+1] if pd.notna(v)]) if len([v for v in values[i-2:i+1] if pd.notna(v)]) > 0 else None
                        forecast_value = to_none_if_nan(avg)
                    else:
                        forecast_value = to_none_if_nan(values[i])
                    short_term_forecast[dates[i+1]] = forecast_value

        long_term_projection_value = to_none_if_nan(values[-1] * 1.05 if values else None)
        if dates and long_term_projection_value is not None:
            long_term_revenue_projection = {dates[-1]: long_term_projection_value}
        else:
            long_term_revenue_projection = {}

        return ForecastOutputs(
            short_term_cashflow_forecast=short_term_forecast,
            long_term_revenue_projection=long_term_revenue_projection,
            liquidity_stress_test_results={"scenario_a": "pass", "scenario_b": "fail"}
        )

