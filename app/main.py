from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.router import api_router
from pydantic import BaseModel
import numpy as np # Import numpy

# Custom JSON serializer for numpy.nan
def convert_nan_to_none(obj):
    if isinstance(obj, float) and np.isnan(obj):
        return None
    raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")

app = FastAPI(
    title="Document Intelligence Backend",
    description="Glue layer for document processing and risk assessment",
    version="0.1.0",
    json_encoders={
        np.float64: convert_nan_to_none, # Handle numpy float NaN
        float: convert_nan_to_none       # Handle standard float NaN
    }
)

# Allow frontend (e.g. localhost:5173) to call this API when testing locally
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", 
                   "https://your-frontend.onrender.com",],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)

