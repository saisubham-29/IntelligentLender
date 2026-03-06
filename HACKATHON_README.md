# Intelli-Credit: AI-Powered Credit Decisioning Engine

**Hackathon Solution for Next-Gen Corporate Credit Appraisal**

## Overview

Intelli-Credit automates the end-to-end credit appraisal process for Indian corporate lending, addressing the "Data Paradox" by intelligently processing structured, unstructured, and external data sources to generate comprehensive Credit Appraisal Memos (CAM) in minutes instead of weeks.

## Key Features

### 1. Multi-Format Data Ingestor
- **PDF Parsing**: Extracts data from scanned Indian documents (Annual Reports, GST Returns, Bank Statements)
- **Structured Data**: Integrates with Databricks for GST filings, ITRs, financial statements
- **Indian Context**: Understands GSTIN, CIN, PAN formats and Indian number systems (lakhs/crores)

### 2. Research Agent (Digital Credit Manager)
- **Secondary Research**: 
  - Crawls Indian business news (Economic Times, Business Standard, Mint)
  - Searches MCA portal for director changes, charges, compliance
  - Queries e-Courts portal for litigation history
  - Monitors RBI/SEBI regulatory actions
  - Tracks sector-specific trends and regulations
- **Primary Insights Portal**:
  - Site visit observations (capacity utilization, machinery condition)
  - Management interview notes with qualitative scoring
  - Customer/supplier reference checks
  - Adjusts risk score based on qualitative inputs

### 3. Fraud Detection & Validation
- **GST-Bank Cross-Verification**: Detects revenue inflation by comparing GST turnover vs bank credits
- **Circular Trading Detection**: Identifies suspicious same-day round-trip transactions
- **GSTR-2A vs 3B Reconciliation**: Flags ITC mismatches indicating non-compliance
- **Promoter Transaction Analysis**: Detects excessive related-party transactions

### 4. ML-Based Recommendation Engine
- **Three-Model Architecture**:
  - Approval classifier (Gradient Boosting)
  - Credit limit regressor (Random Forest)
  - Risk premium calculator
- **Explainable AI**: Feature importance ranking shows why decisions were made
- **Qualitative Adjustment**: Integrates primary insights to adjust ML predictions

### 5. CAM Generator
- **Five Cs Framework**: Character, Capacity, Capital, Collateral, Conditions
- **Indian Context**: Uses ₹ currency, Indian date formats, local terminology
- **Comprehensive Output**: 
  - Executive summary with clear recommendation
  - Detailed financial analysis with Indian ratios
  - Validation results and fraud flags
  - Explainability section with top risk factors
  - Decision rationale with specific reasons for approval/rejection

## Architecture

```
credit_engine/
├── config.py              # Configuration
├── data_ingestion.py      # Databricks integration
├── document_parser.py     # Multi-format PDF parser
├── data_validator.py      # Fraud detection & cross-verification
├── secondary_research.py  # Web research (news, MCA, e-Courts)
├── primary_insights.py    # Qualitative inputs portal
├── feature_engineering.py # ML feature transformation
├── ml_model.py           # Decision models
├── cam_generator.py      # CAM document generation
└── engine.py             # Main orchestrator
```

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

```python
from credit_engine import CreditDecisioningEngine

engine = CreditDecisioningEngine()

# Process application with documents
result = engine.process_application(
    applicant_id="APP-12345",
    documents={
        'annual_report': 'path/to/annual_report.pdf',
        'gst_returns': 'path/to/gstr3b.pdf',
        'bank_statement': 'path/to/bank_statement.pdf',
        'mca_filing': 'path/to/mca_filing.pdf'
    },
    primary_inputs={
        'site_visit': {
            'capacity_utilization_pct': 40,
            'observations': 'Factory at 40% capacity'
        }
    }
)

print(result['decision'])  # APPROVE/REJECT
print(result['cam_document'])  # Full CAM
```

### Adding Primary Insights During Due Diligence

```python
# Credit officer adds site visit notes
engine.add_primary_insight('site_visit', {
    'capacity_utilization_pct': 40,
    'machinery_condition': 'Good',
    'observations': 'Factory operating at 40% capacity'
})

# Add management interview
engine.add_primary_insight('management_interview', {
    'quality_rating': 4,  # 1-5 scale
    'red_flags': [],
    'notes': 'Strong management team'
})
```

## Evaluation Criteria Addressed

### ✓ Extraction Accuracy
- Uses `pdfplumber` and `PyPDF2` for robust PDF parsing
- Regex patterns for Indian identifiers (GSTIN, CIN, PAN)
- Handles scanned documents and Indian number formats

### ✓ Research Depth
- Searches Indian-specific sources (MCA, e-Courts, RBI, SEBI)
- Crawls local business news portals
- Tracks promoter-level investigations
- Monitors sector-specific regulatory changes

### ✓ Explainability
- Feature importance ranking shows top risk factors
- Validation results explain fraud flags
- Decision rationale section explains rejection reasons
- Example: "Rejected due to high litigation risk (₹50L claim) and GST-Bank variance of 25%"

### ✓ Indian Context Sensitivity
- **GSTR-2A vs 3B**: Reconciles ITC claims
- **GST-Bank Cross-verification**: Detects circular trading
- **CIBIL Commercial**: Integrates credit bureau data
- **MCA Compliance**: Tracks director changes, charges
- **e-Courts**: Monitors litigation
- **Indian Formats**: ₹ currency, lakhs/crores, DD-MMM-YYYY dates

## Sample Output

```
RECOMMENDATION: APPROVE
Proposed Credit Limit: ₹5,00,00,000
Risk Premium: 650 bps
Approval Confidence: 78.5%

⚠️ Validation Alerts:
  • GST-Bank Variance: 8.2% (within tolerance)
  • GSTR-2A vs 3B Mismatch: 3.5% (Low Risk)

Primary Insights:
  • Factory operating at 40% capacity
  • Management quality: 4/5

Top Risk Factors:
  • Debt to Income Ratio: 0.342
  • Credit Utilization: 0.287
  • Legal Risk Score: 0.156
```

## Key Differentiators

1. **Indian Context Native**: Built specifically for Indian corporate lending
2. **Fraud Detection**: Automated cross-verification catches revenue inflation
3. **Qualitative Integration**: Adjusts ML predictions based on site visits and interviews
4. **Explainable**: Every decision comes with clear reasoning
5. **End-to-End**: From document upload to CAM generation in one pipeline

## Next Steps

1. Configure Databricks connection in `config.py`
2. Integrate news/MCA/e-Courts APIs in `secondary_research.py`
3. Train models on historical loan data
4. Customize feature engineering for your portfolio
5. Deploy as web application with document upload interface

## Demo

```bash
python example_usage.py
```

This generates a complete CAM with all analysis, validation results, and explainability.

---

**Built for the Intelli-Credit Hackathon Challenge**
