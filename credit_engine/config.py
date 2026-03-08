"""Configuration for Credit Decisioning Engine"""
import os
from dotenv import load_dotenv

load_dotenv()

DATABRICKS_CONFIG = {
    "host": "your-databricks-host",
    "token": "your-token",
    "warehouse_id": "your-warehouse-id"
}

OPENAI_CONFIG = {
    "api_key": "OPENAI_API_KEY",  # Set via environment variable OPENAI_API_KEY
    "model": "gpt-4o-mini",  # Cost-effective vision model
    "max_tokens": 2000
}

GROQ_CONFIG = {
    "api_key": "GROQ_API_KEY",  # Set via environment variable GROQ_API_KEY
    "model": "llama-3.3-70b-versatile",  # Fast and accurate for RAG
    "max_tokens": 4000
}

ML_MODEL_CONFIG = {
    "risk_threshold": 0.65,
    "min_credit_score": 600,
    "max_dti_ratio": 0.43
}

RESEARCH_CONFIG = {
    "max_sources": 10,
    "search_depth": 3
}
