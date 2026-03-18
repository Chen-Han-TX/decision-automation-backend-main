# Decision Automation Backend

This is the backend service designed to ingest documents (e.g., Excel, PDF, images) and perform automated financial analysis, risk scoring, and decisioning.

## Key Features

* **Document Ingestion:** Handles file upload and raw data parsing (Excel, PDF, Image).
* **Data Standardization:** Maps heterogeneous document headers to a canonical Pydantic schema.
* **Financial Analysis:** Calculates key financial metrics (Cashflow, Liquidity, Debt Servicing).
* **Risk Engine:** Computes a risk score and decision based on calculated metrics and static rules.
* **API Endpoints:** Provides `POST /document/analyze-document` (JSON input) and `POST /document/upload-file-for-analysis` (file upload) for comprehensive analysis.

## Structure Overview

* `app/api/`: FastAPI route definitions.
* `app/services/`: Core business logic (Ingestion, Metrics, Risk, Processing).
* `app/schema/`: Pydantic data models for API contracts and standardized data.
* `app/core/`: Application settings and shared utilities.
* `requirements.txt`: Project dependencies.
* `upload_test.py`: Example script for testing file uploads.