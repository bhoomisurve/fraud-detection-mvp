import numpy as np
from typing import Dict, Tuple, List
import shap
import time

class EnsembleScorer:
    def __init__(self):
        self.weights = {
            'isolation_forest': 0.3,
            'xgboost': 0.45,
            'rule_engine': 0.25
        }
        self.thresholds = {
            'low': 0.3,
            'medium': 0.6,
            'high': 0.8
        }
    
    def compute_ensemble_score(
        self,
        isolation_score: float,
        xgboost_score: float,
        rule_score: float
    ) -> float:
        weighted_score = (
            self.weights['isolation_forest'] * isolation_score +
            self.weights['xgboost'] * xgboost_score +
            self.weights['rule_engine'] * rule_score
        )
        return min(max(weighted_score, 0), 1) * 100
    
    def get_risk_level(self, score: float) -> str:
        if score < self.thresholds['low'] * 100:
            return 'LOW'
        elif score < self.thresholds['medium'] * 100:
            return 'MEDIUM'
        else:
            return 'HIGH'
    
    def get_decision(self, score: float, risk_level: str) -> str:
        if risk_level == 'LOW':
            return 'ALLOW'
        elif risk_level == 'MEDIUM':
            return 'STEP_UP_AUTH'
        else:
            return 'BLOCK'
    
    def get_model_contributions(
        self,
        isolation_score: float,
        xgboost_score: float,
        rule_score: float
    ) -> Dict[str, float]:
        ensemble = self.compute_ensemble_score(isolation_score, xgboost_score, rule_score)
        
        contributions = {
            'isolation_forest': isolation_score * self.weights['isolation_forest'] * 100,
            'xgboost': xgboost_score * self.weights['xgboost'] * 100,
            'rule_engine': rule_score * self.weights['rule_engine'] * 100
        }
        
        return contributions
    
    def update_weights(self, new_weights: Dict[str, float]):
        total = sum(new_weights.values())
        self.weights = {k: v/total for k, v in new_weights.items()}


class ExplainabilityEngine:
    def __init__(self, model=None):
        self.explainer = None
        self.model = model
        self.feature_names = [
            'amount', 'amount_deviation', 'velocity_1h', 'velocity_24h',
            'location_deviation', 'device_risk', 'time_deviation',
            'merchant_risk', 'is_new_device', 'is_new_location',
            'amount_to_avg_ratio', 'hour_of_day', 'day_of_week'
        ]
    
    def initialize_explainer(self, model, X_background: np.ndarray):
        self.model = model
        self.explainer = shap.TreeExplainer(model)
    
    def explain_prediction(self, X: np.ndarray) -> Dict[str, float]:
        if self.explainer is None:
            return self._get_rule_based_explanation(X)
        
        try:
            shap_values = self.explainer.shap_values(X)
            if isinstance(shap_values, list):
                shap_values = shap_values[1]
            
            shap_dict = dict(zip(self.feature_names, shap_values[0]))
            return shap_dict
        except:
            return self._get_rule_based_explanation(X)
    
    def _get_rule_based_explanation(self, X: np.ndarray) -> Dict[str, float]:
        features = X[0] if len(X.shape) > 1 else X
        explanations = {}
        
        for i, name in enumerate(self.feature_names):
            if i < len(features):
                explanations[name] = float(features[i])
        
        return explanations
    
    def generate_human_readable_explanations(
        self,
        shap_values: Dict[str, float],
        features: Dict,
        rule_violations: List[str]
    ) -> List[str]:
        explanations = []
        
        sorted_features = sorted(shap_values.items(), key=lambda x: abs(x[1]), reverse=True)
        
        for feature, value in sorted_features[:5]:
            if abs(value) > 0.1:
                if feature == 'amount' and features.get('amount', 0) > 1000:
                    explanations.append(f"High transaction amount (${features.get('amount', 0):.2f})")
                elif feature == 'amount_deviation' and features.get('amount_deviation', 0) > 0.5:
                    explanations.append(f"Amount deviates {features.get('amount_deviation', 0):.1%} from your average")
                elif feature == 'velocity_1h' and features.get('velocity_1h', 0) > 3:
                    explanations.append(f"Unusual activity: {features.get('velocity_1h', 0)} transactions in 1 hour")
                elif feature == 'location_deviation' and features.get('location_deviation', 0) > 0:
                    explanations.append("Transaction from unusual location")
                elif feature == 'is_new_device' and features.get('is_new_device', 0) == 1:
                    explanations.append("First transaction from this device")
                elif feature == 'merchant_risk' and features.get('merchant_risk', 0) > 0.5:
                    explanations.append("High-risk merchant category")
                elif feature == 'time_deviation' and features.get('time_deviation', 0) > 0:
                    explanations.append("Transaction at unusual time")
        
        explanations.extend(rule_violations[:3])
        
        return list(set(explanations))[:5]


