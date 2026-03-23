import numpy as np
import pandas as pd
from typing import Dict, List, Tuple
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import IsolationForest
import joblib
import os

class FeatureEngine:
    def __init__(self):
        self.scaler = StandardScaler()
        self.label_encoders = {}
        self.user_profiles = {}
        
    def compute_features(self, transaction: Dict, user_behavior: Dict, device_info: Dict) -> Dict:
        features = {}
        
        user_id = transaction.get('user_id')
        profile = self.user_profiles.get(user_id, self._create_default_profile())
        
        features['amount'] = transaction.get('amount', 0)
        features['amount_deviation'] = self._compute_amount_deviation(
            transaction.get('amount', 0), 
            profile.get('avg_amount', 100)
        )
        
        features['velocity_1h'] = profile.get('transactions_1h', 0)
        features['velocity_24h'] = profile.get('transactions_24h', 0)
        
        features['location_deviation'] = self._compute_location_deviation(
            transaction.get('location', ''),
            profile.get('common_locations', [])
        )
        
        features['device_risk'] = device_info.get('risk_score', 0.5)
        features['is_new_device'] = 1 if device_info.get('is_new_device', False) else 0
        
        features['time_deviation'] = self._compute_time_deviation(
            transaction.get('timestamp'),
            profile.get('typical_hours', [9, 10, 11, 14, 15, 16])
        )
        
        features['merchant_risk'] = self._compute_merchant_risk(
            transaction.get('merchant_category', 'unknown')
        )
        
        features['is_new_location'] = 1 if transaction.get('location') not in profile.get('common_locations', []) else 0
        
        features['amount_to_avg_ratio'] = transaction.get('amount', 0) / max(profile.get('avg_amount', 1), 1)
        
        features['hour_of_day'] = pd.to_datetime(transaction.get('timestamp')).hour if transaction.get('timestamp') else 12
        features['day_of_week'] = pd.to_datetime(transaction.get('timestamp')).dayofweek if transaction.get('timestamp') else 0
        
        return features
    
    def _create_default_profile(self) -> Dict:
        return {
            'avg_amount': 150,
            'transactions_1h': 0,
            'transactions_24h': 3,
            'common_locations': ['New York', 'Los Angeles', 'Chicago'],
            'typical_hours': [9, 10, 11, 12, 13, 14, 15, 16, 17],
            'common_merchants': ['amazon', 'walmart', 'target']
        }
    
    def _compute_amount_deviation(self, amount: float, avg_amount: float) -> float:
        if avg_amount == 0:
            return 1.0
        return abs(amount - avg_amount) / avg_amount
    
    def _compute_location_deviation(self, current_location: str, common_locations: List[str]) -> float:
        if current_location in common_locations:
            return 0.0
        return 0.7
    
    def _compute_time_deviation(self, timestamp, typical_hours: List[int]) -> float:
        if not timestamp:
            return 0.0
        try:
            hour = pd.to_datetime(timestamp).hour
            if hour in typical_hours:
                return 0.0
            return 0.5
        except:
            return 0.0
    
    def _compute_merchant_risk(self, merchant_category: str) -> float:
        high_risk_categories = ['gambling', 'crypto', 'money_transfer', 'adult']
        medium_risk_categories = ['electronics', 'jewelry', 'travel']
        
        if merchant_category.lower() in high_risk_categories:
            return 0.8
        elif merchant_category.lower() in medium_risk_categories:
            return 0.4
        return 0.1
    
    def update_user_profile(self, user_id: str, transaction: Dict):
        if user_id not in self.user_profiles:
            self.user_profiles[user_id] = self._create_default_profile()
        
        profile = self.user_profiles[user_id]
        amount = transaction.get('amount', 0)
        
        profile['avg_amount'] = (profile['avg_amount'] * 0.9) + (amount * 0.1)
        profile['transactions_24h'] = profile.get('transactions_24h', 0) + 1
        
        location = transaction.get('location', '')
        if location and location not in profile['common_locations']:
            profile['common_locations'].append(location)
    
    def prepare_features_for_model(self, features: Dict) -> np.ndarray:
        feature_order = [
            'amount', 'amount_deviation', 'velocity_1h', 'velocity_24h',
            'location_deviation', 'device_risk', 'time_deviation',
            'merchant_risk', 'is_new_device', 'is_new_location',
            'amount_to_avg_ratio', 'hour_of_day', 'day_of_week'
        ]
        
        feature_vector = []
        for feat in feature_order:
            feature_vector.append(features.get(feat, 0))
        
        return np.array(feature_vector).reshape(1, -1)
