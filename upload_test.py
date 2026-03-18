import httpx
import asyncio

async def upload_excel_file(file_path: str):
    url = "http://127.0.0.1:8000/document/upload-file-for-analysis"
    
    with open(file_path, "rb") as f:
        files = {"file": (file_path, f, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, files=files)
            response.raise_for_status() # Raise an exception for bad status codes
            print(response.json())

if __name__ == "__main__":
    file_to_upload = "test/bank.xlsx"
    asyncio.run(upload_excel_file(file_to_upload))
