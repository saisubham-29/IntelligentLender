# 🚀 Quick Start Guide

## Installation (1 minute)

```bash
# Install dependencies
pip install -r requirements.txt
```

## Run Demo (30 seconds)

```bash
# Quick test with mock data
python quick_test.py
```

**Output**: Decision + CAM saved to `quick_test_output.txt`

## Run Full Test (2 minutes)

```bash
# Comprehensive test with fraud detection
python test_engine.py
```

**Output**: Complete CAM with validation results in `test_CAM_output.txt`

---

## Production Usage

### Option 1: Python Script

```python
from credit_engine import CreditDecisioningEngine

engine = CreditDecisioningEngine()

# Process application
result = engine.process_application(
    applicant_id="APP-12345",
    documents={
        'annual_report': 'path/to/annual_report.pdf',
        'gst_returns': 'path/to/gstr3b.pdf',
        'bank_statement': 'path/to/bank_statement.pdf'
    },
    primary_inputs={
        'site_visit': {
            'capacity_utilization_pct': 75,
            'observations': 'Well-maintained facility'
        }
    }
)

print(f"Decision: {result['decision']['decision']}")
print(f"Credit Limit: ₹{result['decision']['credit_limit']:,.2f}")
print(result['cam_document'])
```

### Option 2: Web Portal (Coming Soon)

```bash
# Start Flask server
python web_portal.py

# Open browser: http://localhost:5000
```

---

## Configuration

### 1. Configure Databricks (Required for production)

Edit `credit_engine/config.py`:

```python
DATABRICKS_CONFIG = {
    "host": "your-databricks-workspace.cloud.databricks.com",
    "token": "your-access-token",
    "warehouse_id": "your-warehouse-id"
}
```

### 2. Add API Keys (Optional - for secondary research)

In `credit_engine/secondary_research.py`, add:
- News API key
- MCA portal credentials
- Other data provider APIs

---

## Project Structure

```
PythonProject/
├── credit_engine/           # Main package
│   ├── config.py           # Configuration
│   ├── engine.py           # Main orchestrator
│   ├── data_ingestion.py   # Databricks integration
│   ├── document_parser.py  # PDF parsing
│   ├── data_validator.py   # Fraud detection
│   ├── secondary_research.py # Web research
│   ├── primary_insights.py # Qualitative inputs
│   ├── feature_engineering.py # ML features
│   ├── ml_model.py         # Decision models
│   └── cam_generator.py    # CAM generation
├── quick_test.py           # Quick demo
├── test_engine.py          # Full test suite
├── example_usage.py        # Usage examples
├── web_portal.py           # Flask API
└── requirements.txt        # Dependencies
```

---

## Workflow

1. **Install**: `pip install -r requirements.txt`
2. **Test**: `python quick_test.py`
3. **Configure**: Update `config.py` with Databricks credentials
4. **Run**: Use `CreditDecisioningEngine` in your code
5. **Output**: Get decision + CAM document

---

## What You Get

- ✅ Decision: APPROVE/REJECT
- ✅ Credit Limit: Recommended amount in ₹
- ✅ Risk Premium: Interest rate adjustment in bps
- ✅ CAM Document: Professional memo with Five Cs analysis
- ✅ Explainability: Top risk factors with importance scores
- ✅ Fraud Flags: GST-Bank variance, circular trading alerts
- ✅ Validation: GSTR-2A vs 3B reconciliation

---

## Troubleshooting

**Issue**: Module not found
```bash
pip install -r requirements.txt
```

**Issue**: No Databricks access
- Use `quick_test.py` or `test_engine.py` (work with mock data)

**Issue**: PDF parsing fails
- Ensure PDFs are not password-protected
- Check file paths are correct

---

## Next Steps

1. ✅ Run `quick_test.py` to verify setup
2. ✅ Check `quick_test_output.txt` for CAM
3. Configure Databricks for production
4. Add real PDF documents
5. Integrate external APIs (news, MCA, e-Courts)
6. Train ML models on historical data

---

**Need help?** Check `TESTING.md` for detailed testing guide.
