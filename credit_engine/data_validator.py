"""Cross-verification and fraud detection"""
import pandas as pd
from typing import Dict, List

class DataValidator:
    def __init__(self):
        self.tolerance = 0.05  # 5% tolerance
    
    def cross_verify_gst_bank(self, gst_data: Dict, bank_df: pd.DataFrame) -> Dict:
        """Cross-verify GST returns against bank statements"""
        gst_turnover = gst_data.get('turnover', 0)
        
        # Calculate bank credits (revenue proxy)
        bank_credits = bank_df[bank_df['type'] == 'credit']['amount'].sum() if not bank_df.empty else 0
        
        variance = abs(gst_turnover - bank_credits) / max(gst_turnover, 1)
        
        return {
            'gst_turnover': gst_turnover,
            'bank_credits': bank_credits,
            'variance_pct': variance * 100,
            'is_suspicious': variance > self.tolerance,
            'risk_flag': 'CIRCULAR_TRADING' if variance > 0.20 else None
        }
    
    def detect_circular_trading(self, bank_df: pd.DataFrame) -> Dict:
        """Detect circular trading patterns"""
        if bank_df.empty:
            return {'detected': False}
        
        # Look for same-day round-trip transactions
        suspicious_patterns = []
        
        # Group by date and look for matching debit-credit pairs
        for date in bank_df['date'].unique():
            day_txns = bank_df[bank_df['date'] == date]
            credits = day_txns[day_txns['type'] == 'credit']
            debits = day_txns[day_txns['type'] == 'debit']
            
            for _, credit in credits.iterrows():
                matching_debits = debits[abs(debits['amount'] - credit['amount']) < 1000]
                if len(matching_debits) > 0:
                    suspicious_patterns.append({
                        'date': date,
                        'amount': credit['amount'],
                        'pattern': 'same_day_reversal'
                    })
        
        return {
            'detected': len(suspicious_patterns) > 0,
            'count': len(suspicious_patterns),
            'patterns': suspicious_patterns[:5]  # Top 5
        }
    
    def verify_gstr_2a_3b(self, gstr2a: Dict, gstr3b: Dict) -> Dict:
        """Verify GSTR-2A vs GSTR-3B mismatch"""
        itc_2a = gstr2a.get('input_tax_credit', 0)
        itc_3b = gstr3b.get('input_tax_credit', 0)
        
        mismatch = abs(itc_2a - itc_3b)
        mismatch_pct = (mismatch / max(itc_2a, 1)) * 100
        
        return {
            'itc_2a': itc_2a,
            'itc_3b': itc_3b,
            'mismatch': mismatch,
            'mismatch_pct': mismatch_pct,
            'is_compliant': mismatch_pct < 5,
            'risk_level': 'HIGH' if mismatch_pct > 15 else 'MEDIUM' if mismatch_pct > 5 else 'LOW'
        }
    
    def check_promoter_transactions(self, bank_df: pd.DataFrame, promoter_accounts: List[str]) -> Dict:
        """Check for suspicious promoter transactions"""
        if bank_df.empty:
            return {'suspicious': False}
        
        promoter_txns = bank_df[bank_df['counterparty'].isin(promoter_accounts)]
        
        total_promoter_flow = promoter_txns['amount'].sum()
        total_flow = bank_df['amount'].sum()
        
        promoter_pct = (total_promoter_flow / max(total_flow, 1)) * 100
        
        return {
            'promoter_transaction_pct': promoter_pct,
            'suspicious': promoter_pct > 20,
            'risk_flag': 'HIGH_PROMOTER_EXPOSURE' if promoter_pct > 20 else None
        }
