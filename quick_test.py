"""Quick test - minimal version"""
from credit_engine.ml_model import CreditDecisionModel
from credit_engine.cam_generator import CAMGenerator
import pandas as pd

# Mock data
applicant = {
    'applicant_id': 'TEST-001',
    'name': 'Test Company Ltd',
    'cin': 'U12345MH2015PTC123456',
    'gstin': '27AABCU9603R1ZM',
    'promoters': ['Mr. Test'],
    'annual_income': 50000000,
    'collateral_value': 80000000,
    'industry': 'Manufacturing'
}

financial = pd.DataFrame([{
    'revenue': 50000000,
    'net_profit': 4000000,
    'total_assets': 60000000,
    'net_worth': 25000000,
    'total_debt': 20000000,
    'current_assets': 15000000,
    'current_liabilities': 8000000,
    'ebitda': 8000000,
    'dscr': 1.8,
    'interest_coverage': 3.2,
    'tangible_net_worth': 23000000,
    'total_income': 50000000
}])

credit = pd.DataFrame([{'credit_score': 720, 'balance': 5000000, 'credit_limit': 10000000, 'delinquent': 0}])

# Create features
features = pd.DataFrame([{
    'age': 8,
    'income': 50000000,
    'employment_years': 8,
    'debt_to_income': 0.4,
    'current_ratio': 1.875,
    'profit_margin': 0.08,
    'credit_score': 720,
    'num_accounts': 1,
    'delinquency_count': 0,
    'credit_utilization': 0.5,
    'news_sentiment': 0.5,
    'legal_risk_score': 0
}])

# Train model
model = CreditDecisionModel()
X_train = pd.DataFrame([{col: 0.5 for col in features.columns} for _ in range(100)])
model.train(X_train, pd.Series([1]*60 + [0]*40), pd.Series([5000000]*100), pd.Series([0.05]*100))

# Predict
decision = model.predict(features)

# Generate CAM
cam_gen = CAMGenerator()
cam = cam_gen.generate_memo(applicant, financial, credit, "No adverse findings", decision, model.get_feature_importance())

print(f"Decision: {decision['decision']}")
print(f"Credit Limit: ₹{decision['credit_limit']:,.2f}")
print(f"\nFull CAM saved to quick_test_output.txt")

with open('quick_test_output.txt', 'w', encoding='utf-8') as f:
    f.write(cam)
