"""Test the credit engine with mock data"""
import pandas as pd
from credit_engine.feature_engineering import FeatureEngineering
from credit_engine.ml_model import CreditDecisionModel
from credit_engine.cam_generator import CAMGenerator
from credit_engine.data_validator import DataValidator
from credit_engine.secondary_research import SecondaryResearch
from credit_engine.primary_insights import PrimaryInsights

def test_basic_flow():
    """Test basic credit decisioning flow with mock data"""
    
    # Mock applicant data
    applicant_data = {
        'applicant_id': 'APP-12345',
        'name': 'ABC Manufacturing Pvt Ltd',
        'cin': 'U12345MH2015PTC123456',
        'gstin': '27AABCU9603R1ZM',
        'promoters': ['Mr. Rajesh Kumar', 'Mrs. Priya Sharma'],
        'years_in_business': 8,
        'industry': 'Textile Manufacturing',
        'age': 8,
        'annual_income': 50000000,
        'employment_years': 8,
        'gst_turnover': 48000000,
        'gst_compliance': 'Compliant',
        'collateral_type': 'Factory Building',
        'collateral_value': 80000000,
        'sector_outlook': 'Stable',
        'market_share': '5%',
        'competitive_position': 'Mid-tier player',
        'tenure_months': 60,
        'repayment_type': 'EMI'
    }
    
    # Mock financial data
    financial_data = pd.DataFrame([{
        'revenue': 50000000,
        'ebitda': 8000000,
        'net_profit': 4000000,
        'total_assets': 60000000,
        'total_liabilities': 35000000,
        'net_worth': 25000000,
        'total_debt': 20000000,
        'current_assets': 15000000,
        'current_liabilities': 8000000,
        'tangible_net_worth': 23000000,
        'dscr': 1.8,
        'interest_coverage': 3.2,
        'total_income': 50000000
    }])
    
    # Mock credit history
    credit_history = pd.DataFrame([
        {'credit_score': 720, 'balance': 5000000, 'credit_limit': 10000000, 'delinquent': 0},
        {'credit_score': 720, 'balance': 3000000, 'credit_limit': 8000000, 'delinquent': 0}
    ])
    
    # Mock research data
    research_data = {
        'news': [],
        'promoter_news': [],
        'mca_filings': {'compliance_score': 0.85},
        'legal_cases': [],
        'regulatory_actions': [],
        'sector_trends': {},
        'credit_ratings': [{'rating': 'BBB', 'agency': 'CRISIL'}]
    }
    
    print("="*80)
    print("TESTING CREDIT DECISIONING ENGINE")
    print("="*80)
    
    # Test Feature Engineering
    print("\n1. Feature Engineering...")
    feature_eng = FeatureEngineering()
    features = feature_eng.engineer_features(
        applicant_data, financial_data, credit_history, research_data
    )
    print(f"✓ Generated {len(features.columns)} features")
    print(f"  Sample features: {list(features.columns[:5])}")
    
    # Test ML Model (create dummy model)
    print("\n2. ML Model Prediction...")
    ml_model = CreditDecisionModel()
    
    # Create dummy training data
    X_train = pd.DataFrame([
        {col: 0.5 for col in features.columns} for _ in range(100)
    ])
    y_approval = pd.Series([1] * 60 + [0] * 40)
    y_limit = pd.Series([5000000] * 60 + [0] * 40)
    y_default = pd.Series([0.05] * 60 + [0.20] * 40)
    
    ml_model.train(X_train, y_approval, y_limit, y_default)
    decision = ml_model.predict(features)
    
    print(f"✓ Decision: {decision['decision']}")
    print(f"  Credit Limit: ₹{decision['credit_limit']:,.2f}")
    print(f"  Risk Premium: {decision['risk_premium_bps']} bps")
    print(f"  Approval Probability: {decision['approval_probability']*100:.1f}%")
    
    # Test Secondary Research
    print("\n3. Secondary Research...")
    research = SecondaryResearch()
    research_summary = research.synthesize_findings(research_data)
    print(f"✓ Research Summary: {research_summary}")
    
    # Test Primary Insights
    print("\n4. Primary Insights...")
    primary = PrimaryInsights()
    primary.add_site_visit_notes({
        'capacity_utilization_pct': 75,
        'machinery_condition': 'Good',
        'observations': 'Well-maintained facility'
    })
    primary.add_management_interview({
        'quality_rating': 4,
        'red_flags': [],
        'notes': 'Strong management team'
    })
    qual_score = primary.calculate_qualitative_score()
    print(f"✓ Qualitative Adjustment: {qual_score['total_adjustment']} points")
    print(f"  Insights Recorded: {qual_score['insights_count']}")
    
    # Test CAM Generation
    print("\n5. CAM Generation...")
    cam_gen = CAMGenerator()
    feature_importance = ml_model.get_feature_importance()
    cam_document = cam_gen.generate_memo(
        applicant_data, financial_data, credit_history,
        research_summary, decision, feature_importance,
        None, primary.get_summary()
    )
    print(f"✓ CAM Generated ({len(cam_document)} characters)")
    
    # Save CAM
    with open('test_CAM_output.txt', 'w', encoding='utf-8') as f:
        f.write(cam_document)
    print(f"✓ Saved to test_CAM_output.txt")
    
    print("\n" + "="*80)
    print("CAM PREVIEW (First 1000 chars)")
    print("="*80)
    print(cam_document[:1000])
    print("\n[... see test_CAM_output.txt for full CAM ...]")
    
    return decision, cam_document

