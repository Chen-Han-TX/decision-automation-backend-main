from typing import Dict, Any, Optional
from app.services.pdf_processing_service import PdfProcessingService
from app.services.excel_processing_service import ExcelProcessingService
from app.services.image_processing_service import ImageProcessingService

class FileFormatHandlerService:
    def __init__(self):
        self.pdf_processor = PdfProcessingService()
        self.excel_processor = ExcelProcessingService()
        self.image_processor = ImageProcessingService()

    async def process_file(self, file_content: bytes, filename: str) -> Dict[str, Any]:
        if filename.endswith('.pdf'):
            return self.pdf_processor.process_pdf_file(file_content)
        elif filename.endswith(('.xls', '.xlsx')):
            return self.excel_processor.process_excel_file(file_content)
        elif filename.endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff')):
            return self.image_processor.process_image_file(file_content)
        else:
            return {"error": "Unsupported file format"}
