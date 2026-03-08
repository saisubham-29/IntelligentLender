# AI Document Parsing Setup Guide

## Overview

The system now uses **OpenAI GPT-4 Vision** to intelligently extract structured data from uploaded PDF documents instead of basic regex patterns.

## What Changed

### Before (Regex-based)
- Simple keyword matching ("revenue", "profit")
- Failed on complex layouts or handwritten text
- No context understanding
- Missed data in tables/images

### After (AI-powered)
- Understands document structure and context
- Extracts data from any format (tables, text, images)
- Handles Indian number formats (lakhs, crores)
- Returns structured JSON data

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

New packages added:
- `openai>=1.12.0` - OpenAI API client
- `pdf2image>=1.16.3` - Convert PDF to images
- `Pillow>=10.0.0` - Image processing

### 2. Install System Dependencies

**For pdf2image (required):**

**macOS:**
```bash
brew install poppler
```

**Ubuntu/Debian:**
```bash
sudo apt-get install poppler-utils
```

**Windows:**
Download poppler from: https://github.com/oschwartz10612/poppler-windows/releases

### 3. Get OpenAI API Key

1. Go to https://platform.openai.com/api-keys
2. Create a new API key
3. Set environment variable:

```bash
export OPENAI_API_KEY='sk-...'
```

Or add to `.env` file:
```
OPENAI_API_KEY=sk-...
```

### 4. Configure Model (Optional)

Edit `credit_engine/config.py`:

```python
OPENAI_CONFIG = {
    "api_key": "your-openai-api-key",
    "model": "gpt-4o-mini",  # Cost-effective: ~$0.15/1K images
    "max_tokens": 2000
}
```

**Model Options:**
- `gpt-4o-mini` - Recommended, cheapest ($0.15/1K images)
- `gpt-4o` - More accurate but expensive ($2.50/1K images)

## How It Works

### 1. PDF Upload
User uploads financial statement, bank statement, or GST return

### 2. PDF → Images
System converts first 1-3 pages to images (150 DPI)

### 3. AI Analysis
GPT-4 Vision analyzes images and extracts:

**Financial Statement:**
- Revenue, Net Profit, Total Debt
- Total Assets, Net Worth
- Contingent Liabilities
- Auditor Opinion

**Bank Statement:**
- Account details, Balances
- Total Credits/Debits
- Bounce count
- Suspicious patterns

**GST Returns:**
- GSTIN, Turnover
- Tax credits and liabilities
- Filing status

### 4. Structured Output
Returns JSON with extracted data, used for credit decision

## Cost Estimation

**Per Document:**
- 1-page PDF: ~$0.0002 (₹0.02)
- 3-page PDF: ~$0.0005 (₹0.04)

**Monthly (1000 applications):**
- ~$0.50 (₹40) with gpt-4o-mini

## Fallback Behavior

If OpenAI API key not set or API fails:
- Returns empty data structure
- Shows warning: "AI parsing unavailable"
- System continues with manual form data

## Testing

### Test with Sample Document

```python
from credit_engine.ai_document_parser import AIDocumentParser

parser = AIDocumentParser()
result = parser.parse_annual_report('sample_financial_statement.pdf')
print(result)
```

Expected output:
```json
{
  "revenue": 50000000,
  "net_profit": 4000000,
  "total_debt": 20000000,
  "total_assets": 60000000,
  "net_worth": 25000000,
  "contingent_liabilities": 0,
  "auditor_opinion": "Unqualified opinion"
}
```

## Troubleshooting

### "AI parsing unavailable"
- Check OPENAI_API_KEY is set
- Verify API key is valid
- Check internet connectivity

### "pdf2image error"
- Install poppler (see step 2)
- Verify PDF is not corrupted

### "Rate limit exceeded"
- Upgrade OpenAI plan
- Add retry logic with exponential backoff

## Security Notes

- Never commit API keys to git
- Use environment variables
- Rotate keys regularly
- Monitor usage on OpenAI dashboard

## Next Steps

1. Set OPENAI_API_KEY environment variable
2. Install poppler system dependency
3. Test with sample PDF
4. Monitor costs on OpenAI dashboard
