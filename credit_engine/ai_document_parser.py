"""AI-powered document parser using OpenAI GPT-4 Vision + Groq for text processing"""
import os
import base64
import json
from typing import Dict, List
from pdf2image import convert_from_path
from openai import OpenAI
from groq import Groq
import pdfplumber
from .config import OPENAI_CONFIG

class AIDocumentParser:
    def __init__(self):
        api_key = os.getenv('OPENAI_API_KEY', OPENAI_CONFIG.get('api_key'))
        self.client = OpenAI(api_key=api_key) if api_key and api_key != 'your-openai-api-key' and api_key != 'OPENAI_API_KEY' else None
        
        groq_key = os.getenv('GROQ_API_KEY')
        self.groq_client = Groq(api_key=groq_key) if groq_key else None
        
        self.model = OPENAI_CONFIG.get('model', 'gpt-4o-mini')
        self.use_groq_fallback = True  # Use Groq if OpenAI fails
    
    def parse_annual_report(self, pdf_path: str) -> Dict:
        """Extract financial metrics from annual report using AI"""
        if not self.client:
            return self._fallback_parse()
        
        prompt = """You are a financial analyst. Extract EXACT numerical values from this financial document.

Extract these fields (all amounts in INR):
- revenue: Total revenue/turnover (convert lakhs/crores to actual number)
- net_profit: Net profit after tax (can be negative)
- total_debt: Total borrowings/debt
- total_assets: Total assets
- net_worth: Net worth/shareholders equity
- contingent_liabilities: Contingent liabilities (0 if not mentioned)
- auditor_opinion: Auditor's opinion (Unqualified/Qualified/Adverse/Disclaimer)

IMPORTANT:
- Convert "45.5 Cr" to 455000000
- Convert "12.3 Lakhs" to 1230000
- If value not found, use 0
- Return ONLY valid JSON, no explanation

Example: {"revenue": 125000000, "net_profit": 12000000, ...}"""
        
        return self._parse_with_vision(pdf_path, prompt, max_pages=5)
    
    def parse_bank_statement(self, pdf_path: str) -> Dict:
        """Extract bank statement summary using AI"""
        if not self.client:
            return self._fallback_parse()
        
        prompt = """You are analyzing a bank statement. Extract these details:

- account_number: Bank account number
- opening_balance: Opening balance in INR
- closing_balance: Closing balance in INR  
- total_credits: Sum of all credit transactions in INR
- total_debits: Sum of all debit transactions in INR
- average_balance: Average monthly balance in INR
- bounce_count: Number of bounced/returned transactions
- suspicious_patterns: List any unusual patterns (large cash deposits, round-tripping, etc.)

Convert all amounts to actual numbers (no lakhs/crores notation).
Return ONLY valid JSON."""
        
        return self._parse_with_vision(pdf_path, prompt, max_pages=3)
    
    def parse_gst_returns(self, pdf_path: str) -> Dict:
        """Extract GST return data using AI"""
        if not self.client:
            return self._fallback_parse()
        
        prompt = """Extract GST return information from this document:

- gstin: 15-digit GSTIN number
- turnover: Total taxable turnover in INR
- input_tax_credit: Total ITC claimed in INR
- output_tax: Total output tax liability in INR
- tax_liability: Net tax payable in INR
- filing_status: "Compliant" if filed on time, "Non-compliant" if late/not filed

Convert all amounts to actual numbers.
Return ONLY valid JSON."""
        
        return self._parse_with_vision(pdf_path, prompt, max_pages=2)
    
    def _parse_with_vision(self, pdf_path: str, prompt: str, max_pages: int = 1) -> Dict:
        """Parse PDF using GPT-4 Vision"""
        try:
            # Convert PDF to images
            images = convert_from_path(pdf_path, first_page=1, last_page=max_pages, dpi=150)
            
            # Prepare messages with images
            messages = [{"role": "user", "content": [{"type": "text", "text": prompt}]}]
            
            for img in images[:max_pages]:
                # Convert to base64
                import io
                buffer = io.BytesIO()
                img.save(buffer, format='PNG')
                img_base64 = base64.b64encode(buffer.getvalue()).decode()
                
                messages[0]["content"].append({
                    "type": "image_url",
                    "image_url": {"url": f"data:image/png;base64,{img_base64}"}
                })
            
            # Call OpenAI
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=OPENAI_CONFIG.get('max_tokens', 2000),
                temperature=0
            )
            
            # Parse JSON response
            content = response.choices[0].message.content
            # Extract JSON from markdown code blocks if present
            if '```json' in content:
                content = content.split('```json')[1].split('```')[0].strip()
            elif '```' in content:
                content = content.split('```')[1].split('```')[0].strip()
            
            return json.loads(content)
        
        except Exception as e:
            print(f"AI parsing error: {e}")
            # Try Groq fallback with OCR text
            if self.groq_client and self.use_groq_fallback:
                return self._parse_with_groq(pdf_path, prompt)
            return self._fallback_parse()
    
    def _parse_with_groq(self, pdf_path: str, prompt: str) -> Dict:
        """Parse document using Groq after OCR text extraction"""
        try:
            # Extract text from PDF using pdfplumber
            text_content = ""
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages[:5]:  # First 5 pages
                    text_content += page.extract_text() or ""
            
            if not text_content.strip():
                return self._fallback_parse()
            
            # Use Groq to analyze the text
            response = self.groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{
                    "role": "user",
                    "content": f"{prompt}\n\nDocument text:\n{text_content[:8000]}"  # Limit to 8K chars
                }],
                temperature=0,
                max_tokens=2000
            )
            
            content = response.choices[0].message.content
            # Extract JSON from markdown code blocks if present
            if '```json' in content:
                content = content.split('```json')[1].split('```')[0].strip()
            elif '```' in content:
                content = content.split('```')[1].split('```')[0].strip()
            
            print(f"✓ Groq parsed document successfully")
            return json.loads(content)
        
        except Exception as e:
            print(f"Groq parsing error: {e}")
            return self._fallback_parse()
    
    def _fallback_parse(self) -> Dict:
        """Return empty dict when AI unavailable"""
        return {
            'revenue': 0,
            'net_profit': 0,
            'total_debt': 0,
            'total_assets': 0,
            'net_worth': 0,
            'error': 'AI parsing unavailable - set OPENAI_API_KEY'
        }
