"""
SECTION 3: RECOMMENDATION ENGINE
CAM Generator and Explainable Decision Logic
"""
from typing import Dict, List
import pandas as pd
from datetime import datetime

class RecommendationEngine:
    """
    Produces professional CAM and transparent, explainable credit decisions
    """
    
    def __init__(self):
        self.decision_factors = []
    
    # ============================================================
    # DECISION LOGIC (Transparent & Explainable)
    # ============================================================
    
    def make_credit_decision(self, applicant: Dict, financial_data: pd.DataFrame,
                            research_results: Dict, verification_results: Dict,
                            primary_insights: Dict) -> Dict:
        """
        Make explainable credit decision based on Five Cs of Credit
        Returns: Decision with complete explanation of logic
        """
        
        self.decision_factors = []
        
        # Analyze Five Cs of Credit
        character_score = self._assess_character(applicant, research_results)
        capacity_score = self._assess_capacity(financial_data, primary_insights)
        capital_score = self._assess_capital(financial_data)
        collateral_score = self._assess_collateral(applicant, financial_data)
        conditions_score = self._assess_conditions(research_results)
        
        # Calculate overall score
        weights = {'character': 0.25, 'capacity': 0.30, 'capital': 0.20, 
                   'collateral': 0.15, 'conditions': 0.10}
        
        overall_score = (
            character_score * weights['character'] +
            capacity_score * weights['capacity'] +
            capital_score * weights['capital'] +
            collateral_score * weights['collateral'] +
            conditions_score * weights['conditions']
        )
        
        # Make decision
        decision = self._determine_decision(overall_score, self.decision_factors)
        
        # Calculate loan amount and interest rate
        if decision['decision'] == 'APPROVE':
            loan_details = self._calculate_loan_terms(
                financial_data, overall_score, applicant.get('loan_amount_requested', 0)
            )
            decision.update(loan_details)
        
        # Add Five Cs breakdown
        decision['five_cs_analysis'] = {
            'character': {'score': character_score, 'weight': weights['character']},
            'capacity': {'score': capacity_score, 'weight': weights['capacity']},
            'capital': {'score': capital_score, 'weight': weights['capital']},
            'collateral': {'score': collateral_score, 'weight': weights['collateral']},
            'conditions': {'score': conditions_score, 'weight': weights['conditions']},
            'overall_score': overall_score
        }
        
        # Add complete explanation
        decision['explanation'] = self._generate_decision_explanation(
            decision, self.decision_factors, verification_results
        )
        
        return decision
    
    def _assess_character(self, applicant: Dict, research: Dict) -> float:
        """
        Assess Character (0-100)
        Factors: Promoter background, litigation, regulatory actions, credit history
        """
        score = 70  # Start neutral
        
        # Promoter research
        promoter_risk = research.get('promoter_research', {}).get('risk_level', 'UNKNOWN')
        if promoter_risk == 'HIGH':
            score -= 30
            self.decision_factors.append("❌ HIGH promoter risk found in background check")
        elif promoter_risk == 'MEDIUM':
            score -= 15
            self.decision_factors.append("⚠️ MEDIUM promoter risk identified")
        else:
            self.decision_factors.append("✓ Clean promoter background")
        
        # Litigation
        litigation = research.get('litigation_research', {})
        cases = litigation.get('cases_found', 0)
        if cases > 3:
            score -= 20
            self.decision_factors.append(f"❌ {cases} litigation cases found - high legal risk")
        elif cases > 0:
            score -= 10
            self.decision_factors.append(f"⚠️ {cases} litigation case(s) pending")
        
        # Regulatory actions
        regulatory = research.get('regulatory_research', {})
        actions = regulatory.get('actions_found', 0)
        if actions > 0:
            score -= 15
            self.decision_factors.append(f"❌ {actions} regulatory action(s) found")
        
        # Wilful defaulter check
        if applicant.get('wilful_defaulter') == 'Yes':
            score = 0
            self.decision_factors.append("❌ CRITICAL: Listed as wilful defaulter")
        
        return max(score, 0)
    
    def _assess_capacity(self, financial: pd.DataFrame, insights: Dict) -> float:
        """
        Assess Capacity (0-100)
        Factors: Cash flow, DSCR, profitability, capacity utilization
        """
        score = 70
        
        fin = financial.iloc[0] if len(financial) > 0 else {}
        
        # DSCR (Debt Service Coverage Ratio)
        dscr = fin.get('dscr', 0)
        if dscr >= 1.5:
            score += 15
            self.decision_factors.append(f"✓ Strong DSCR: {dscr:.2f} (>1.5)")
        elif dscr >= 1.25:
            score += 5
            self.decision_factors.append(f"✓ Adequate DSCR: {dscr:.2f}")
        elif dscr < 1.0:
            score -= 20
            self.decision_factors.append(f"❌ Poor DSCR: {dscr:.2f} (<1.0) - insufficient cash flow")
        
        # Profitability
        profit_margin = fin.get('net_profit', 0) / (fin.get('revenue', 1) + 1)
        if profit_margin > 0.10:
            score += 10
            self.decision_factors.append(f"✓ Strong profitability: {profit_margin*100:.1f}%")
        elif profit_margin < 0:
            score -= 15
            self.decision_factors.append(f"❌ Operating at loss: {profit_margin*100:.1f}%")
        
        # Capacity utilization (from primary insights)
        capacity = insights.get('site_visit', {}).get('capacity_utilization_pct', 100)
        if capacity < 50:
            score -= 15
            self.decision_factors.append(f"❌ Low capacity utilization: {capacity}% - demand concerns")
        elif capacity > 80:
            score += 10
            self.decision_factors.append(f"✓ High capacity utilization: {capacity}%")
        
        return max(score, 0)
    
    def _assess_capital(self, financial: pd.DataFrame) -> float:
        """
        Assess Capital (0-100)
        Factors: Net worth, leverage, equity base
        """
        score = 70
        
        fin = financial.iloc[0] if len(financial) > 0 else {}
        
        # Debt to Equity
        debt = fin.get('total_debt', 0)
        equity = fin.get('net_worth', 1)
        debt_to_equity = debt / (equity + 1)
        
        if debt_to_equity < 1.0:
            score += 15
            self.decision_factors.append(f"✓ Conservative leverage: D/E = {debt_to_equity:.2f}")
        elif debt_to_equity > 3.0:
            score -= 20
            self.decision_factors.append(f"❌ High leverage: D/E = {debt_to_equity:.2f} (>3.0)")
        
        # Net worth adequacy
        if equity > 10000000:  # 1 Cr
            score += 10
            self.decision_factors.append(f"✓ Strong equity base: ₹{equity:,.0f}")
        elif equity < 1000000:  # 10 L
            score -= 15
            self.decision_factors.append(f"❌ Weak equity base: ₹{equity:,.0f}")
        
        return max(score, 0)
    
    def _assess_collateral(self, applicant: Dict, financial: pd.DataFrame) -> float:
        """
        Assess Collateral (0-100)
        Factors: Security coverage, asset quality
        """
        score = 70
        
        collateral = applicant.get('collateral_value', 0)
        loan_requested = applicant.get('loan_amount_requested', 0)
        
        if collateral > 0 and loan_requested > 0:
            ltv = (loan_requested / collateral) * 100
            if ltv <= 60:
                score += 20
                self.decision_factors.append(f"✓ Strong security: LTV = {ltv:.1f}%")
            elif ltv > 80:
                score -= 15
                self.decision_factors.append(f"⚠️ High LTV: {ltv:.1f}% (>80%)")
        else:
            score -= 10
            self.decision_factors.append("⚠️ No collateral offered")
        
        return max(score, 0)
    
    def _assess_conditions(self, research: Dict) -> float:
        """
        Assess Conditions (0-100)
        Factors: Sector outlook, economic conditions, regulatory environment
        """
        score = 70
        
        # Sector conditions
        sector = research.get('sector_research', {})
        headwinds = sector.get('headwinds', [])
        tailwinds = sector.get('tailwinds', [])
        
        if len(headwinds) > len(tailwinds):
            score -= 15
            self.decision_factors.append(f"⚠️ Sector headwinds: {len(headwinds)} challenges identified")
        elif len(tailwinds) > len(headwinds):
            score += 10
            self.decision_factors.append(f"✓ Sector tailwinds: {len(tailwinds)} opportunities")
        
        # News sentiment
        sentiment = research.get('news_sentiment', {}).get('sentiment', 'NEUTRAL')
        if sentiment == 'NEGATIVE':
            score -= 10
            self.decision_factors.append("⚠️ Negative news sentiment")
        elif sentiment == 'POSITIVE':
            score += 5
            self.decision_factors.append("✓ Positive news sentiment")
        
        return max(score, 0)
    
    def _determine_decision(self, overall_score: float, factors: List[str]) -> Dict:
        """Determine final decision based on score and factors"""
        
        # Check for critical failures
        critical_failures = [f for f in factors if '❌ CRITICAL' in f]
        if critical_failures:
            return {
                'decision': 'REJECT',
                'reason': 'Critical failure criteria met',
                'critical_issues': critical_failures
            }
        
        # Score-based decision
        if overall_score >= 70:
            return {'decision': 'APPROVE', 'confidence': 'HIGH'}
        elif overall_score >= 60:
            return {'decision': 'APPROVE', 'confidence': 'MEDIUM'}
        elif overall_score >= 50:
            return {'decision': 'CONDITIONAL_APPROVE', 'confidence': 'LOW'}
        else:
            return {'decision': 'REJECT', 'reason': 'Overall score below threshold'}
    
    def _calculate_loan_terms(self, financial: pd.DataFrame, score: float, 
                             requested_amount: float) -> Dict:
        """Calculate loan amount and interest rate"""
        
        fin = financial.iloc[0] if len(financial) > 0 else {}
        revenue = fin.get('revenue', 0)
        
        # Loan amount: 20-40% of revenue based on score
        multiplier = 0.20 + (score / 100) * 0.20  # 20-40%
        recommended_amount = revenue * multiplier
        
        # Cap at requested amount
        approved_amount = min(recommended_amount, requested_amount)
        
        # Interest rate: Base rate + risk premium
        base_rate = 10.0  # 10%
        risk_premium = (100 - score) / 10  # 0-10% based on score
        interest_rate = base_rate + risk_premium
        
        return {
            'approved_amount': round(approved_amount, 2),
            'recommended_amount': round(recommended_amount, 2),
            'interest_rate': round(interest_rate, 2),
            'risk_premium_bps': round(risk_premium * 100, 0),
            'tenure_months': 60  # Default 5 years
        }
    
    def _generate_decision_explanation(self, decision: Dict, factors: List[str],
                                      verification: Dict) -> str:
        """Generate complete explanation of decision logic"""
        
        explanation = []
        
        # Decision summary
        if decision['decision'] == 'APPROVE':
            explanation.append(f"✅ APPROVED for ₹{decision.get('approved_amount', 0):,.0f} at {decision.get('interest_rate', 0):.2f}% interest")
            explanation.append(f"Confidence: {decision.get('confidence', 'MEDIUM')}")
        elif decision['decision'] == 'REJECT':
            explanation.append(f"❌ REJECTED - {decision.get('reason', 'Score below threshold')}")
        
        explanation.append("\n📊 DECISION FACTORS:")
        
        # Add all factors
        for factor in factors:
            explanation.append(f"  {factor}")
        
        # Add verification results
        if verification:
            explanation.append("\n🔍 VERIFICATION RESULTS:")
            gst_bank = verification.get('gst_bank', {})
            if gst_bank:
                explanation.append(f"  GST-Bank Variance: {gst_bank.get('variance_pct', 0):.1f}% - {gst_bank.get('risk_level', 'UNKNOWN')}")
                if gst_bank.get('circular_trading', {}).get('detected'):
                    explanation.append(f"  ⚠️ Circular trading patterns detected")
        
        # Add Five Cs summary
        five_cs = decision.get('five_cs_analysis', {})
        if five_cs:
            explanation.append("\n📋 FIVE Cs OF CREDIT:")
            explanation.append(f"  Character: {five_cs.get('character', {}).get('score', 0):.0f}/100")
            explanation.append(f"  Capacity: {five_cs.get('capacity', {}).get('score', 0):.0f}/100")
            explanation.append(f"  Capital: {five_cs.get('capital', {}).get('score', 0):.0f}/100")
            explanation.append(f"  Collateral: {five_cs.get('collateral', {}).get('score', 0):.0f}/100")
            explanation.append(f"  Conditions: {five_cs.get('conditions', {}).get('score', 0):.0f}/100")
            explanation.append(f"  Overall Score: {five_cs.get('overall_score', 0):.0f}/100")
        
        return "\n".join(explanation)
    
    # ============================================================
    # CAM GENERATOR
    # ============================================================
    
    def generate_cam(self, applicant: Dict, financial: pd.DataFrame, 
                    research: Dict, decision: Dict, verification: Dict,
                    primary_insights: Dict) -> str:
        """
        Generate professional Credit Appraisal Memo (CAM)
        Structured format covering Five Cs of Credit
        """
        
        cam = []
        
        # Header
        cam.append("="*80)
        cam.append("CREDIT APPRAISAL MEMO (CAM)")
        cam.append("="*80)
        cam.append(f"\nDate: {datetime.now().strftime('%d %B %Y')}")
        cam.append(f"Application ID: {applicant.get('applicant_id', 'N/A')}")
        cam.append(f"Company Name: {applicant.get('name', 'N/A')}")
        cam.append(f"CIN: {applicant.get('cin', 'N/A')}")
        cam.append(f"\nLoan Amount Requested: ₹{applicant.get('loan_amount_requested', 0):,.0f}")
        cam.append(f"Purpose: {applicant.get('loan_purpose', 'N/A')}")
        cam.append(f"Tenure: {applicant.get('tenure_months', 60)} months")
        
        # Executive Summary
        cam.append("\n" + "="*80)
        cam.append("EXECUTIVE SUMMARY")
        cam.append("="*80)
        cam.append(f"\nDecision: {decision['decision']}")
        if decision['decision'] == 'APPROVE':
            cam.append(f"Approved Amount: ₹{decision.get('approved_amount', 0):,.0f}")
            cam.append(f"Interest Rate: {decision.get('interest_rate', 0):.2f}%")
            cam.append(f"Risk Premium: {decision.get('risk_premium_bps', 0):.0f} bps")
        cam.append(f"\n{decision.get('explanation', '')}")
        
        # Five Cs Analysis
        cam.append("\n" + "="*80)
        cam.append("FIVE Cs OF CREDIT ANALYSIS")
        cam.append("="*80)
        
        five_cs = decision.get('five_cs_analysis', {})
        
        cam.append("\n1. CHARACTER")
        cam.append(f"   Score: {five_cs.get('character', {}).get('score', 0):.0f}/100")
        cam.append(f"   Promoter Background: {research.get('promoter_research', {}).get('risk_level', 'N/A')}")
        cam.append(f"   Litigation Cases: {research.get('litigation_research', {}).get('cases_found', 0)}")
        cam.append(f"   Regulatory Actions: {research.get('regulatory_research', {}).get('actions_found', 0)}")
        
        cam.append("\n2. CAPACITY")
        cam.append(f"   Score: {five_cs.get('capacity', {}).get('score', 0):.0f}/100")
        fin = financial.iloc[0] if len(financial) > 0 else {}
        cam.append(f"   Revenue: ₹{fin.get('revenue', 0):,.0f}")
        cam.append(f"   EBITDA: ₹{fin.get('ebitda', 0):,.0f}")
        cam.append(f"   DSCR: {fin.get('dscr', 0):.2f}")
        if primary_insights.get('site_visit'):
            cam.append(f"   Capacity Utilization: {primary_insights['site_visit'].get('capacity_utilization_pct', 'N/A')}%")
        
        cam.append("\n3. CAPITAL")
        cam.append(f"   Score: {five_cs.get('capital', {}).get('score', 0):.0f}/100")
        cam.append(f"   Net Worth: ₹{fin.get('net_worth', 0):,.0f}")
        cam.append(f"   Total Debt: ₹{fin.get('total_debt', 0):,.0f}")
        debt_to_equity = fin.get('total_debt', 0) / (fin.get('net_worth', 1) + 1)
        cam.append(f"   Debt/Equity: {debt_to_equity:.2f}")
        
        cam.append("\n4. COLLATERAL")
        cam.append(f"   Score: {five_cs.get('collateral', {}).get('score', 0):.0f}/100")
        cam.append(f"   Collateral Value: ₹{applicant.get('collateral_value', 0):,.0f}")
        if applicant.get('collateral_value', 0) > 0:
            ltv = (applicant.get('loan_amount_requested', 0) / applicant.get('collateral_value', 1)) * 100
            cam.append(f"   LTV Ratio: {ltv:.1f}%")
        
        cam.append("\n5. CONDITIONS")
        cam.append(f"   Score: {five_cs.get('conditions', {}).get('score', 0):.0f}/100")
        cam.append(f"   Sector: {applicant.get('industry', 'N/A')}")
        cam.append(f"   News Sentiment: {research.get('news_sentiment', {}).get('sentiment', 'N/A')}")
        sector = research.get('sector_research', {})
        cam.append(f"   Sector Headwinds: {len(sector.get('headwinds', []))}")
        cam.append(f"   Sector Tailwinds: {len(sector.get('tailwinds', []))}")
        
        # Verification Results
        if verification:
            cam.append("\n" + "="*80)
            cam.append("DATA VERIFICATION")
            cam.append("="*80)
            gst_bank = verification.get('gst_bank', {})
            if gst_bank:
                cam.append(f"\nGST-Bank Cross-Verification:")
                cam.append(f"  GST Turnover: ₹{gst_bank.get('gst_turnover', 0):,.0f}")
                cam.append(f"  Bank Credits: ₹{gst_bank.get('bank_credits', 0):,.0f}")
                cam.append(f"  Variance: {gst_bank.get('variance_pct', 0):.1f}%")
                cam.append(f"  Risk Level: {gst_bank.get('risk_level', 'N/A')}")
                if gst_bank.get('circular_trading', {}).get('detected'):
                    cam.append(f"  ⚠️ Circular Trading: {', '.join(gst_bank['circular_trading']['patterns'])}")
        
        # Research Findings
        cam.append("\n" + "="*80)
        cam.append("SECONDARY RESEARCH FINDINGS")
        cam.append("="*80)
        cam.append(f"\nResearch Risk Score: {research.get('risk_score', 0)}/100")
        cam.append(f"Synthesis: {research.get('synthesis', 'N/A')}")
        
        key_findings = research.get('key_findings', [])
        if key_findings:
            cam.append("\nKey Findings:")
            for finding in key_findings:
                cam.append(f"  • {finding}")
        
        # Primary Insights
        if primary_insights:
            cam.append("\n" + "="*80)
            cam.append("PRIMARY INSIGHTS (Credit Officer Observations)")
            cam.append("="*80)
            
            if primary_insights.get('site_visit'):
                cam.append("\nSite Visit:")
                sv = primary_insights['site_visit']
                cam.append(f"  Capacity Utilization: {sv.get('capacity_utilization_pct', 'N/A')}%")
                cam.append(f"  Machinery Condition: {sv.get('machinery_condition', 'N/A')}")
                cam.append(f"  Observations: {sv.get('observations', 'N/A')}")
            
            if primary_insights.get('management_interview'):
                cam.append("\nManagement Interview:")
                mi = primary_insights['management_interview']
                cam.append(f"  Quality Rating: {mi.get('quality_rating', 'N/A')}/10")
                cam.append(f"  Notes: {mi.get('notes', 'N/A')}")
                if mi.get('red_flags'):
                    cam.append(f"  Red Flags: {', '.join(mi['red_flags'])}")
        
        # Recommendation
        cam.append("\n" + "="*80)
        cam.append("RECOMMENDATION")
        cam.append("="*80)
        cam.append(f"\n{decision.get('explanation', '')}")
        
        # Footer
        cam.append("\n" + "="*80)
        cam.append("END OF CREDIT APPRAISAL MEMO")
        cam.append("="*80)
        
        return "\n".join(cam)
