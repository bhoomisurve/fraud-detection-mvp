import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
import xgboost as xgb
import joblib
import os
from typing import Dict, Tuple, List
import warnings
warnings.filterwarnings('ignore')

class AnomalyDetector:
    def __init__(self, contamination: float = 0.1):
        self.model = IsolationForest(
            contamination=contamination,
            n_estimators=100,
            max_samples='auto',
            random_state=42
        )
        self.is_fitted = False
    
    def fit(self, X: np.ndarray):
        self.model.fit(X)
        self.is_fitted = True
    
    def predict(self, X: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        if not self.is_fitted:
            raise ValueError("Model not fitted. Call fit() first.")
        
        predictions = self.model.predict(X)
        scores = self.model.score_samples(X)
        
        score_range = scores.max() - scores.min()
        if score_range == 0:
            anomaly_scores = np.ones_like(scores) * 0.5
        else:
            anomaly_scores = (scores - scores.min()) / score_range
        risk_scores = 1 - anomaly_scores
        
        return predictions, risk_scores
    
    def get_risk_score(self, X: np.ndarray) -> float:
        _, risk_scores = self.predict(X)
        return float(risk_scores[0])
    
    def save(self, path: str):
        joblib.dump(self.model, path)
    
    def load(self, path: str):
        self.model = joblib.load(path)
        self.is_fitted = True


class FraudClassifier:
    def __init__(self, params: Dict = None):
        default_params = {
            'objective': 'binary:logistic',
            'eval_metric': 'auc',
            'max_depth': 6,
            'learning_rate': 0.1,
            'n_estimators': 100,
            'scale_pos_weight': 10,
            'random_state': 42
        }
        self.params = params or default_params
        self.model = xgb.XGBClassifier(**self.params)
        self.is_fitted = False
        self.feature_names = [
            'amount', 'amount_deviation', 'velocity_1h', 'velocity_24h',
            'location_deviation', 'device_risk', 'time_deviation',
            'merchant_risk', 'is_new_device', 'is_new_location',
            'amount_to_avg_ratio', 'hour_of_day', 'day_of_week'
        ]
    
    def fit(self, X: np.ndarray, y: np.ndarray, eval_set: Tuple = None):
        if eval_set:
            self.model.fit(X, y, eval_set=[eval_set], verbose=False)
        else:
            self.model.fit(X, y)
        self.is_fitted = True
    
    def predict(self, X: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        if not self.is_fitted:
            raise ValueError("Model not fitted. Call fit() first.")
        
        predictions = self.model.predict(X)
        probabilities = self.model.predict_proba(X)
        
        return predictions, probabilities
    
    def get_fraud_probability(self, X: np.ndarray) -> float:
        _, probabilities = self.predict(X)
        return float(probabilities[0][1])
    
    def get_feature_importance(self) -> Dict[str, float]:
        if not self.is_fitted:
            return {}
        importance = self.model.feature_importances_
        return dict(zip(self.feature_names, importance))
    
    def save(self, path: str):
        self.model.save_model(path)
    
    def load(self, path: str):
        self.model.load_model(path)
        self.is_fitted = True


class RuleEngine:
    def __init__(self):
        self.rules = {
            'high_amount_threshold': 5000,
            'velocity_threshold_1h': 5,
            'velocity_threshold_24h': 20,
            'high_risk_merchants': ['gambling', 'crypto', 'money_transfer'],
            'blocked_countries': ['Country_X', 'Country_Y'],
            'max_amount_new_device': 500
        }
    
    def evaluate(self, transaction: Dict, features: Dict) -> Tuple[bool, List[str], float]:
        violations = []
        risk_contributions = []
        
        if transaction.get('amount', 0) > self.rules['high_amount_threshold']:
            violations.append(f"High transaction amount: ${transaction.get('amount')}")
            risk_contributions.append(0.3)
        
        if features.get('velocity_1h', 0) > self.rules['velocity_threshold_1h']:
            violations.append(f"High velocity: {features.get('velocity_1h')} transactions in 1 hour")
            risk_contributions.append(0.4)
        
        if features.get('velocity_24h', 0) > self.rules['velocity_threshold_24h']:
            violations.append(f"Very high velocity: {features.get('velocity_24h')} transactions in 24 hours")
            risk_contributions.append(0.5)
        
        merchant_category = transaction.get('merchant_category', '').lower()
        if merchant_category in self.rules['high_risk_merchants']:
            violations.append(f"High-risk merchant category: {merchant_category}")
            risk_contributions.append(0.35)
        
        if transaction.get('location') in self.rules['blocked_countries']:
            violations.append(f"Transaction from blocked location: {transaction.get('location')}")
            risk_contributions.append(0.9)
        
        if features.get('is_new_device', 0) == 1:
            if transaction.get('amount', 0) > self.rules['max_amount_new_device']:
                violations.append(f"High amount on new device: ${transaction.get('amount')}")
                risk_contributions.append(0.45)
        
        if features.get('amount_to_avg_ratio', 1) > 5:
            violations.append(f"Amount {features.get('amount_to_avg_ratio'):.1f}x higher than average")
            risk_contributions.append(0.3)
        
        if features.get('location_deviation', 0) > 0.5:
            violations.append("Unusual location detected")
            risk_contributions.append(0.25)
        
        risk_score = min(sum(risk_contributions), 1.0) if risk_contributions else 0.0
        is_flagged = len(violations) > 0
        
        return is_flagged, violations, risk_score
    
    def add_rule(self, rule_name: str, rule_value):
        self.rules[rule_name] = rule_value
    
    def update_rule(self, rule_name: str, rule_value):
        if rule_name in self.rules:
            self.rules[rule_name] = rule_value
