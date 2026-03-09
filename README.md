# AI-Powered Credit Decisioning Engine

Automated end-to-end credit appraisal system that generates Comprehensive Credit Appraisal Memos (CAM) using ML-based risk assessment and **AI-powered document parsing**.

## Features

- **Comprehensive Document Parsing**: AI extracts data from 8 document types
  - Structured: GST filings, ITRs, Bank statements
  - Unstructured: Annual reports, Financial statements, Board minutes, Rating reports, Shareholding patterns
- **External Intelligence**: Real-time data from MCA, e-Courts, sector news
- **Web Scraping + RAG**: Groq-powered analysis with article sources
- **Multi-source Data Ingestion**: Connects to Databricks for historical data
- **Feature Engineering**: Transforms raw data into ML-ready features
- **ML-based Decisions**: Predicts approval, credit limit, and risk premium
- **Automated CAM Generation**: Comprehensive memo with all findings (displayed inline)
- **Fraud Detection**: Cross-verification of GST, ITR, and bank data
- **Primary Insights**: Site visits and management interviews

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

# Install poppler for PDF processing (required for AI parsing)
# macOS:
brew install poppler

# Ubuntu/Debian:
sudo apt-get install poppler-utils
```

## Configuration

### 1. Databricks (Optional)
Edit `credit_engine/config.py`:

```python
DATABRICKS_CONFIG = {
    "host": "your-databricks-host",
    "token": "your-token",
    "warehouse_id": "your-warehouse-id"
}
```

### 2. OpenAI API (Required for AI Document Parsing)
Set environment variable:

```bash
export OPENAI_API_KEY='sk-...'
```

Get your API key from: https://platform.openai.com/api-keys

**Cost**: ~₹0.02 per document with gpt-4o-mini model

### 3. Groq API (Required for Web Research - FREE)
Set environment variable:

```bash
export GROQ_API_KEY='gsk_...'
```

Get your FREE API key from: https://console.groq.com

**Cost**: FREE (14,400 requests/day)

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

```bash
# Create sample CSV with correct format
python train_model.py --sample

# Train model from your CSV data
python train_model.py path/to/historical_decisions.csv
```

CSV format includes 29 columns covering all aspects:
- Company identifiers (CIN, LLPIN, PAN, GSTIN)
- Financial metrics (Revenue, EBITDA, Debt, etc.)
- Tax compliance (GSTR Variance, ITC)
- Banking behavior (Cheque bounces, NACH returns)
- Operational data (Capacity utilization, Machinery status)
- Governance (Auditor qualifications, Shareholding pledge)
- Target decision (APPROVE/REJECT)

See `CSV_TRAINING_GUIDE.md` for complete format specification.

## Next Steps

1. **Set up AI parsing**: `export OPENAI_API_KEY='sk-...'` and test with `python test_ai_parsing.py`
2. **Set up web research**: `export GROQ_API_KEY='gsk_...'` (FREE from https://console.groq.com)
3. Configure Databricks connection (optional)
4. Train models on historical data
5. Customize feature engineering for your use case
6. Adjust risk thresholds in `config.py`

## Documentation

- **[CSV Training Guide](CSV_TRAINING_GUIDE.md)** - Model training with historical data
- **[Comprehensive Data Sources](COMPREHENSIVE_DATA_SOURCES.md)** - All 8 document types + external intelligence
- **[Web Scraping + RAG Guide](WEB_SCRAPING_RAG_GUIDE.md)** - Web research with Groq
- **[AI Parsing Setup Guide](AI_PARSING_SETUP.md)** - Complete guide for AI document parsing
- **[AI Implementation Summary](AI_IMPLEMENTATION_SUMMARY.md)** - Technical details and benefits
- **[Improvements Summary](IMPROVEMENTS_SUMMARY.md)** - Latest improvements
- **[Validation Fixes](VALIDATION_FIXES.md)** - Form validation and UX improvements
