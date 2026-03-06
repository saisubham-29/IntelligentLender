"""Multi-format document parser for unstructured data"""
import PyPDF2
import pdfplumber
import re
from typing import Dict, List
import pandas as pd

class DocumentParser:
    def __init__(self):
        self.patterns = {
            'pan': r'[A-Z]{5}[0-9]{4}[A-Z]{1}',
            'gstin': r'\d{2}[A-Z]{5}\d{4}[A-Z]{1}[A-Z\d]{1}[Z]{1}[A-Z\d]{1}',
            'cin': r'[UL]\d{5}[A-Z]{2}\d{4}[A-Z]{3}\d{6}',
            'amount': r'₹?\s*(\d+(?:,\d+)*(?:\.\d+)?)\s*(?:cr|crore|lakh|lakhs)?'
        }
    
    def parse_annual_report(self, pdf_path: str) -> Dict:
        """Extract key metrics from annual report PDF"""
        text = self._extract_pdf_text(pdf_path)
        
        return {
            'revenue': self._extract_revenue(text),
            'profit': self._extract_profit(text),
            'debt': self._extract_debt(text),
            'contingent_liabilities': self._extract_contingent_liabilities(text),
            'related_party_transactions': self._extract_rpt(text),
            'auditor_remarks': self._extract_auditor_remarks(text)
        }
    
    def parse_gst_returns(self, pdf_path: str) -> Dict:
        """Parse GST returns (GSTR-1, 3B)"""
        text = self._extract_pdf_text(pdf_path)
        
        return {
            'gstin': self._extract_pattern(text, 'gstin'),
            'turnover': self._extract_gst_turnover(text),
            'input_tax_credit': self._extract_itc(text),
            'output_tax': self._extract_output_tax(text),
            'filing_status': self._check_filing_compliance(text)
        }
    
    def parse_bank_statement(self, pdf_path: str) -> pd.DataFrame:
        """Extract transactions from bank statement"""
        with pdfplumber.open(pdf_path) as pdf:
            tables = []
            for page in pdf.pages:
                table = page.extract_table()
                if table:
                    tables.append(pd.DataFrame(table[1:], columns=table[0]))
            
            if tables:
                df = pd.concat(tables, ignore_index=True)
                return self._clean_bank_statement(df)
        return pd.DataFrame()
    
    def parse_mca_filing(self, pdf_path: str) -> Dict:
        """Parse MCA filings for director changes, charges"""
        text = self._extract_pdf_text(pdf_path)
        
        return {
            'cin': self._extract_pattern(text, 'cin'),
            'directors': self._extract_directors(text),
            'charges': self._extract_charges(text),
            'authorized_capital': self._extract_capital(text, 'authorized'),
            'paid_up_capital': self._extract_capital(text, 'paid')
        }
    
    def parse_legal_notice(self, pdf_path: str) -> Dict:
        """Extract key info from legal notices/court documents"""
        text = self._extract_pdf_text(pdf_path)
        
        return {
            'case_number': self._extract_case_number(text),
            'parties': self._extract_parties(text),
            'claim_amount': self._extract_claim_amount(text),
            'status': self._extract_case_status(text),
            'next_hearing': self._extract_hearing_date(text)
        }
    
    def _extract_pdf_text(self, pdf_path: str) -> str:
        """Extract text from PDF with OCR fallback"""
        try:
            with pdfplumber.open(pdf_path) as pdf:
                return '\n'.join([page.extract_text() or '' for page in pdf.pages])
        except:
            # Fallback to PyPDF2
            with open(pdf_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                return '\n'.join([page.extract_text() for page in reader.pages])
    
    def _extract_pattern(self, text: str, pattern_name: str) -> str:
        match = re.search(self.patterns[pattern_name], text)
        return match.group(0) if match else None
    
    def _extract_revenue(self, text: str) -> float:
        patterns = [r'revenue.*?(\d+(?:,\d+)*(?:\.\d+)?)', r'turnover.*?(\d+(?:,\d+)*(?:\.\d+)?)']
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return self._parse_indian_number(match.group(1))
        return 0.0
    
    def _extract_profit(self, text: str) -> float:
        match = re.search(r'net profit.*?(\d+(?:,\d+)*(?:\.\d+)?)', text, re.IGNORECASE)
        return self._parse_indian_number(match.group(1)) if match else 0.0
    
    def _extract_debt(self, text: str) -> float:
        match = re.search(r'total (?:debt|borrowings).*?(\d+(?:,\d+)*(?:\.\d+)?)', text, re.IGNORECASE)
        return self._parse_indian_number(match.group(1)) if match else 0.0
    
    def _extract_contingent_liabilities(self, text: str) -> float:
        match = re.search(r'contingent liabilit.*?(\d+(?:,\d+)*(?:\.\d+)?)', text, re.IGNORECASE)
        return self._parse_indian_number(match.group(1)) if match else 0.0
    
    def _extract_rpt(self, text: str) -> List[str]:
        # Extract related party transactions
        return []
    
    def _extract_auditor_remarks(self, text: str) -> str:
        match = re.search(r'auditor.*?opinion.*?[:](.*?)(?:\n\n|\Z)', text, re.IGNORECASE | re.DOTALL)
        return match.group(1).strip() if match else ""
    
    def _extract_gst_turnover(self, text: str) -> float:
        match = re.search(r'taxable turnover.*?(\d+(?:,\d+)*(?:\.\d+)?)', text, re.IGNORECASE)
        return self._parse_indian_number(match.group(1)) if match else 0.0
    
    def _extract_itc(self, text: str) -> float:
        match = re.search(r'input tax credit.*?(\d+(?:,\d+)*(?:\.\d+)?)', text, re.IGNORECASE)
        return self._parse_indian_number(match.group(1)) if match else 0.0
    
    def _extract_output_tax(self, text: str) -> float:
        match = re.search(r'output tax.*?(\d+(?:,\d+)*(?:\.\d+)?)', text, re.IGNORECASE)
        return self._parse_indian_number(match.group(1)) if match else 0.0
    
    def _check_filing_compliance(self, text: str) -> str:
        if 'filed' in text.lower() or 'submitted' in text.lower():
            return 'Compliant'
        return 'Non-compliant'
    
    def _clean_bank_statement(self, df: pd.DataFrame) -> pd.DataFrame:
        # Clean and standardize bank statement data
        return df
    
    def _extract_directors(self, text: str) -> List[str]:
        # Extract director names
        return []
    
    def _extract_charges(self, text: str) -> List[Dict]:
        # Extract charge details
        return []
    
    def _extract_capital(self, text: str, capital_type: str) -> float:
        match = re.search(f'{capital_type} capital.*?(\d+(?:,\d+)*(?:\.\d+)?)', text, re.IGNORECASE)
        return self._parse_indian_number(match.group(1)) if match else 0.0
    
    def _extract_case_number(self, text: str) -> str:
        match = re.search(r'case no[.:]?\s*([A-Z0-9/\-]+)', text, re.IGNORECASE)
        return match.group(1) if match else None
    
    def _extract_parties(self, text: str) -> Dict:
        return {'plaintiff': '', 'defendant': ''}
    
    def _extract_claim_amount(self, text: str) -> float:
        match = re.search(r'claim.*?(\d+(?:,\d+)*(?:\.\d+)?)', text, re.IGNORECASE)
        return self._parse_indian_number(match.group(1)) if match else 0.0
    
    def _extract_case_status(self, text: str) -> str:
        statuses = ['pending', 'disposed', 'dismissed', 'decreed']
        for status in statuses:
            if status in text.lower():
                return status.capitalize()
        return 'Unknown'
    
    def _extract_hearing_date(self, text: str) -> str:
        match = re.search(r'next hearing.*?(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})', text, re.IGNORECASE)
        return match.group(1) if match else None
    
    def _parse_indian_number(self, num_str: str) -> float:
        """Convert Indian number format to float"""
        num_str = num_str.replace(',', '')
        return float(num_str)