def test_fraud_detection():
    """Test fraud detection features"""
    print("\n" + "="*80)
    print("TESTING FRAUD DETECTION")
    print("="*80)
    
    validator = DataValidator()
    
    # Test GST-Bank cross-verification
    print("\n1. GST-Bank Cross-Verification...")
    gst_data = {'turnover': 50000000}
    bank_df = pd.DataFrame([
        {'type': 'credit', 'amount': 40000000, 'date': '2026-01-15'},
        {'type': 'debit', 'amount': 35000000, 'date': '2026-01-20'}
    ])
    
    result = validator.cross_verify_gst_bank(gst_data, bank_df)
    print(f"✓ GST Turnover: ₹{result['gst_turnover']:,.0f}")
    print(f"  Bank Credits: ₹{result['bank_credits']:,.0f}")
    print(f"  Variance: {result['variance_pct']:.2f}%")
    print(f"  Suspicious: {result['is_suspicious']}")
    
    # Test circular trading detection
    print("\n2. Circular Trading Detection...")
    suspicious_bank_df = pd.DataFrame([
        {'type': 'credit', 'amount': 1000000, 'date': '2026-01-15', 'counterparty': 'ABC'},
        {'type': 'debit', 'amount': 1000000, 'date': '2026-01-15', 'counterparty': 'ABC'},
        {'type': 'credit', 'amount': 2000000, 'date': '2026-01-16', 'counterparty': 'XYZ'},
        {'type': 'debit', 'amount': 2000000, 'date': '2026-01-16', 'counterparty': 'XYZ'}
    ])
    
    circular = validator.detect_circular_trading(suspicious_bank_df)
    print(f"✓ Circular Trading Detected: {circular['detected']}")
    if circular['detected']:
        print(f"  Suspicious Patterns: {circular['count']}")
    
    # Test GSTR verification
    print("\n3. GSTR-2A vs 3B Verification...")
    gstr2a = {'input_tax_credit': 500000}
    gstr3b = {'input_tax_credit': 480000}
    
    gstr_result = validator.verify_gstr_2a_3b(gstr2a, gstr3b)
    print(f"✓ ITC 2A: ₹{gstr_result['itc_2a']:,.0f}")
    print(f"  ITC 3B: ₹{gstr_result['itc_3b']:,.0f}")
    print(f"  Mismatch: {gstr_result['mismatch_pct']:.2f}%")
    print(f"  Risk Level: {gstr_result['risk_level']}")

if __name__ == "__main__":
    # Run basic flow test
    decision, cam = test_basic_flow()
    
    # Run fraud detection test
    test_fraud_detection()
    
    print("\n" + "="*80)
    print("✓ ALL TESTS COMPLETED SUCCESSFULLY")
    print("="*80)
    print("\nNext steps:")
    print("1. Check test_CAM_output.txt for full CAM document")
    print("2. Configure Databricks in credit_engine/config.py")
    print("3. Add real PDF documents for parsing")
    print("4. Integrate news/MCA/e-Courts APIs")
