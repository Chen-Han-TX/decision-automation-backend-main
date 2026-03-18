# Sample files for testing document upload

Use these files to test the backend document upload (Excel, PDF, or image).

## Excel (bank statement style)

- **sample_bank_statement.xlsx** – Sample transaction data with Date, Description, Credit, Debit, Balance. Use this to test `POST /document/upload-file-for-analysis` in the app or at http://127.0.0.1:8000/docs.

To regenerate the sample Excel file (after installing dependencies):

```bash
cd decision-automation-backend-main
source venv/bin/activate
pip install openpyxl  # if not already installed
python samples/generate_sample_excel.py
```

The file is written to `samples/sample_bank_statement.xlsx`. Upload it via the frontend or Swagger UI.
