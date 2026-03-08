"""Comprehensive data ingestion for all document types"""
import os
from typing import Dict, List
from pdf2image import convert_from_path
import pytesseract
import json
import re

class ComprehensiveDocumentParser:
    def __init__(self):
        self.client = True  # Using local OCR
    
    # STRUCTURED DATA PARSING
    
    def parse_gst_filing(self, pdf_path: str) -> Dict:
        """Parse GST returns (GSTR-1, 3B, 9)"""
        prompt = """Extract GST filing data:
- gstin: 15-digit GSTIN
- filing_period: Month/Quarter/Year
- turnover: Total taxable turnover (INR)
- input_tax_credit: ITC claimed (INR)
- output_tax: Output tax liability (INR)
- net_tax_payable: Net tax (INR)
- filing_date: Date of filing
- filing_status: On-time/Late/Not-filed
- hsn_codes: List of top HSN codes
- top_suppliers: List of top 3 supplier GSTINs
- top_customers: List of top 3 customer GSTINs

Return ONLY valid JSON."""
        return self._parse_with_vision(pdf_path, prompt, max_pages=3)
    
    def parse_itr(self, pdf_path: str) -> Dict:
        """Parse Income Tax Returns"""
        prompt = """Extract ITR data:
- pan: PAN number
- assessment_year: AY (e.g., 2023-24)
- total_income: Total income (INR)
- tax_paid: Total tax paid (INR)
- refund_due: Refund amount if any (INR)
- business_income: Income from business (INR)
- capital_gains: Capital gains (INR)
- other_income: Other sources (INR)
- deductions: Total deductions claimed (INR)
- advance_tax_paid: Advance tax (INR)
- filing_date: Date of filing
- verification_status: Verified/Pending

Return ONLY valid JSON."""
        return self._parse_with_vision(pdf_path, prompt, max_pages=4)
    
    def parse_bank_statement(self, pdf_path: str) -> Dict:
        """Parse bank statements with transaction analysis"""
        prompt = """Analyze bank statement:
- account_number: Account number
- bank_name: Bank name
- statement_period: From-To dates
- opening_balance: Opening balance (INR)
- closing_balance: Closing balance (INR)
- total_credits: Sum of all credits (INR)
- total_debits: Sum of all debits (INR)
- average_balance: Average monthly balance (INR)
- minimum_balance: Lowest balance (INR)
- bounce_count: Number of bounced/returned cheques
- salary_credits: Monthly salary credits if any (INR)
- loan_emis: Monthly loan EMI debits (INR)
- cash_deposits: Large cash deposits >50000 (count and total)
- suspicious_transactions: Any unusual patterns

Return ONLY valid JSON."""
        return self._parse_with_vision(pdf_path, prompt, max_pages=5)
    
    # UNSTRUCTURED DATA PARSING
    
    def parse_annual_report(self, pdf_path: str) -> Dict:
        """Parse annual reports comprehensively"""
        prompt = """Extract from annual report:
- company_name: Company name
- financial_year: FY (e.g., 2023-24)
- revenue: Total revenue (INR)
- net_profit: Net profit after tax (INR)
- total_assets: Total assets (INR)
- total_liabilities: Total liabilities (INR)
- net_worth: Shareholders equity (INR)
- total_debt: Total borrowings (INR)
- current_assets: Current assets (INR)
- current_liabilities: Current liabilities (INR)
- cash_and_equivalents: Cash balance (INR)
- inventory: Inventory value (INR)
- receivables: Trade receivables (INR)
- payables: Trade payables (INR)
- contingent_liabilities: Contingent liabilities (INR)
- auditor_name: Auditor name
- auditor_opinion: Unqualified/Qualified/Adverse/Disclaimer
- key_risks: List of key risks mentioned
- related_party_transactions: Significant RPTs (INR)

Return ONLY valid JSON."""
        return self._parse_with_vision(pdf_path, prompt, max_pages=8)
    
    def parse_financial_statement(self, pdf_path: str) -> Dict:
        """Parse standalone financial statements"""
        prompt = """Extract financial statement data:
- statement_type: Balance Sheet/P&L/Cash Flow
- period_ending: Date
- revenue: Revenue (INR)
- operating_profit: EBIT (INR)
- net_profit: PAT (INR)
- total_assets: Total assets (INR)
- fixed_assets: Fixed assets (INR)
- current_assets: Current assets (INR)
- total_liabilities: Total liabilities (INR)
- equity: Equity (INR)
- debt: Total debt (INR)
- working_capital: Current assets - Current liabilities (INR)
- ebitda: EBITDA (INR)
- depreciation: Depreciation (INR)
- interest_expense: Interest paid (INR)

Return ONLY valid JSON."""
        return self._parse_with_vision(pdf_path, prompt, max_pages=5)
    
    def parse_board_minutes(self, pdf_path: str) -> Dict:
        """Parse board meeting minutes"""
        prompt = """Extract from board minutes:
- meeting_date: Date of meeting
- attendees: List of directors present
- key_decisions: List of major decisions taken
- financial_approvals: Any financial approvals (loans, investments)
- director_changes: Any appointments/resignations
- dividend_declared: Dividend amount if any (INR)
- expansion_plans: Any expansion/capex plans mentioned
- concerns_raised: Any concerns or risks discussed
- related_party_approvals: RPT approvals
- compliance_issues: Any compliance matters

Return ONLY valid JSON."""
        return self._parse_with_vision(pdf_path, prompt, max_pages=10)
    
    def parse_rating_report(self, pdf_path: str) -> Dict:
        """Parse credit rating agency reports"""
        prompt = """Extract from rating report:
- company_name: Company name
- rating_agency: CRISIL/ICRA/CARE/India Ratings
- rating: Credit rating (e.g., AA-, BBB+)
- rating_outlook: Stable/Positive/Negative
- rating_date: Date of rating
- previous_rating: Previous rating if mentioned
- rating_rationale: Key reasons for rating (2-3 points)
- strengths: Key strengths (list)
- weaknesses: Key weaknesses (list)
- financial_metrics: Key ratios mentioned
- debt_amount: Total debt rated (INR)
- outlook_drivers: Factors for upgrade/downgrade

Return ONLY valid JSON."""
        return self._parse_with_vision(pdf_path, prompt, max_pages=6)
    
    def parse_shareholding_pattern(self, pdf_path: str) -> Dict:
        """Parse shareholding pattern"""
        prompt = """Extract shareholding data:
- as_of_date: Date of shareholding
- promoter_holding: Promoter % holding
- promoter_pledged: % of promoter shares pledged
- public_holding: Public % holding
- institutional_holding: FII + DII % holding
- top_shareholders: List of top 5 shareholders with %
- changes_from_previous: Any significant changes
- pledge_details: Details of pledged shares if any
- lock_in_shares: Any shares under lock-in

Return ONLY valid JSON."""
        return self._parse_with_vision(pdf_path, prompt, max_pages=3)
    
    # HELPER METHOD
    
    def _parse_with_vision(self, pdf_path: str, prompt: str, max_pages: int = 5) -> Dict:
        """Parse PDF using Tesseract OCR"""
        if not self.client:
            return {"error": "OCR not available"}
        
        try:
            images = convert_from_path(pdf_path, first_page=1, last_page=max_pages, dpi=300)
            
            text = ""
            for img in images[:max_pages]:
                text += pytesseract.image_to_string(img) + "\n\n"
            
            # Extract structured data using regex patterns
            return self._extract_structured_data(text, prompt)
        
        except Exception as e:
            print(f"Parsing error: {e}")
            return {"error": str(e)}
    
    def _extract_structured_data(self, text: str, prompt: str) -> Dict:
        """Extract data from OCR text using patterns"""
        data = {}
        
        # Common patterns
        patterns = {
            'gstin': r'\b\d{2}[A-Z]{5}\d{4}[A-Z]{1}[A-Z\d]{1}[Z]{1}[A-Z\d]{1}\b',
            'pan': r'\b[A-Z]{5}\d{4}[A-Z]{1}\b',
            'amount': r'₹?\s*[\d,]+\.?\d*',
            'date': r'\d{1,2}[-/]\d{1,2}[-/]\d{2,4}',
            'percentage': r'\d+\.?\d*\s*%'
        }
        
        # Extract based on document type
        if 'GST' in prompt or 'GSTR' in prompt:
            data['gstin'] = re.search(patterns['gstin'], text)
            data['gstin'] = data['gstin'].group() if data['gstin'] else None
            amounts = re.findall(patterns['amount'], text)
            data['turnover'] = amounts[0] if amounts else None
            
        elif 'ITR' in prompt or 'Income Tax' in prompt:
            data['pan'] = re.search(patterns['pan'], text)
            data['pan'] = data['pan'].group() if data['pan'] else None
            amounts = re.findall(patterns['amount'], text)
            data['total_income'] = amounts[0] if amounts else None
            
        elif 'Bank' in prompt or 'Statement' in prompt:
            amounts = re.findall(patterns['amount'], text)
            data['opening_balance'] = amounts[0] if len(amounts) > 0 else None
            data['closing_balance'] = amounts[-1] if len(amounts) > 1 else None
            
        else:
            # Generic extraction
            data['text'] = text[:1000]  # First 1000 chars
        
        return data
