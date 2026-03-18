from typing import Dict, Any
from app.core.models import RagOutput

class RagService:

    async def process_document(self, document_content: Dict[str, Any]) -> RagOutput:
        return RagOutput(
            summary="This is a summarized version of the document content.",
            relevant_chunks=["chunk 1: some relevant info", "chunk 2: more info"]
        )

