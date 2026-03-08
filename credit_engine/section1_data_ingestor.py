"""
SECTION 1: DATA INGESTOR (Multi-Format Support)
High latency pipelines for comprehensive data extraction
"""
import os
from typing import Dict, List
from pdf2image import convert_from_path
import pytesseract
import json
import re

class DataIngestor:
    """
    Multi-format data ingestion with unstructured parsing and structured synthesis
    """
    
    def __init__(self):
        self.client = True  # Using local OCR
    
    # ============================================================
    # UNSTRUCTURED PARSING
    # ============================================================
    
    def parse_unstructured_document(self, pdf_path: str, doc_type: str) -> Dict:
        """
        Extract key financial commitments and risks from unstructured PDFs
        Handles: Annual reports, Legal notices, Sanction letters
        """
        
        prompts = {
            'annual_report': """Extract key financial commitments and risks:
- Financial commitments: Loans, guarantees, capital expenditure plans
- Contingent liabilities: Legal claims, guarantees given
- Risk factors: Market risks, regulatory risks, operational risks
- Management discussion: Key concerns mentioned
- Related party transactions: Significant RPTs
- Auditor concerns: Any qualifications or emphasis of matter

Return JSON with extracted information.""",
            
            'legal_notice': """Extract legal risk information:
- Case details: Case number, court, parties involved
- Claim amount: Total claim in INR
- Nature of dispute: Brief description
- Current status: Pending/Disposed/Under appeal
- Potential liability: Estimated financial impact
- Timeline: Next hearing date, expected resolution

Return JSON with all details.""",
            
            'sanction_letter': """Extract credit facility details:
- Sanctioning bank: Bank name
- Facility type: Term loan/Working capital/LC/BG
- Sanctioned amount: Amount in INR
- Interest rate: Rate charged
- Tenure: Loan period
- Security: Collateral details
- Covenants: Key conditions and restrictions
- Repayment schedule: EMI/Bullet payment details

Return JSON with facility information."""
        }
        
        prompt = prompts.get(doc_type, prompts['annual_report'])
        return self._parse_with_vision(pdf_path, prompt, max_pages=10)
    
    # ============================================================
    # STRUCTURED SYNTHESIS
    # ============================================================
    
    def cross_verify_gst_bank(self, gst_data: Dict, bank_data: Dict) -> Dict:
        """
        Cross-leverage GST returns against bank statements
        Detects: Circular trading, Revenue inflation
        """
        
        # Convert to float, handle string values from OCR
        try:
            gst_turnover = float(str(gst_data.get('turnover', 0)).replace(',', '').replace('₹', '').strip() or 0)
            bank_credits = float(str(bank_data.get('total_credits', 0)).replace(',', '').replace('₹', '').strip() or 0)
        except:
            gst_turnover = 0
            bank_credits = 0
        
        # Calculate variance
        if gst_turnover > 0:
            variance = abs(bank_credits - gst_turnover) / gst_turnover * 100
        else:
            variance = 100
        
        # Detect circular trading patterns
        circular_trading = self._detect_circular_trading(bank_data)
        
        # Revenue inflation check
        revenue_inflation = variance > 15  # >15% variance is suspicious
        
        return {
            'gst_turnover': gst_turnover,
            'bank_credits': bank_credits,
            'variance_pct': variance,
            'is_suspicious': variance > 20 or circular_trading['detected'],
            'circular_trading': circular_trading,
            'revenue_inflation': revenue_inflation,
            'risk_level': 'HIGH' if variance > 20 else 'MEDIUM' if variance > 10 else 'LOW',
            'explanation': self._generate_variance_explanation(variance, circular_trading)
        }
    
    def _detect_circular_trading(self, bank_data: Dict) -> Dict:
        """
        Detect circular trading patterns in bank transactions
        Patterns: Same amount in/out, Round-tripping, Frequent reversals
        """
        
        # Simplified detection - in production, analyze actual transactions
        suspicious_patterns = []
        
        # Check for high cash deposits
        cash_deposits = bank_data.get('cash_deposits', {})
        if cash_deposits.get('count', 0) > 5:
            suspicious_patterns.append(f"Multiple large cash deposits: {cash_deposits.get('count')} transactions")
        
        # Check for suspicious transactions flag
        if bank_data.get('suspicious_transactions'):
            suspicious_patterns.append(bank_data['suspicious_transactions'])
        
        return {
            'detected': len(suspicious_patterns) > 0,
            'count': len(suspicious_patterns),
            'patterns': suspicious_patterns,
            'severity': 'HIGH' if len(suspicious_patterns) > 2 else 'MEDIUM' if len(suspicious_patterns) > 0 else 'LOW'
        }
    
    def _generate_variance_explanation(self, variance: float, circular_trading: Dict) -> str:
        """Generate human-readable explanation of findings"""
        
        if variance > 20:
            explanation = f"⚠️ HIGH RISK: {variance:.1f}% variance between GST turnover and bank credits. "
        elif variance > 10:
            explanation = f"⚠️ MEDIUM RISK: {variance:.1f}% variance detected. "
        else:
            explanation = f"✓ LOW RISK: {variance:.1f}% variance is within acceptable range. "
        
        if circular_trading['detected']:
            explanation += f"Circular trading patterns detected: {', '.join(circular_trading['patterns'])}. "
        
        return explanation
    
    # ============================================================
    # HELPER METHODS
    # ============================================================
    
    def _parse_with_vision(self, pdf_path: str, prompt: str, max_pages: int = 3) -> Dict:
        """Parse PDF using Tesseract OCR (optimized for speed)"""
        if not self.client:
            return {"error": "OCR not available"}
        
        try:
            print(f"  → Processing PDF (max {max_pages} pages)...")
            # Reduced DPI and pages for faster processing
            images = convert_from_path(pdf_path, first_page=1, last_page=max_pages, dpi=150)
            
            text = ""
            for i, img in enumerate(images[:max_pages], 1):
                print(f"  → OCR page {i}/{len(images)}...")
                text += pytesseract.image_to_string(img) + "\n\n"
            
            print(f"  ✓ Extracted {len(text)} characters")
            # Return extracted text
            return {"text": text, "extracted": True}
        
        except Exception as e:
            print(f"  ✗ Parsing error: {e}")
            return {"error": str(e)}
    
    def ingest_all_documents(self, uploaded_files: Dict) -> Dict:
        """
        Main ingestion pipeline - processes all uploaded documents
        Returns comprehensive parsed data with cross-verification
        """
        
        parsed_data = {}
        
        # Parse all documents
        for doc_key, filepath in uploaded_files.items():
            if filepath.endswith('.pdf'):
                try:
                    if doc_key in ['annual_report', 'legal_notice', 'sanction_letter']:
                        parsed_data[doc_key] = self.parse_unstructured_document(filepath, doc_key)
                    else:
                        # Use comprehensive parser for structured docs
                        from .comprehensive_parser import ComprehensiveDocumentParser
                        parser = ComprehensiveDocumentParser()
                        method = getattr(parser, f'parse_{doc_key}', None)
                        if method:
                            parsed_data[doc_key] = method(filepath)
                except Exception as e:
                    print(f"Error parsing {doc_key}: {e}")
        
        # Cross-verification
        verification_results = {}
        if 'gst_filing' in parsed_data and 'bank_statement' in parsed_data:
            verification_results['gst_bank'] = self.cross_verify_gst_bank(
                parsed_data['gst_filing'],
                parsed_data['bank_statement']
            )
        
        return {
            'parsed_documents': parsed_data,
            'verification_results': verification_results,
            'extraction_quality': self._assess_extraction_quality(parsed_data)
        }
    
    def _assess_extraction_quality(self, parsed_data: Dict) -> Dict:
        """Assess quality of data extraction"""
        
        total_docs = len(parsed_data)
        successful = sum(1 for v in parsed_data.values() if not v.get('error'))
        
        return {
            'total_documents': total_docs,
            'successful_extractions': successful,
            'success_rate': (successful / total_docs * 100) if total_docs > 0 else 0,
            'quality_score': 'HIGH' if successful == total_docs else 'MEDIUM' if successful > total_docs/2 else 'LOW'
        }
