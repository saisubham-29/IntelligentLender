"""Feature engineering for ML model"""
import pandas as pd
import numpy as np
from typing import Dict

class FeatureEngineering:
    def __init__(self):
        pass
    
    def engineer_features(self, applicant_data: Dict, financial_data: pd.DataFrame, 
                         credit_history: pd.DataFrame, research_data: Dict) -> pd.DataFrame:
        """Transform raw data into ML features"""
        features = {}
        
        # Basic applicant features
        features['age'] = applicant_data.get('age', 0)
        features['income'] = applicant_data.get('annual_income', 0)
        features['employment_years'] = applicant_data.get('employment_years', 0)
        
        # Financial ratios
        if not financial_data.empty:
            latest = financial_data.iloc[0]
            features['debt_to_income'] = latest.get('total_debt', 0) / max(latest.get('total_income', 1), 1)
            features['current_ratio'] = latest.get('current_assets', 0) / max(latest.get('current_liabilities', 1), 1)
            features['profit_margin'] = latest.get('net_profit', 0) / max(latest.get('revenue', 1), 1)
        
        # Credit history features
        if not credit_history.empty:
            features['credit_score'] = credit_history['credit_score'].iloc[0]
            features['num_accounts'] = len(credit_history)
            features['delinquency_count'] = credit_history['delinquent'].sum()
            features['credit_utilization'] = credit_history['balance'].sum() / max(credit_history['credit_limit'].sum(), 1)
        
        # Research-based features
        features['news_sentiment'] = self._calculate_sentiment(research_data.get('news', []))
        features['legal_risk_score'] = len(research_data.get('legal_issues', []))
        
        return pd.DataFrame([features])
    
    def _calculate_sentiment(self, news_items: list) -> float:
        """Calculate sentiment score from news"""
        if not news_items:
            return 0.5
        # Placeholder - integrate with sentiment analysis
        return 0.5
