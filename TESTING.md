# Testing Guide

## Quick Start (30 seconds)

```bash
# Install dependencies
pip install -r requirements.txt

# Run quick test
python quick_test.py
```

This generates a CAM in `quick_test_output.txt` with mock data.

## Comprehensive Test (2 minutes)

```bash
# Run full test suite
python test_engine.py
```

This tests:
- ✓ Feature engineering
- ✓ ML model training & prediction
- ✓ Secondary research synthesis
- ✓ Primary insights integration
- ✓ Fraud detection (GST-Bank, circular trading, GSTR-2A vs 3B)
- ✓ CAM generation

Output: `test_CAM_output.txt`

## Test Individual Components

### 1. Test Document Parser

```python
from credit_engine.document_parser import DocumentParser

parser = DocumentParser()

# Test with your PDF
annual_report = parser.parse_annual_report('path/to/annual_report.pdf')
print(annual_report)

gst_data = parser.parse_gst_returns('path/to/gstr3b.pdf')
print(gst_data)
```

### 2. Test Fraud Detection

```python
from credit_engine.data_validator import DataValidator
import pandas as pd

validator = DataValidator()

# Test GST-Bank cross-verification
gst_data = {'turnover': 50000000}
bank_df = pd.DataFrame([
    {'type': 'credit', 'amount': 40000000, 'date': '2026-01-15'},
])

result = validator.cross_verify_gst_bank(gst_data, bank_df)
print(f"Variance: {result['variance_pct']:.2f}%")
print(f"Suspicious: {result['is_suspicious']}")
```

### 3. Test Primary Insights

```python
from credit_engine.primary_insights import PrimaryInsights

insights = PrimaryInsights()

# Add site visit
insights.add_site_visit_notes({
    'capacity_utilization_pct': 40,
    'machinery_condition': 'Good',
    'observations': 'Factory at 40% capacity'
})

# Calculate adjustment
score = insights.calculate_qualitative_score()
print(f"Score adjustment: {score['total_adjustment']}")
```

### 4. Test Full Pipeline

```python
from credit_engine import CreditDecisioningEngine

engine = CreditDecisioningEngine()

# Note: Requires Databricks connection configured
result = engine.process_application(
    applicant_id="APP-12345",
    documents={
        'annual_report': 'path/to/report.pdf',
        'gst_returns': 'path/to/gst.pdf',
        'bank_statement': 'path/to/bank.pdf'
    },
    primary_inputs={
        'site_visit': {
            'capacity_utilization_pct': 75,
            'observations': 'Well-maintained facility'
        }
    }
)

print(result['decision'])
print(result['cam_document'])
```

## Test with Sample PDFs

Create sample PDFs in `test_data/` folder:

```
test_data/
├── annual_report.pdf
├── gstr3b.pdf
├── bank_statement.pdf
├── mca_filing.pdf
└── legal_notice.pdf
```

Then run:

```python
from credit_engine.document_parser import DocumentParser

parser = DocumentParser()

# Parse all documents
docs = {
    'annual_report': parser.parse_annual_report('test_data/annual_report.pdf'),
    'gst': parser.parse_gst_returns('test_data/gstr3b.pdf'),
    'bank': parser.parse_bank_statement('test_data/bank_statement.pdf'),
    'mca': parser.parse_mca_filing('test_data/mca_filing.pdf'),
    'legal': parser.parse_legal_notice('test_data/legal_notice.pdf')
}

print(docs)
```

## Expected Output

### Quick Test Output
```
Decision: APPROVE/REJECT
Credit Limit: ₹5,000,000.00
Risk Premium: 650 bps

Full CAM saved to quick_test_output.txt
```

### Comprehensive Test Output
```
================================================================================
TESTING CREDIT DECISIONING ENGINE
================================================================================

1. Feature Engineering...
✓ Generated 12 features

2. ML Model Prediction...
✓ Decision: APPROVE
  Credit Limit: ₹5,234,567.89
  Risk Premium: 650 bps
  Approval Probability: 78.5%

3. Secondary Research...
✓ Research Summary: No significant findings

4. Primary Insights...
✓ Qualitative Adjustment: +10 points
  Insights Recorded: 2

5. CAM Generation...
✓ CAM Generated (5432 characters)
✓ Saved to test_CAM_output.txt

================================================================================
TESTING FRAUD DETECTION
================================================================================

1. GST-Bank Cross-Verification...
✓ GST Turnover: ₹50,000,000
  Bank Credits: ₹40,000,000
  Variance: 20.00%
  Suspicious: True

2. Circular Trading Detection...
✓ Circular Trading Detected: True
  Suspicious Patterns: 2

3. GSTR-2A vs 3B Verification...
✓ ITC 2A: ₹500,000
  ITC 3B: ₹480,000
  Mismatch: 4.00%
  Risk Level: LOW

✓ ALL TESTS COMPLETED SUCCESSFULLY
```

## Troubleshooting

### Issue: ModuleNotFoundError
```bash
pip install -r requirements.txt
```

### Issue: Databricks connection error
For testing without Databricks, use the mock test scripts:
- `quick_test.py` - No Databricks needed
- `test_engine.py` - No Databricks needed

### Issue: PDF parsing fails
Ensure PDFs are readable (not password-protected or corrupted):
```python
import pdfplumber
with pdfplumber.open('test.pdf') as pdf:
    print(pdf.pages[0].extract_text())
```

## Performance Benchmarks

- Document parsing: ~2-5 seconds per PDF
- Feature engineering: <1 second
- ML prediction: <1 second
- CAM generation: <1 second
- **Total pipeline: ~10-20 seconds per application**

## Next Steps

1. ✓ Run `quick_test.py` to verify installation
2. ✓ Run `test_engine.py` for comprehensive testing
3. Configure Databricks in `credit_engine/config.py`
4. Add real PDF documents
5. Integrate news/MCA/e-Courts APIs in `secondary_research.py`
6. Train models on historical data using `engine.train_model()`
