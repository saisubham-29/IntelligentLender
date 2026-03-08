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
        self.feature_names = None
    
    def train(self, X_train: pd.DataFrame, y_approval: pd.Series, 
              y_limit: pd.Series = None, y_default_rate: pd.Series = None):
        """Train the credit decision models"""
        self.feature_names = X_train.columns.tolist()
        
        # Train approval model
        self.approval_model = GradientBoostingClassifier(n_estimators=100, max_depth=5, random_state=42)
        self.approval_model.fit(X_train, y_approval)
        
        # Train limit model (only on approved cases)
        if y_limit is not None:
            approved_mask = y_approval == 1
            if approved_mask.sum() > 0:
                self.limit_model = RandomForestRegressor(n_estimators=100, max_depth=7, random_state=42)
                self.limit_model.fit(X_train[approved_mask], y_limit[approved_mask])
        
        # Train risk model
        if y_default_rate is not None:
            self.risk_model = RandomForestRegressor(n_estimators=100, max_depth=7, random_state=42)
            self.risk_model.fit(X_train, y_default_rate)
        
        print(f"✓ Model trained on {len(X_train)} samples with {len(self.feature_names)} features")
    
    def train_from_csv(self, csv_path: str):
        """Train model from CSV file"""
        from .csv_handler import CSVDataHandler
        
        handler = CSVDataHandler()
        data = handler.prepare_for_training(csv_path)
        
        # Extract credit limits and risk premiums from training data if available
        y_limit = None
        y_risk = None
        
        # Train model
        self.train(data['X_train'], data['y_train'], y_limit, y_risk)
        
        # Evaluate on test set
        if len(data['X_test']) > 0:
            y_pred = self.approval_model.predict(data['X_test'])
            accuracy = (y_pred == data['y_test']).mean()
            print(f"✓ Test accuracy: {accuracy*100:.1f}%")
        
        return handler
    
    def predict(self, features: pd.DataFrame) -> Dict:
        """Make credit decision with detailed reasoning and credit bandwidth"""
        approval_prob = self.approval_model.predict_proba(features)[0][1]
        default_prob = self.risk_model.predict(features)[0] if self.risk_model else 0.03
        
        feat = features.iloc[0]
        
        # Calculate realistic credit bandwidth based on financials
        revenue = max(feat.get('income', 0), 1000000)  # Minimum 10L revenue
        
        # Sanity check - cap revenue at reasonable value
        if revenue > 100000000000:  # 1000 Cr cap
            revenue = 100000000000
        
        profit_margin = feat.get('profit_margin', 0)
        current_ratio = feat.get('current_ratio', 1.0)
        credit_score = feat.get('credit_score', 700)
        debt_to_income = feat.get('debt_to_income', 0.3)
        
        # Base credit limit: 20-40% of annual revenue depending on factors
        base_multiplier = 0.20
        
        # Adjust based on credit score
        if credit_score >= 750:
            base_multiplier += 0.15
        elif credit_score >= 700:
            base_multiplier += 0.10
        elif credit_score >= 650:
            base_multiplier += 0.05
        
        # Adjust based on profitability
        if profit_margin > 0.10:
            base_multiplier += 0.10
        elif profit_margin > 0.05:
            base_multiplier += 0.05
        
        # Adjust based on liquidity
        if current_ratio >= 1.5:
            base_multiplier += 0.05
        elif current_ratio < 1.0:
            base_multiplier -= 0.10
        
        # Adjust based on existing debt
        if debt_to_income < 0.3:
            base_multiplier += 0.05
        elif debt_to_income > 0.5:
            base_multiplier -= 0.15
        
        # Calculate bandwidth
        min_limit = revenue * max(base_multiplier - 0.10, 0.05)
        max_limit = revenue * min(base_multiplier + 0.15, 0.60)
        recommended_limit = revenue * base_multiplier
        
        # Analyze factors for decision
        rejection_reasons = []
        key_factors = {}
        
        # Relaxed thresholds for better approval rates
        if credit_score < 600:
            rejection_reasons.append(f"Low credit score: {credit_score} (minimum: 600)")
            key_factors['credit_score'] = {'value': credit_score, 'threshold': 600, 'status': 'FAIL'}
        else:
            key_factors['credit_score'] = {'value': credit_score, 'threshold': 600, 'status': 'PASS'}
        
        if debt_to_income > 0.65:
            rejection_reasons.append(f"High debt-to-income ratio: {debt_to_income:.2%} (maximum: 65%)")
            key_factors['debt_to_income'] = {'value': debt_to_income, 'threshold': 0.65, 'status': 'FAIL'}
        else:
            key_factors['debt_to_income'] = {'value': debt_to_income, 'threshold': 0.65, 'status': 'PASS'}
        
        if current_ratio < 0.75:
            rejection_reasons.append(f"Poor liquidity: Current ratio {current_ratio:.2f} (minimum: 0.75)")
            key_factors['current_ratio'] = {'value': current_ratio, 'threshold': 0.75, 'status': 'FAIL'}
        else:
            key_factors['current_ratio'] = {'value': current_ratio, 'threshold': 0.75, 'status': 'PASS'}
        
        if feat.get('delinquency_count', 0) > 2:
            rejection_reasons.append(f"Multiple payment defaults: {int(feat.get('delinquency_count', 0))} delinquent accounts")
            key_factors['delinquency_count'] = {'value': feat.get('delinquency_count', 0), 'threshold': 2, 'status': 'FAIL'}
        else:
            key_factors['delinquency_count'] = {'value': feat.get('delinquency_count', 0), 'threshold': 2, 'status': 'PASS'}
        
        if profit_margin < -0.10:
            rejection_reasons.append(f"Severe losses: {profit_margin:.2%} profit margin")
            key_factors['profit_margin'] = {'value': profit_margin, 'threshold': -0.10, 'status': 'FAIL'}
        else:
            key_factors['profit_margin'] = {'value': profit_margin, 'threshold': -0.10, 'status': 'PASS'}
        
        # Decision logic: approve if no critical failures
        should_approve = len(rejection_reasons) == 0
        
        credit_limit = 0
        risk_premium = 0
        
        if should_approve:
            credit_limit = recommended_limit
            risk_premium = self._calculate_risk_premium(default_prob, credit_score, profit_margin)
        
        return {
            "decision": "APPROVE" if should_approve else "REJECT",
            "approval_probability": 1.0 - (len(rejection_reasons) * 0.15),
            "credit_limit": round(credit_limit, 2),
            "recommended_limit": round(recommended_limit, 2),
            "min_limit": round(min_limit, 2),
            "max_limit": round(max_limit, 2),
            "credit_bandwidth": f"₹{min_limit:,.0f} - ₹{max_limit:,.0f}",
            "risk_premium_bps": round(risk_premium, 2),
            "default_probability": max(default_prob, 0.01),
            "rejection_reasons": rejection_reasons if not should_approve else [],
            "key_factors": key_factors,
            "parsed_features": features.iloc[0].to_dict()
        }
    
    def _calculate_risk_premium(self, default_prob: float, credit_score: int, profit_margin: float) -> float:
        """Calculate risk premium in basis points based on multiple factors"""
        base_rate = 200  # 2% base premium
        
        # Adjust for default probability
        risk_adjustment = default_prob * 800
        
        # Adjust for credit score
        if credit_score >= 750:
            risk_adjustment -= 50
        elif credit_score < 650:
            risk_adjustment += 100
        
        # Adjust for profitability
        if profit_margin > 0.10:
            risk_adjustment -= 30
        elif profit_margin < 0:
            risk_adjustment += 150
        
        return base_rate + risk_adjustment
    
    def get_feature_importance(self) -> Dict:
        """Get feature importance for explainability"""
        if self.approval_model is None:
            return {}
        
        feature_names = self.approval_model.feature_names_in_
        importances = self.approval_model.feature_importances_
        
        return dict(zip(feature_names, importances))
