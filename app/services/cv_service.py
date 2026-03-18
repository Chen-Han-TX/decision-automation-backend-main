from typing import Dict, Any
from app.core.models import CvOutput

class CvService:

    async def analyze_document(self, document_content: Dict[str, Any]) -> CvOutput:
        return CvOutput(
            text_detections=[
                {"box": [10, 10, 20, 20], "text": "sample text"}
            ],
            object_detections=[
                {"box": [50, 50, 60, 60], "label": "sample_object"}
            ]
        )

