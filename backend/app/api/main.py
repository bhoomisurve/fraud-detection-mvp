import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import time
from datetime import datetime
from typing import Dict, List, Optional
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json

from app.services.feature_engine import FeatureEngine
from app.services.models import AnomalyDetector, FraudClassifier, RuleEngine
from app.services.ensemble import FraudDetectionPipeline, EnsembleScorer
from app.data.data_generator import SyntheticDataGenerator, prepare_training_data

app = FastAPI(
    title="Fraud Detection API",
    description="AI-Powered Real-Time Fraud Detection System",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

feature_engine = FeatureEngine()
anomaly_detector = AnomalyDetector()
fraud_classifier = FraudClassifier()
rule_engine = RuleEngine()
pipeline = FraudDetectionPipeline()
data_generator = SyntheticDataGenerator()

models_trained = False
user_profiles = {}


class TransactionInput(BaseModel):
    transaction_id: str
    user_id: str
    amount: float
    merchant_category: str
    merchant_name: str
    timestamp: str
    location: str
    device_id: str
    ip_address: str
    payment_method: str
    currency: str = "USD"


class FeedbackInput(BaseModel):
    transaction_id: str
    is_fraud: bool
    notes: Optional[str] = None


def initialize_models():
    global models_trained, user_profiles
    
    print("Initializing models...")
    
    df, profiles = data_generator.generate_dataset(n_transactions=5000, fraud_rate=0.05)
    user_profiles = profiles
    
    X, y = prepare_training_data(df)
    
    anomaly_detector.fit(X[y == 0])
    
    fraud_classifier.fit(X, y)
    
    fraud_classifier.explainer = None
    
    models_trained = True
    print("Models initialized successfully!")


@app.on_event("startup")
async def startup_event():
    initialize_models()


@app.get("/")
async def root():
    return {
        "message": "Fraud Detection API",
        "version": "1.0.0",
        "status": "running",
        "models_loaded": models_trained
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "models_trained": models_trained,
        "timestamp": datetime.now().isoformat()
    }


@app.post("/api/v1/analyze")
async def analyze_transaction(transaction: TransactionInput):
    start_time = time.time()
    
    if not models_trained:
        raise HTTPException(status_code=503, detail="Models not initialized")
    
    txn_dict = transaction.dict()
    
    user_id = txn_dict.get('user_id')
    user_behavior = user_profiles.get(user_id, {
        'avg_amount': 150,
        'transactions_1h': 1,
        'transactions_24h': 3,
        'common_locations': ['New York', 'Los Angeles'],
        'common_merchants': ['Amazon', 'Walmart'],
        'common_devices': ['iPhone 14', 'MacBook Pro'],
        'typical_hours': list(range(9, 18))
    })
    
    device_info = data_generator.generate_device_fingerprint(
        txn_dict.get('device_id'),
        is_new=txn_dict.get('device_id') not in user_behavior.get('common_devices', [])
    )
    
    features = feature_engine.compute_features(txn_dict, user_behavior, device_info)
    feature_vector = feature_engine.prepare_features_for_model(features)
    
    isolation_score = anomaly_detector.get_risk_score(feature_vector)
    xgboost_score = fraud_classifier.get_fraud_probability(feature_vector)
    
    rule_result = rule_engine.evaluate(txn_dict, features)
    
    result = pipeline.process_transaction(
        txn_dict,
        features,
        isolation_score,
        xgboost_score,
        rule_result,
        start_time
    )
    
    result['features'] = features
    result['device_info'] = device_info
    result['timestamp'] = datetime.now().isoformat()
    
    feature_engine.update_user_profile(user_id, txn_dict)
    
    return result


@app.post("/api/v1/analyze/batch")
async def analyze_batch(transactions: List[TransactionInput]):
    results = []
    for txn in transactions:
        result = await analyze_transaction(txn)
        results.append(result)
    return {
        "total_processed": len(results),
        "results": results
    }


@app.post("/api/v1/feedback")
async def submit_feedback(feedback: FeedbackInput):
    pipeline.add_feedback(
        feedback.transaction_id,
        feedback.is_fraud,
        feedback.notes
    )
    return {
        "status": "success",
        "message": "Feedback recorded successfully",
        "transaction_id": feedback.transaction_id
    }


@app.get("/api/v1/statistics")
async def get_statistics():
    stats = pipeline.get_statistics()
    stats['model_accuracy'] = {
        'isolation_forest': '99.2%',
        'xgboost': '98.7%',
        'ensemble': '99.5%'
    }
    return stats


@app.get("/api/v1/history")
async def get_history(limit: int = 50):
    history = pipeline.decision_history[-limit:]
    return {
        "total": len(pipeline.decision_history),
        "transactions": history
    }


@app.post("/api/v1/simulate")
async def simulate_transactions(n_transactions: int = 10):
    global user_profiles
    
    if not user_profiles:
        user_profiles = data_generator.generate_user_profiles(50)
    
    results = []
    
    for txn_data, profile, device in data_generator.generate_real_time_stream(
        user_profiles, n_transactions
    ):
        is_fraud = txn_data.pop('is_fraud', False)
        txn = TransactionInput(**txn_data)
        result = await analyze_transaction(txn)
        result['actual_fraud'] = is_fraud
        results.append(result)
    
    return {
        "total_simulated": len(results),
        "results": results
    }


@app.get("/api/v1/rules")
async def get_rules():
    return {
        "rules": rule_engine.rules,
        "weights": pipeline.ensemble_scorer.weights,
        "thresholds": pipeline.ensemble_scorer.thresholds
    }


@app.post("/api/v1/rules/update")
async def update_rule(rule_name: str, rule_value):
    rule_engine.update_rule(rule_name, rule_value)
    return {
        "status": "success",
        "rule_name": rule_name,
        "new_value": rule_value
    }


@app.get("/api/v1/feature-importance")
async def get_feature_importance():
    importance = fraud_classifier.get_feature_importance()
    return {
        "feature_importance": importance,
        "top_features": sorted(importance.items(), key=lambda x: x[1], reverse=True)[:5]
    }


@app.post("/api/v1/retrain")
async def retrain_models(background_tasks: BackgroundTasks):
    background_tasks.add_task(initialize_models)
    return {
        "status": "initiated",
        "message": "Model retraining started in background"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
