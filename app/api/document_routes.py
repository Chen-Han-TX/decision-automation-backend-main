from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from app.services.ingestion_service import IngestionService
from app.core.models import DocumentAnalysisRequest, DocumentInput
from app.schema.output_schema import UnifiedDocumentResponse
from app.services.file_format_handler_service import FileFormatHandlerService
import traceback

router = APIRouter()

@router.post("/analyze-document", response_model=UnifiedDocumentResponse)
async def analyze_document(request: DocumentAnalysisRequest, ingestion_service: IngestionService = Depends()):
    try:
        response = await ingestion_service.process_document(request)
        return response
    except Exception as e:
        traceback.print_exc() # Print traceback for debugging
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/upload-file-for-analysis", response_model=UnifiedDocumentResponse)
async def upload_file_for_analysis(file: UploadFile = File(...), 
                                   ingestion_service: IngestionService = Depends(),
                                   file_format_handler: FileFormatHandlerService = Depends()):
    valid_extensions = ('.pdf', '.xls', '.xlsx', '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff')
    if not file.filename.lower().endswith(valid_extensions):
        raise HTTPException(status_code=400, detail=f"Invalid file type. Supported formats: {', '.join(valid_extensions)}.")

    try:
        file_content = await file.read()
        processed_data = await file_format_handler.process_file(file_content, file.filename)
        
        if "error" in processed_data:
            raise HTTPException(status_code=400, detail=f"File processing error: {processed_data['error']}")

        document_input = DocumentInput(
            document_id=file.filename,
            content=processed_data,
            metadata={'original_filename': file.filename, 'file_type': file.content_type}
        )
        request = DocumentAnalysisRequest(document=document_input)
        response = await ingestion_service.process_document(request)
        return response
    except HTTPException as e:
        raise e
    except Exception as e:
        traceback.print_exc() # Print traceback for debugging
        raise HTTPException(status_code=500, detail=f"Failed to process file for analysis: {e}")

