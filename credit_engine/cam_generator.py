"""Generate Comprehensive Credit Appraisal Memo (CAM) - Indian context"""
from typing import Dict
from datetime import datetime
import pandas as pd

class CAMGenerator:
    def __init__(self):
        pass
    
    def generate_memo(self, applicant_data: Dict, financial_data: pd.DataFrame,
                     credit_history: pd.DataFrame, research_summary: str,
                     ml_decision: Dict, feature_importance: Dict,
                     validation_results: Dict = None, primary_insights: str = None) -> str:
        """Generate comprehensive CAM document with Five Cs framework"""
        
        memo = f"""
{'='*80}
COMPREHENSIVE CREDIT APPRAISAL MEMO (CAM)
{'='*80}

Date: {datetime.now().strftime('%d-%b-%Y')}
Applicant ID: {applicant_data.get('applicant_id', 'N/A')}
Company Name: {applicant_data.get('name', 'N/A')}
CIN: {applicant_data.get('cin', 'N/A')}
GSTIN: {applicant_data.get('gstin', 'N/A')}

{'='*80}
EXECUTIVE SUMMARY
{'='*80}

RECOMMENDATION: {ml_decision['decision']}
Proposed Credit Limit: ₹{ml_decision['credit_limit']:,.2f}
Risk Premium: {ml_decision['risk_premium_bps']} bps
Approval Confidence: {ml_decision['approval_probability']*100:.1f}%
Default Probability: {ml_decision['default_probability']*100:.2f}%

{'='*80}
THE FIVE Cs OF CREDIT ANALYSIS
{'='*80}

1. CHARACTER (Integrity & Willingness to Repay)
{'─'*80}

Promoter/Management Background:
  • Promoters: {applicant_data.get('promoters', 'N/A')}
  • Years in Business: {applicant_data.get('years_in_business', 'N/A')}
  • Industry Experience: {applicant_data.get('industry_experience', 'N/A')} years

Credit History:
"""
        if not credit_history.empty:
            memo += f"""  • CIBIL/Credit Score: {credit_history.get('credit_score', [0])[0] if 'credit_score' in credit_history else 'N/A'}
  • Existing Loans: {len(credit_history)} accounts
  • Delinquency History: {credit_history.get('delinquent', pd.Series([0])).sum()} instances
  • Credit Utilization: {(credit_history.get('balance', pd.Series([0])).sum() / max(credit_history.get('credit_limit', pd.Series([1])).sum(), 1))*100:.1f}%
"""
        
        memo += f"""
Regulatory/Legal Standing:
{research_summary}

2. CAPACITY (Ability to Repay)
{'─'*80}

Financial Performance:
"""
        if not financial_data.empty:
            latest = financial_data.iloc[0]
            memo += f"""  • Annual Revenue: ₹{latest.get('revenue', 0):,.2f}
  • EBITDA: ₹{latest.get('ebitda', 0):,.2f}
  • Net Profit: ₹{latest.get('net_profit', 0):,.2f}
  • PAT Margin: {(latest.get('net_profit', 0) / max(latest.get('revenue', 1), 1))*100:.2f}%
  • Debt Service Coverage Ratio: {latest.get('dscr', 0):.2f}x
  • Interest Coverage Ratio: {latest.get('interest_coverage', 0):.2f}x
"""
        
        memo += f"""
GST Analysis:
  • GST Turnover (Last 12M): ₹{applicant_data.get('gst_turnover', 0):,.2f}
  • GST Filing Compliance: {applicant_data.get('gst_compliance', 'N/A')}
"""
        
        if validation_results:
            gst_bank = validation_results.get('gst_bank_verification', {})
            if gst_bank:
                memo += f"""  • GST vs Bank Variance: {gst_bank.get('variance_pct', 0):.2f}%
  • Circular Trading Risk: {'⚠️ DETECTED' if gst_bank.get('is_suspicious') else '✓ Clear'}
"""
        
        memo += f"""
3. CAPITAL (Financial Strength & Net Worth)
{'─'*80}

"""
        if not financial_data.empty:
            latest = financial_data.iloc[0]
            memo += f"""Balance Sheet Strength:
  • Total Assets: ₹{latest.get('total_assets', 0):,.2f}
  • Net Worth: ₹{latest.get('net_worth', 0):,.2f}
  • Total Debt: ₹{latest.get('total_debt', 0):,.2f}
  • Debt-to-Equity Ratio: {latest.get('total_debt', 0) / max(latest.get('net_worth', 1), 1):.2f}x
  • Current Ratio: {latest.get('current_assets', 0) / max(latest.get('current_liabilities', 1), 1):.2f}x
  • Tangible Net Worth: ₹{latest.get('tangible_net_worth', 0):,.2f}
"""
        
        memo += f"""
4. COLLATERAL (Security)
{'─'*80}

Primary Security:
  • Type: {applicant_data.get('collateral_type', 'N/A')}
  • Value: ₹{applicant_data.get('collateral_value', 0):,.2f}
  • LTV Ratio: {(ml_decision['credit_limit'] / max(applicant_data.get('collateral_value', 1), 1))*100:.1f}%

Collateral Coverage: {(applicant_data.get('collateral_value', 0) / max(ml_decision['credit_limit'], 1))*100:.1f}%

5. CONDITIONS (Economic & Industry Environment)
{'─'*80}

Industry: {applicant_data.get('industry', 'N/A')}
Sector Outlook: {applicant_data.get('sector_outlook', 'Stable')}

Market Position:
  • Market Share: {applicant_data.get('market_share', 'N/A')}
  • Competitive Position: {applicant_data.get('competitive_position', 'N/A')}

{'='*80}
PRIMARY DUE DILIGENCE FINDINGS
{'='*80}

{primary_insights or 'No primary insights recorded'}

{'='*80}
DATA VALIDATION & FRAUD CHECKS
{'='*80}

"""
        if validation_results:
            memo += "GST-Bank Cross-Verification:\n"
            gst_bank = validation_results.get('gst_bank_verification', {})
            if gst_bank:
                memo += f"  • Status: {'⚠️ MISMATCH DETECTED' if gst_bank.get('is_suspicious') else '✓ Verified'}\n"
                memo += f"  • Variance: {gst_bank.get('variance_pct', 0):.2f}%\n"
            
            circular = validation_results.get('circular_trading', {})
            if circular and circular.get('detected'):
                memo += f"\n⚠️ Circular Trading Alert:\n"
                memo += f"  • {circular.get('count', 0)} suspicious patterns detected\n"
            
            gstr = validation_results.get('gstr_verification', {})
            if gstr:
                memo += f"\nGSTR-2A vs 3B Reconciliation:\n"
                memo += f"  • ITC Mismatch: {gstr.get('mismatch_pct', 0):.2f}%\n"
                memo += f"  • Risk Level: {gstr.get('risk_level', 'N/A')}\n"
        
        memo += f"""
{'='*80}
ML MODEL INSIGHTS & EXPLAINABILITY
{'='*80}

Model Confidence: {ml_decision['approval_probability']*100:.1f}%
Default Risk: {ml_decision['default_probability']*100:.2f}%

Top Risk Factors (Feature Importance):
"""
        for feature, importance in sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)[:8]:
            memo += f"  • {feature.replace('_', ' ').title()}: {importance:.3f}\n"
        
        memo += f"""
{'='*80}
FINAL RECOMMENDATION & DECISION RATIONALE
{'='*80}

Decision: {ml_decision['decision']}

"""
        if ml_decision['decision'] == 'APPROVE':
            memo += f"""Approved Credit Facility:
  • Sanctioned Limit: ₹{ml_decision['credit_limit']:,.2f}
  • Interest Rate: Base Rate + {ml_decision['risk_premium_bps']} bps
  • Tenure: {applicant_data.get('tenure_months', 'N/A')} months
  • Repayment: {applicant_data.get('repayment_type', 'N/A')}

Conditions Precedent:
  • Execution of loan documents
  • Creation of security as per sanction terms
  • Submission of post-dated cheques
  • Insurance coverage on assets

Covenants:
  • Maintain minimum DSCR of 1.25x
  • Submit quarterly financial statements
  • No dividend distribution without lender consent
  • Maintain debt-equity ratio below 2:1
"""
        else:
            memo += f"""Rejection Rationale:
"""
            if ml_decision['approval_probability'] < 0.5:
                memo += f"  • Low approval confidence ({ml_decision['approval_probability']*100:.1f}%)\n"
            if ml_decision['default_probability'] > 0.15:
                memo += f"  • High default risk ({ml_decision['default_probability']*100:.2f}%)\n"
            if validation_results and validation_results.get('gst_bank_verification', {}).get('is_suspicious'):
                memo += f"  • GST-Bank mismatch indicating potential revenue inflation\n"
            if research_summary and '⚠️' in research_summary:
                memo += f"  • Adverse findings in secondary research\n"
        
        memo += f"""
{'='*80}
PREPARED BY
{'='*80}

Credit Officer: [Name]
Date: {datetime.now().strftime('%d-%b-%Y')}

REVIEWED BY
Credit Manager: [Name]
Date: ___________

APPROVED BY
Credit Committee: [Names]
Date: ___________

{'='*80}
END OF MEMO
{'='*80}

Note: This CAM was generated using AI-powered credit decisioning engine.
All recommendations are subject to final approval by authorized credit committee.
"""
        return memo
