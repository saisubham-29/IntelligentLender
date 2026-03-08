# CSV Training Data Guide

## Overview

The system now supports **CSV-based model training** for better accuracy and optimization using historical credit decisions.

## CSV Format

### Required Columns

```csv
CIN,LLPIN,Entity Status,Date of Incorporation,Paid-up Capital,PAN,GSTIN,GSTR Variance %,ITC Availed,Audited Net Income,Inventory,Accounts Receivable,EBITDA,Long-Term Debt,Cheque Bounces,NACH Returns,OD Utilization,NACH Obligation %,CMR Rank,Asset Classification,Wilful Defaulter,Capacity Utilization,Machinery Status,Promoter Experience,Contingent Liabilities,Auditor Qualifications,Shareholding Pledge,Risk Premium,Target_Decision
```

### Column Descriptions

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| **CIN** | String | Corporate Identification Number | U12345MH2020PTC123456 |
| **LLPIN** | String | Limited Liability Partnership ID | AAA-1234 |
| **Entity Status** | Categorical | Active/Inactive/Dissolved | Active |
| **Date of Incorporation** | Date | Company incorporation date | 2020-01-15 |
| **Paid-up Capital** | Numeric | Paid-up capital in INR | 10000000 |
| **PAN** | String | Permanent Account Number | AABCU1234C |
| **GSTIN** | String | GST Identification Number | 27AABCU1234C1Z5 |
| **GSTR Variance %** | Numeric | GST return variance percentage | 5.2 |
| **ITC Availed** | Numeric | Input Tax Credit availed (INR) | 500000 |
| **Audited Net Income** | Numeric | Net income from audit (INR) | 8000000 |
| **Inventory** | Numeric | Inventory value (INR) | 2000000 |
| **Accounts Receivable** | Numeric | Receivables (INR) | 3000000 |
| **EBITDA** | Numeric | Earnings before interest, tax, depreciation, amortization (INR) | 12000000 |
| **Long-Term Debt** | Numeric | Long-term debt (INR) | 15000000 |
| **Cheque Bounces** | Numeric | Number of bounced cheques | 0 |
| **NACH Returns** | Numeric | Number of NACH returns | 0 |
| **OD Utilization** | Numeric | Overdraft utilization % | 45.5 |
| **NACH Obligation %** | Numeric | NACH obligation percentage | 30.0 |
| **CMR Rank** | Numeric | Credit Monitoring Rank (1-5) | 2 |
| **Asset Classification** | Categorical | Standard/Sub-Standard/Doubtful/Loss | Standard |
| **Wilful Defaulter** | Categorical | Yes/No | No |
| **Capacity Utilization** | Numeric | Factory capacity utilization % | 75.0 |
| **Machinery Status** | Categorical | Good/Average/Poor | Good |
| **Promoter Experience** | Numeric | Years of experience | 15 |
| **Contingent Liabilities** | Numeric | Contingent liabilities (INR) | 500000 |
| **Auditor Qualifications** | Categorical | Unqualified/Qualified/Adverse/Disclaimer | Unqualified |
| **Shareholding Pledge** | Numeric | % of shares pledged | 25.0 |
| **Risk Premium** | Numeric | Risk premium in % | 2.5 |
| **Target_Decision** | Categorical | **APPROVE/REJECT** (Target variable) | APPROVE |

## Feature Engineering

The system automatically engineers additional features:

### Financial Ratios
- **Debt to EBITDA**: Long-Term Debt / EBITDA
- **Receivables to Income**: Accounts Receivable / Net Income
- **Inventory to Income**: Inventory / Net Income

### Risk Indicators
- **Total Payment Failures**: Cheque Bounces + NACH Returns
- **High GSTR Variance**: Flag if variance > 10%
- **High Pledge Risk**: Flag if pledge > 50%
- **Low Capacity Risk**: Flag if utilization < 60%

### Derived Features
- **Company Age**: Calculated from Date of Incorporation
- **Categorical Encodings**: All categorical variables encoded

## Usage

### 1. Create Sample CSV

```bash
python train_model.py --sample
```

This creates `sample_training_data.csv` with the correct format.

### 2. Prepare Your Data

Format your historical credit decisions as CSV with all required columns.

**Example:**
```csv
CIN,LLPIN,Entity Status,Date of Incorporation,Paid-up Capital,...,Target_Decision
U12345MH2020PTC123456,AAA-1234,Active,2020-01-15,10000000,...,APPROVE
U67890DL2018PTC789012,BBB-5678,Active,2018-06-20,5000000,...,REJECT
```

### 3. Train Model

```bash
python train_model.py path/to/your_data.csv
```

**Output:**
```
============================================================
🤖 TRAINING CREDIT DECISION MODEL
============================================================

📂 Loading data from: your_data.csv

✓ Loaded 1000 records from CSV
✓ Columns: [list of columns]
✓ Training set: 800 samples
✓ Test set: 200 samples
✓ Features: 35
✓ Approval rate: 65.0%
✓ Model trained on 800 samples with 35 features
✓ Test accuracy: 87.5%
✓ Model saved to: credit_engine/trained_model.pkl
✓ Handler saved to: credit_engine/csv_handler.pkl

============================================================
✅ TRAINING COMPLETE
============================================================
```

