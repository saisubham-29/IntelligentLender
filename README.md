# AI-Powered Credit Decisioning Engine

Automated end-to-end credit appraisal system that generates Comprehensive Credit Appraisal Memos (CAM) using ML-based risk assessment.

## Features

- **Multi-source Data Ingestion**: Connects to Databricks for applicant, financial, and credit history data
- **Web-scale Secondary Research**: Automated research on entities (news, legal, financial, industry)
- **Feature Engineering**: Transforms raw data into ML-ready features
- **ML-based Decisions**: Predicts approval, credit limit, and risk premium
- **Automated CAM Generation**: Synthesizes all findings into comprehensive memo

## Architecture

```
credit_engine/
├── config.py              # Configuration
├── data_ingestion.py      # Databricks data fetching
├── secondary_research.py  # Web research module
├── feature_engineering.py # Feature transformation
├── ml_model.py           # ML decision models
├── cam_generator.py      # CAM document generation
└── engine.py             # Main orchestrator
```

## Installation

```bash
pip install -r requirements.txt
```

## Configuration

Edit `credit_engine/config.py`:

```python
DATABRICKS_CONFIG = {
    "host": "your-databricks-host",
    "token": "your-token",
    "warehouse_id": "your-warehouse-id"
}
```

## Usage

```python
from credit_engine import CreditDecisioningEngine

engine = CreditDecisioningEngine()
result = engine.process_application("APP-12345")

print(result['decision'])  # Decision details
print(result['cam_document'])  # Full CAM
```

## Output

The engine returns:
- **Decision**: APPROVE/REJECT
- **Credit Limit**: Recommended lending amount
- **Risk Premium**: Interest rate adjustment in basis points
- **CAM Document**: Comprehensive appraisal memo with all analysis

## Model Training

Train on historical data:

```python
engine.train_model("SELECT * FROM historical_applications")
```

## Next Steps

1. Configure Databricks connection
2. Integrate news/financial APIs in `secondary_research.py`
3. Train models on historical data
4. Customize feature engineering for your use case
5. Adjust risk thresholds in `config.py`
