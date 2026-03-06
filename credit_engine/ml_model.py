"""ML-based credit decision model"""
import pandas as pd
import numpy as np
from sklearn.ensemble import GradientBoostingClassifier, RandomForestRegressor
from typing import Dict, Tuple
from .config import ML_MODEL_CONFIG

class CreditDecisionModel:
    def __init__(self):
        self.approval_model = None
        self.limit_model = None
        self.risk_model = None
    
    def train(self, X_train: pd.DataFrame, y_approval: pd.Series, 
              y_limit: pd.Series, y_default_rate: pd.Series):
        """Train the credit decision models"""
        self.approval_model = GradientBoostingClassifier(n_estimators=100, max_depth=5)
        self.approval_model.fit(X_train, y_approval)
        
        self.limit_model = RandomForestRegressor(n_estimators=100, max_depth=7)
        self.limit_model.fit(X_train[y_approval == 1], y_limit[y_approval == 1])
        
        self.risk_model = RandomForestRegressor(n_estimators=100, max_depth=7)
        self.risk_model.fit(X_train, y_default_rate)
    
    def predict(self, features: pd.DataFrame) -> Dict:
        """Make credit decision"""
        approval_prob = self.approval_model.predict_proba(features)[0][1]
        should_approve = approval_prob >= ML_MODEL_CONFIG['risk_threshold']
        
        credit_limit = 0
        risk_premium = 0
        
        if should_approve:
            credit_limit = max(0, self.limit_model.predict(features)[0])
            default_prob = self.risk_model.predict(features)[0]
            risk_premium = self._calculate_risk_premium(default_prob)
        
        return {
            "decision": "APPROVE" if should_approve else "REJECT",
            "approval_probability": approval_prob,
            "credit_limit": round(credit_limit, 2),
            "risk_premium_bps": round(risk_premium, 2),
            "default_probability": self.risk_model.predict(features)[0]
        }
    
    def _calculate_risk_premium(self, default_prob: float) -> float:
        """Calculate risk premium in basis points"""
        base_rate = 500  # 5% base rate
        risk_adjustment = default_prob * 1000  # Scale default prob to bps
        return base_rate + risk_adjustment
    
    def get_feature_importance(self) -> Dict:
        """Get feature importance for explainability"""
        if self.approval_model is None:
            return {}
        
        feature_names = self.approval_model.feature_names_in_
        importances = self.approval_model.feature_importances_
        
        return dict(zip(feature_names, importances))