### 4. Use Trained Model

The web portal automatically loads the trained model if available:

```python
# In web_portal.py
import joblib

try:
    ml_model = joblib.load('credit_engine/trained_model.pkl')
    csv_handler = joblib.load('credit_engine/csv_handler.pkl')
    print("✓ Loaded trained model from CSV data")
except:
    ml_model = CreditDecisionModel()
    # Use default model
```

## Data Preprocessing

### Automatic Handling

1. **Missing Values**: Filled with 0 for numeric, 'Unknown' for categorical
2. **Date Conversion**: Dates converted to company age in years
3. **Categorical Encoding**: Label encoding for all categorical variables
4. **Feature Scaling**: StandardScaler applied to all features
5. **Identifier Removal**: CIN, LLPIN, PAN, GSTIN removed (not used for prediction)

### Train-Test Split

- **Training**: 80% of data
- **Testing**: 20% of data
- **Stratified**: Maintains approval/rejection ratio

## Model Architecture

### Approval Model
- **Algorithm**: Gradient Boosting Classifier
- **Parameters**: 100 estimators, max depth 5
- **Output**: APPROVE/REJECT decision

### Credit Limit Model (Optional)
- **Algorithm**: Random Forest Regressor
- **Trained on**: Only approved cases
- **Output**: Recommended credit limit

### Risk Model (Optional)
- **Algorithm**: Random Forest Regressor
- **Output**: Default probability

## Performance Metrics

After training, the system reports:

- **Test Accuracy**: % of correct predictions
- **Approval Rate**: % of approvals in training data
- **Feature Count**: Number of features used
- **Sample Count**: Training and test set sizes

## Best Practices

### Data Quality

1. **Minimum Records**: At least 500 records for reliable training
2. **Balanced Dataset**: 40-60% approval rate ideal
3. **Complete Data**: Minimize missing values
4. **Recent Data**: Use last 2-3 years of decisions
5. **Consistent Format**: Ensure all columns match specification

### Data Collection

```python
# Collect from existing systems
historical_data = {
    'CIN': cin_from_mca,
    'Paid-up Capital': from_annual_report,
    'GSTR Variance %': calculated_from_gst_filings,
    'Audited Net Income': from_financial_statements,
    'Cheque Bounces': from_bank_statements,
    'Target_Decision': actual_decision_made
}
```

### Incremental Training

Retrain model periodically with new decisions:

```bash
# Monthly retraining
python train_model.py historical_decisions_2024.csv
```

## Integration with Document Parsing

The system combines CSV training with document parsing:

1. **Upload Documents** → AI extracts data
2. **Map to CSV Format** → Extracted data mapped to CSV columns
3. **Apply Trained Model** → Prediction using CSV-trained model
4. **Generate Decision** → Final decision with reasoning

## Example Workflow

### Step 1: Collect Historical Data

```python
import pandas as pd

# Load from database
historical = pd.read_sql("""
    SELECT cin, llpin, entity_status, ...
    FROM credit_applications
    WHERE decision_date >= '2022-01-01'
""", connection)

# Save as CSV
historical.to_csv('training_data.csv', index=False)
```

### Step 2: Train Model

```bash
python train_model.py training_data.csv
```

### Step 3: Deploy

Model automatically loaded by web portal on startup.

### Step 4: Monitor & Retrain

```python
# Track predictions vs actual outcomes
# Retrain monthly with new data
```

## Troubleshooting

### "Column not found"
- Ensure CSV has all required columns
- Check column names match exactly (case-sensitive)

### "Low accuracy"
- Need more training data (>500 records)
- Check data quality and consistency
- Verify target variable is correct

### "Model not loading"
- Check if .pkl files exist in credit_engine/
- Retrain model if files corrupted

## Advanced Features

### Custom Feature Engineering

Edit `csv_handler.py` to add domain-specific features:

```python
def engineer_features(self, df):
    # Add custom features
    df['custom_ratio'] = df['col1'] / df['col2']
    return df
```

### Hyperparameter Tuning

Edit `ml_model.py` to optimize model parameters:

```python
self.approval_model = GradientBoostingClassifier(
    n_estimators=200,  # Increase for better accuracy
    max_depth=7,       # Increase for complex patterns
    learning_rate=0.05 # Decrease for stability
)
```

## Cost & Performance

- **Training Time**: 5-30 seconds (depends on data size)
- **Model Size**: ~5-10 MB
- **Prediction Time**: <100ms per application
- **Accuracy**: 85-95% (with good training data)

## Next Steps

1. ✅ Create sample CSV: `python train_model.py --sample`
2. ✅ Prepare your historical data in CSV format
3. ✅ Train model: `python train_model.py your_data.csv`
4. ✅ Test predictions via web portal
5. Monitor accuracy and retrain periodically
