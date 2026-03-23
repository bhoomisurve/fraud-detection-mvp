import requests
import json
import time
from datetime import datetime

API_URL = "http://localhost:8000"

def print_separator():
    print("=" * 60)

def test_health():
    print("\n🔍 Testing Health Endpoint...")
    response = requests.get(f"{API_URL}/health")
    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    return response.status_code == 200

def test_root():
    print("\n🔍 Testing Root Endpoint...")
    response = requests.get(f"{API_URL}/")
    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    return response.status_code == 200

def test_analyze_transaction():
    print("\n🔍 Testing Transaction Analysis...")
    
    transactions = [
        {
            "transaction_id": f"txn_normal_{int(time.time())}",
            "user_id": "user_0001",
            "amount": 150.00,
            "merchant_category": "retail",
            "merchant_name": "Amazon",
            "timestamp": datetime.now().isoformat(),
            "location": "New York",
            "device_id": "iPhone 14",
            "ip_address": "192.168.1.1",
            "payment_method": "credit_card",
            "currency": "USD"
        },
        {
            "transaction_id": f"txn_suspicious_{int(time.time())}",
            "user_id": "user_0001",
            "amount": 8500.00,
            "merchant_category": "gambling",
            "merchant_name": "BetMGM",
            "timestamp": datetime.now().isoformat(),
            "location": "Tokyo",
            "device_id": "Unknown Device",
            "ip_address": "10.0.0.1",
            "payment_method": "credit_card",
            "currency": "USD"
        },
        {
            "transaction_id": f"txn_high_velocity_{int(time.time())}",
            "user_id": "user_0002",
            "amount": 500.00,
            "merchant_category": "crypto",
            "merchant_name": "Coinbase",
            "timestamp": datetime.now().isoformat(),
            "location": "Singapore",
            "device_id": "Unknown Device",
            "ip_address": "10.0.0.2",
            "payment_method": "debit_card",
            "currency": "USD"
        }
    ]
    
    for i, txn in enumerate(transactions, 1):
        print(f"\n--- Transaction {i} ---")
        print(f"Amount: ${txn['amount']}")
        print(f"Category: {txn['merchant_category']}")
        print(f"Location: {txn['location']}")
        
        start_time = time.time()
        response = requests.post(f"{API_URL}/api/v1/analyze", json=txn)
        elapsed = (time.time() - start_time) * 1000
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ Analysis Complete ({elapsed:.1f}ms)")
            print(f"Risk Score: {result['risk_score']}")
            print(f"Risk Level: {result['risk_level']}")
            print(f"Decision: {result['decision']}")
            print(f"Processing Time: {result['processing_time_ms']}ms")
            if result.get('explanations'):
                print("Explanations:")
                for exp in result['explanations']:
                    print(f"  - {exp}")
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)
    
    return True

def test_simulate():
    print("\n🔍 Testing Transaction Simulation...")
    response = requests.post(f"{API_URL}/api/v1/simulate?n_transactions=5")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"Total Simulated: {result['total_simulated']}")
        
        fraud_count = sum(1 for r in result['results'] if r.get('actual_fraud'))
        blocked_count = sum(1 for r in result['results'] if r['decision'] == 'BLOCK')
        
        print(f"Actual Fraud: {fraud_count}")
        print(f"Blocked: {blocked_count}")
        
        print("\n--- Sample Results ---")
        for r in result['results'][:3]:
            print(f"  {r['transaction_id'][:20]}... | Score: {r['risk_score']} | "
                  f"Level: {r['risk_level']} | Decision: {r['decision']}")
    
    return response.status_code == 200

def test_statistics():
    print("\n🔍 Testing Statistics Endpoint...")
    response = requests.get(f"{API_URL}/api/v1/statistics")
    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    return response.status_code == 200

def test_rules():
    print("\n🔍 Testing Rules Endpoint...")
    response = requests.get(f"{API_URL}/api/v1/rules")
    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    return response.status_code == 200

def test_feature_importance():
    print("\n🔍 Testing Feature Importance...")
    response = requests.get(f"{API_URL}/api/v1/feature-importance")
    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    return response.status_code == 200

def test_feedback():
    print("\n🔍 Testing Feedback Endpoint...")
    feedback = {
        "transaction_id": "txn_test_001",
        "is_fraud": True,
        "notes": "Confirmed fraudulent transaction"
    }
    response = requests.post(f"{API_URL}/api/v1/feedback", json=feedback)
    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    return response.status_code == 200

def main():
    print_separator()
    print("   FRAUD DETECTION MVP - API TEST SUITE")
    print_separator()
    
    tests = [
        ("Health Check", test_health),
        ("Root Endpoint", test_root),
        ("Analyze Transaction", test_analyze_transaction),
        ("Simulate Transactions", test_simulate),
        ("Statistics", test_statistics),
        ("Rules", test_rules),
        ("Feature Importance", test_feature_importance),
        ("Feedback", test_feedback)
    ]
    
    results = []
    for name, test_func in tests:
        try:
            success = test_func()
            results.append((name, success))
        except Exception as e:
            print(f"\n❌ {name} failed with error: {e}")
            results.append((name, False))
    
    print_separator()
    print("   TEST RESULTS SUMMARY")
    print_separator()
    
    passed = sum(1 for _, s in results if s)
    total = len(results)
    
    for name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {name}")
    
    print_separator()
    print(f"Total: {passed}/{total} tests passed")
    print_separator()

if __name__ == "__main__":
    main()