from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class HealthCheckResponse(BaseModel):
    status: str
    message: str

class DocumentInput(BaseModel):
    document_id: str
    content: Dict[str, Any]
    metadata: Dict[str, Any] = {}

class DocumentAnalysisRequest(BaseModel):
    document: DocumentInput

class CvOutput(BaseModel):
    text_detections: List[Dict[str, Any]] = []
    object_detections: List[Dict[str, Any]] = []

class RagOutput(BaseModel):
    summary: str
    relevant_chunks: List[str]

class AnomalyOutput(BaseModel):
    is_anomaly: bool
    anomaly_score: Optional[float] = None
    reason: Optional[str] = None

