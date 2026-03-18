from typing import Dict, Any
from io import BytesIO
import pypdf

class PdfProcessingService:
    @staticmethod
    def process_pdf_file(file_content: bytes) -> Dict[str, Any]:
        text_content = ""
        try:
            pdf_file = BytesIO(file_content)
            reader = pypdf.PdfReader(pdf_file)
            for page_num in range(len(reader.pages)):
                text_content += reader.pages[page_num].extract_text() + "\n"
        except Exception as e:
            print(f"Error processing PDF: {e}")
            # Return empty content or raise a specific error
            return {"text_content": "", "error": str(e)}

        # In a real application, you would do more sophisticated parsing here
        # For now, we return a dictionary with the extracted text content
        return {"text_content": text_content}
