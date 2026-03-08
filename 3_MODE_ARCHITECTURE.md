# 3-Mode Architecture - User Guide

## Overview

The Intelli-Credit system now has **3 independent modes** that can work standalone OR be triggered sequentially from the homepage.

## Homepage Structure

```
┌─────────────────────────────────────────────────────────────┐
│                    INTELLI-CREDIT HOMEPAGE                  │
│                   http://localhost:5000                     │
└─────────────────────────────────────────────────────────────┘
                              │
                ┌─────────────┼─────────────┬─────────────┐
                │             │             │             │
                ▼             ▼             ▼             ▼
         ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐
         │  MODE 1  │  │  MODE 2  │  │  MODE 3  │  │   FULL   │
         │   📊     │  │   🔍     │  │   💡     │  │   FLOW   │
         │  Data    │  │ Digital  │  │Recommend │  │   🚀     │
         │ Ingestor │  │  Credit  │  │  Engine  │  │          │
         │          │  │ Manager  │  │          │  │ All 3    │
         └──────────┘  └──────────┘  └──────────┘  └──────────┘
```

## Mode 1: Data Ingestor 📊

**Purpose**: Parse documents and extract insights independently

**URL**: `/mode1`

**Features**:
- Upload documents (GST, Bank Statement, Annual Report, ITR)
- Extract structured data using GPT-4 Vision
- Cross-verify GST vs Bank statements
- Detect circular trading patterns
- Calculate extraction quality score

**Use Case**: 
> "I just want to parse these documents and see what data I can extract"

**API Endpoint**: `POST /api/mode1/ingest`

**Response**:
```json
{
  "documents_parsed": [...],
  "extraction_quality": "HIGH",
  "verification_results": {
    "gst_bank_variance": 5.2,
    "circular_trading_detected": false
  }
}
```

---

## Mode 2: Digital Credit Manager 🔍

**Purpose**: Conduct research and gather insights independently

**URL**: `/mode2`

**Features**:
- **Tab 1: Secondary Research**
  - Web crawling for company news
  - Promoter background checks
  - Sector trend analysis
  - Litigation history
  - MCA filings search
  
- **Tab 2: Site Visit**
  - Record capacity utilization
  - Document machinery condition
  - Add qualitative observations
  
- **Tab 3: Management Interview**
  - Rate management quality (1-10)
  - Flag red flags
  - Add interview notes

**Use Case**: 
> "I want to research this company and add my site visit notes"

**API Endpoints**:
- `POST /api/mode2/research` - Conduct web research
- `POST /api/mode2/site_visit` - Add site visit notes
- `POST /api/mode2/interview` - Add interview notes

**Response**:
```json
{
  "research_summary": "...",
  "research_risk_score": 65,
  "key_findings": [
    "Promoter has clean track record",
    "Sector facing regulatory headwinds",
    "2 pending litigations found"
  ]
}
```

---

## Mode 3: Recommendation Engine 💡

**Purpose**: Generate credit decisions and CAM reports independently

**URL**: `/mode3`

**Features**:
- Enter company information
- Input financial data (Revenue, EBITDA, Debt, etc.)
- Optional: Paste research findings
- Analyze **Five Cs of Credit**:
  1. **Character** - Promoter background, litigation
  2. **Capacity** - Cash flow, profitability
  3. **Capital** - Net worth, leverage
  4. **Collateral** - Asset coverage
  5. **Conditions** - Sector trends, macro factors
- Make APPROVE/REJECT decision
- Calculate approved amount & interest rate
- Generate professional CAM document
- Provide transparent explanation

**Use Case**: 
> "I have all the data, just give me a decision and CAM report"

**API Endpoint**: `POST /api/mode3/recommend`

**Response**:
```json
{
  "decision": "APPROVE",
  "approved_amount": 5000000,
  "interest_rate": 12.5,
  "five_cs_analysis": {
    "character": {"score": 85, "notes": "..."},
    "capacity": {"score": 78, "notes": "..."},
    "capital": {"score": 72, "notes": "..."},
    "collateral": {"score": 80, "notes": "..."},
    "conditions": {"score": 65, "notes": "..."}
  },
  "decision_explanation": "Approved due to strong promoter track record...",
  "cam_document": "CREDIT APPRAISAL MEMO\n\n..."
}
```