class FraudDetectionPipeline:
    def __init__(self):
        self.ensemble_scorer = EnsembleScorer()
        self.explainability_engine = ExplainabilityEngine()
        self.decision_history = []
        self.feedback_data = []
    
    def process_transaction(
        self,
        transaction: Dict,
        features: Dict,
        isolation_score: float,
        xgboost_score: float,
        rule_result: Tuple[bool, List[str], float],
        start_time: float
    ) -> Dict:
        is_flagged, rule_violations, rule_score = rule_result
        
        risk_score = self.ensemble_scorer.compute_ensemble_score(
            isolation_score, xgboost_score, rule_score
        )
        
        risk_level = self.ensemble_scorer.get_risk_level(risk_score)
        decision = self.ensemble_scorer.get_decision(risk_score, risk_level)
        
        feature_vector = np.array([[
            features.get('amount', 0),
            features.get('amount_deviation', 0),
            features.get('velocity_1h', 0),
            features.get('velocity_24h', 0),
            features.get('location_deviation', 0),
            features.get('device_risk', 0),
            features.get('time_deviation', 0),
            features.get('merchant_risk', 0),
            features.get('is_new_device', 0),
            features.get('is_new_location', 0),
            features.get('amount_to_avg_ratio', 0),
            features.get('hour_of_day', 12),
            features.get('day_of_week', 0)
        ]])
        
        shap_values = self.explainability_engine.explain_prediction(feature_vector)
        
        explanations = self.explainability_engine.generate_human_readable_explanations(
            shap_values, features, rule_violations
        )
        
        model_contributions = self.ensemble_scorer.get_model_contributions(
            isolation_score, xgboost_score, rule_score
        )
        
        processing_time = (time.time() - start_time) * 1000
        
        result = {
            'transaction_id': transaction.get('transaction_id'),
            'risk_score': round(risk_score, 2),
            'risk_level': risk_level,
            'decision': decision,
            'explanations': explanations,
            'shap_values': shap_values,
            'model_contributions': model_contributions,
            'processing_time_ms': round(processing_time, 2)
        }
        
        self.decision_history.append(result)
        
        return result
    
    def add_feedback(self, transaction_id: str, is_fraud: bool, notes: str = None):
        self.feedback_data.append({
            'transaction_id': transaction_id,
            'is_fraud': is_fraud,
            'notes': notes,
            'timestamp': time.time()
        })
    
    def get_statistics(self) -> Dict:
        if not self.decision_history:
            return {
                'total_transactions': 0,
                'flagged_transactions': 0,
                'blocked_transactions': 0,
                'avg_processing_time': 0
            }
        
        total = len(self.decision_history)
        flagged = sum(1 for d in self.decision_history if d['risk_level'] in ['MEDIUM', 'HIGH'])
        blocked = sum(1 for d in self.decision_history if d['decision'] == 'BLOCK')
        avg_time = sum(d['processing_time_ms'] for d in self.decision_history) / total
        
        return {
            'total_transactions': total,
            'flagged_transactions': flagged,
            'blocked_transactions': blocked,
            'fraud_prevented': len(self.feedback_data),
            'avg_processing_time': round(avg_time, 2)
        }
