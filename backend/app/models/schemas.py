from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime
from enum import Enum

class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"

class Transaction(BaseModel):
    transaction_id: str
    user_id: str
    amount: float
    merchant_category: str
    merchant_name: str
    timestamp: datetime
    location: str
    device_id: str
    ip_address: str
    payment_method: str
    currency: str = "USD"

class UserBehavior(BaseModel):
    user_id: str
    avg_transaction_amount: float
    transaction_count_24h: int
    transaction_count_7d: int
    common_merchants: List[str]
    common_locations: List[str]
    common_devices: List[str]
    typical_transaction_hours: List[int]
    last_transaction_time: Optional[datetime]

class DeviceFingerprint(BaseModel):
    device_id: str
    device_type: str
    os: str
    browser: str
    is_new_device: bool
    risk_score: float

class FeatureSet(BaseModel):
    amount_deviation: float
    velocity_1h: int
    velocity_24h: int
    location_deviation: float
    device_risk: float
    time_deviation: float
    merchant_risk: float
    is_new_device: int
    is_new_location: int
    amount_to_avg_ratio: float

class RiskAssessment(BaseModel):
    transaction_id: str
    risk_score: float
    risk_level: RiskLevel
    decision: str
    explanations: List[str]
    shap_values: Dict[str, float]
    model_contributions: Dict[str, float]
    processing_time_ms: float
    timestamp: datetime

class FraudFeedback(BaseModel):
    transaction_id: str
    is_fraud: bool
    user_confirmation: bool
    notes: Optional[str]

class TransactionStats(BaseModel):
    total_transactions: int
    flagged_transactions: int
    blocked_transactions: int
    fraud_prevented: int
    avg_processing_time: float
