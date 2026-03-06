"""Configuration for Credit Decisioning Engine"""

DATABRICKS_CONFIG = {
    "host": "your-databricks-host",
    "token": "your-token",
    "warehouse_id": "your-warehouse-id"
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
