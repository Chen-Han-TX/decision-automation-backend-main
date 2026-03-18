import pandas as pd
from typing import Dict, Any, Union
from io import BytesIO

class ExcelProcessingService:
    @staticmethod
    def process_excel_file(file_content: bytes, document_type: str = "auto") -> Dict[str, Any]:
        df = pd.read_excel(BytesIO(file_content))

        if not df.empty:
            return {"excel_data": df.to_dict(orient='records')}
        else:
            return {"excel_data": []}
