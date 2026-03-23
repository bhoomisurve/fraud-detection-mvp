import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import random
import uuid
from typing import Dict, List, Tuple

class SyntheticDataGenerator:
    def __init__(self, seed: int = 42):
        np.random.seed(seed)
        random.seed(seed)
        
        self.merchants = {
            'retail': ['Amazon', 'Walmart', 'Target', 'Best Buy', 'Costco'],
            'food': ['McDonalds', 'Starbucks', 'Uber Eats', 'DoorDash', 'Subway'],
            'travel': ['Delta', 'United', 'Marriott', 'Airbnb', 'Expedia'],
            'entertainment': ['Netflix', 'Spotify', 'AMC', 'Disney+', 'HBO Max'],
            'gambling': ['BetMGM', 'DraftKings', 'FanDuel', 'Caesars', 'PokerStars'],
            'crypto': ['Coinbase', 'Binance', 'Crypto.com', 'Kraken', 'Gemini'],
            'money_transfer': ['Western Union', 'MoneyGram', 'Remitly', 'Wise', 'PayPal']
        }
        
        self.merchant_categories = {
            'retail': 0.1, 'food': 0.05, 'travel': 0.3, 'entertainment': 0.05,
            'gambling': 0.7, 'crypto': 0.8, 'money_transfer': 0.6
        }
        
        self.locations = ['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix', 
                         'Philadelphia', 'San Antonio', 'San Diego', 'Dallas', 'San Jose',
                         'London', 'Tokyo', 'Singapore', 'Dubai', 'Sydney']
        
        self.payment_methods = ['credit_card', 'debit_card', 'apple_pay', 'google_pay', 'bank_transfer']
        
        self.devices = ['iPhone 14', 'iPhone 13', 'Samsung S23', 'MacBook Pro', 'Windows PC', 'iPad']
        
    def generate_user_profiles(self, n_users: int = 100) -> Dict:
        profiles = {}
        for i in range(n_users):
            user_id = f"user_{i+1:04d}"
            profiles[user_id] = {
                'user_id': user_id,
                'avg_transaction_amount': np.random.lognormal(4, 1),
                'transaction_count_24h': np.random.poisson(3),
                'transaction_count_7d': np.random.poisson(15),
                'common_merchants': random.sample(
                    self.merchants['retail'] + self.merchants['food'] + self.merchants['entertainment'],
                    k=min(5, len(self.merchants['retail'] + self.merchants['food'] + self.merchants['entertainment']))
                ),
                'common_locations': random.sample(self.locations[:10], k=3),
                'common_devices': random.sample(self.devices, k=2),
                'typical_transaction_hours': random.sample(range(8, 22), k=8)
            }
        return profiles
    
    def generate_transaction(self, user_profile: Dict, is_fraud: bool = False) -> Dict:
        if is_fraud:
            return self._generate_fraudulent_transaction(user_profile)
        return self._generate_normal_transaction(user_profile)
    
    def _generate_normal_transaction(self, profile: Dict) -> Dict:
        merchant_category = random.choice(['retail', 'food', 'entertainment', 'travel'])
        merchant_name = random.choice(self.merchants[merchant_category])
        
        amount = np.random.lognormal(
            np.log(profile['avg_transaction_amount']), 
            0.5
        )
        
        location = random.choice(profile['common_locations'])
        device = random.choice(profile['common_devices'])
        hour = random.choice(profile['typical_transaction_hours'])
        
        timestamp = datetime.now() - timedelta(
            hours=random.randint(0, 24),
            minutes=random.randint(0, 60)
        )
        timestamp = timestamp.replace(hour=hour)
        
        return {
            'transaction_id': str(uuid.uuid4()),
            'user_id': profile['user_id'],
            'amount': round(amount, 2),
            'merchant_category': merchant_category,
            'merchant_name': merchant_name,
            'timestamp': timestamp.isoformat(),
            'location': location,
            'device_id': device,
            'ip_address': f"192.168.{random.randint(1,255)}.{random.randint(1,255)}",
            'payment_method': random.choice(self.payment_methods),
            'currency': 'USD'
        }
    
    def _generate_fraudulent_transaction(self, profile: Dict) -> Dict:
        fraud_types = ['high_amount', 'unusual_location', 'rapid_transactions', 'high_risk_merchant']
        fraud_type = random.choice(fraud_types)
        
        if fraud_type == 'high_amount':
            amount = profile['avg_transaction_amount'] * np.random.uniform(5, 20)
            merchant_category = random.choice(['retail', 'electronics', 'jewelry'])
            location = random.choice(profile['common_locations'])
            device = random.choice(profile['common_devices'])
            
        elif fraud_type == 'unusual_location':
            amount = np.random.lognormal(np.log(profile['avg_transaction_amount']), 0.5)
            merchant_category = random.choice(['retail', 'travel'])
            location = random.choice(self.locations[10:])
            device = f"Unknown Device {random.randint(1000, 9999)}"
            
        elif fraud_type == 'rapid_transactions':
            amount = np.random.lognormal(np.log(profile['avg_transaction_amount'] * 2), 0.5)
            merchant_category = random.choice(['retail', 'food'])
            location = random.choice(profile['common_locations'])
            device = random.choice(self.devices)
            
        else:
            amount = np.random.lognormal(np.log(profile['avg_transaction_amount'] * 3), 0.5)
            merchant_category = random.choice(['gambling', 'crypto', 'money_transfer'])
            location = random.choice(self.locations)
            device = random.choice(self.devices)
        
        merchant_name = random.choice(self.merchants.get(merchant_category, self.merchants['retail']))
        
        timestamp = datetime.now() - timedelta(
            minutes=random.randint(0, 120)
        )
        hour = random.randint(0, 23)
        timestamp = timestamp.replace(hour=hour)
        
        return {
            'transaction_id': str(uuid.uuid4()),
            'user_id': profile['user_id'],
            'amount': round(amount, 2),
            'merchant_category': merchant_category,
            'merchant_name': merchant_name,
            'timestamp': timestamp.isoformat(),
            'location': location,
            'device_id': device,
            'ip_address': f"10.0.{random.randint(1,255)}.{random.randint(1,255)}",
            'payment_method': random.choice(self.payment_methods),
            'currency': 'USD',
            'is_fraud': True
        }
    
    def generate_dataset(self, n_transactions: int = 10000, fraud_rate: float = 0.05) -> Tuple[pd.DataFrame, pd.DataFrame]:
        profiles = self.generate_user_profiles(n_transactions // 100)
        
        transactions = []
        labels = []
        
        n_fraud = int(n_transactions * fraud_rate)
        n_normal = n_transactions - n_fraud
        
        for _ in range(n_normal):
            profile = random.choice(list(profiles.values()))
            txn = self._generate_normal_transaction(profile)
            txn['is_fraud'] = False
            transactions.append(txn)
            labels.append(0)
        
        for _ in range(n_fraud):
            profile = random.choice(list(profiles.values()))
            txn = self._generate_fraudulent_transaction(profile)
            txn['is_fraud'] = True
            transactions.append(txn)
            labels.append(1)
        
        df = pd.DataFrame(transactions)
        df['label'] = labels
        
        df = df.sample(frac=1, random_state=42).reset_index(drop=True)
        
        return df, profiles
    
    def generate_device_fingerprint(self, device_id: str, is_new: bool = False) -> Dict:
        device_types = ['mobile', 'desktop', 'tablet']
        oss = ['iOS', 'Android', 'Windows', 'MacOS', 'Linux']
        browsers = ['Safari', 'Chrome', 'Firefox', 'Edge', 'Samsung Internet']
        
        return {
            'device_id': device_id,
            'device_type': random.choice(device_types),
            'os': random.choice(oss),
            'browser': random.choice(browsers),
            'is_new_device': is_new,
            'risk_score': random.uniform(0.8, 1.0) if is_new else random.uniform(0, 0.3)
        }
    
    def generate_real_time_stream(self, profiles: Dict, n_transactions: int = 100):
        for _ in range(n_transactions):
            profile = random.choice(list(profiles.values()))
            is_fraud = random.random() < 0.05
            txn = self.generate_transaction(profile, is_fraud)
            device = self.generate_device_fingerprint(
                txn['device_id'], 
                is_fraud and random.random() < 0.7
            )
            yield txn, profile, device


def prepare_training_data(df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
    feature_cols = [
        'amount', 'hour_of_day', 'day_of_week'
    ]
    
    df['hour_of_day'] = pd.to_datetime(df['timestamp']).dt.hour
    df['day_of_week'] = pd.to_datetime(df['timestamp']).dt.dayofweek
    
    df['merchant_risk'] = df['merchant_category'].map({
        'retail': 0.1, 'food': 0.05, 'travel': 0.3, 'entertainment': 0.05,
        'gambling': 0.7, 'crypto': 0.8, 'money_transfer': 0.6
    }).fillna(0.3)
    
    df['is_new_location'] = df['location'].apply(lambda x: 0 if x in ['New York', 'Los Angeles', 'Chicago'] else 1)
    df['is_new_device'] = np.random.choice([0, 1], size=len(df), p=[0.9, 0.1])
    df['velocity_1h'] = np.random.poisson(2, size=len(df))
    df['velocity_24h'] = np.random.poisson(5, size=len(df))
    df['amount_deviation'] = np.abs(df['amount'] - df['amount'].mean()) / df['amount'].mean()
    df['location_deviation'] = df['is_new_location'] * 0.7
    df['device_risk'] = df['is_new_device'] * 0.8
    df['time_deviation'] = np.where(
        df['hour_of_day'].isin(range(8, 22)), 0, 0.5
    )
    df['amount_to_avg_ratio'] = df['amount'] / df['amount'].mean()
    
    feature_cols = [
        'amount', 'amount_deviation', 'velocity_1h', 'velocity_24h',
        'location_deviation', 'device_risk', 'time_deviation',
        'merchant_risk', 'is_new_device', 'is_new_location',
        'amount_to_avg_ratio', 'hour_of_day', 'day_of_week'
    ]
    
    X = df[feature_cols].values
    y = df['label'].values
    
    return X, y