---

## Full Flow 🚀

**Purpose**: Run all 3 modes sequentially for complete analysis

**URL**: `/full-flow`

**Process**:
1. Upload all documents
2. **Section 1** parses and verifies
3. **Section 2** conducts research
4. **Section 3** makes decision and generates CAM
5. Display comprehensive results

**Use Case**: 
> "I want the complete end-to-end credit appraisal"

**API Endpoint**: `POST /api/process_with_files`

**Response**: Combined output from all 3 sections

---

## When to Use Each Mode

| Scenario | Mode to Use |
|----------|-------------|
| Just need to extract data from documents | Mode 1 |
| Want to research a company online | Mode 2 |
| Need to add site visit notes | Mode 2 |
| Have all data, need decision + CAM | Mode 3 |
| Complete credit appraisal from scratch | Full Flow |
| Testing document parsing accuracy | Mode 1 |
| Checking web research quality | Mode 2 |
| Validating decision logic | Mode 3 |

---

## Technical Architecture

```
web_portal.py
├── Route: /                    → home.html (4 options)
├── Route: /mode1               → mode1.html
├── Route: /mode2               → mode2.html
├── Route: /mode3               → mode3.html
├── Route: /full-flow           → index.html
│
├── API: /api/mode1/ingest      → Section 1: DataIngestor
├── API: /api/mode2/research    → Section 2: ResearchAgent
├── API: /api/mode2/site_visit  → Section 2: ResearchAgent
├── API: /api/mode2/interview   → Section 2: ResearchAgent
├── API: /api/mode3/recommend   → Section 3: RecommendationEngine
└── API: /api/process_with_files → All 3 Sections
```

---

## Color Coding

Each mode has a distinct visual identity:

- **Mode 1** (Data Ingestor): Purple gradient (#667eea → #764ba2)
- **Mode 2** (Digital Credit Manager): Pink gradient (#f093fb → #f5576c)
- **Mode 3** (Recommendation Engine): Blue gradient (#4facfe → #00f2fe)
- **Full Flow**: Purple gradient (matches Mode 1)

---

## Getting Started

1. Start the server:
   ```bash
   python web_portal.py
   ```

2. Open browser:
   ```
   http://localhost:5000
   ```

3. Choose your mode:
   - Click on any of the 3 mode cards for standalone operation
   - Click "Start Full Analysis" for complete flow

4. Each mode has a "Back to Home" button to return to the homepage

---

## Benefits of This Architecture

✅ **Modularity**: Each section works independently  
✅ **Flexibility**: Use only what you need  
✅ **Testing**: Test each component separately  
✅ **User Experience**: Clear navigation and purpose  
✅ **Scalability**: Easy to add more modes  
✅ **Maintainability**: Clean separation of concerns  

---

## API Integration

All modes expose REST APIs, so you can:
- Build mobile apps
- Integrate with other systems
- Automate workflows
- Create custom dashboards

Example using curl:
```bash
# Mode 1: Parse documents
curl -X POST http://localhost:5000/api/mode1/ingest \
  -F "gst_filing=@gst.pdf" \
  -F "bank_statement=@bank.xlsx"

# Mode 2: Research company
curl -X POST http://localhost:5000/api/mode2/research \
  -H "Content-Type: application/json" \
  -d '{"company_name": "ABC Ltd", "sector": "NBFC"}'

# Mode 3: Get decision
curl -X POST http://localhost:5000/api/mode3/recommend \
  -H "Content-Type: application/json" \
  -d '{"company_name": "ABC Ltd", "revenue": 10000000, ...}'
```

---

## Next Steps

1. Test each mode independently
2. Try the full flow with sample documents
3. Customize the UI as needed
4. Add more features to each mode
5. Integrate with your existing systems

---

**Questions?** Check the main README.md or THREE_SECTION_ARCHITECTURE.md for more details.
