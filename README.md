# FRAUD SHIELD - AI-Powered Real-Time Fraud Detection System

A fully functional MVP prototype for detecting fraudulent transactions in real-time using machine learning ensemble methods.

## Features

- **Real-Time Analysis**: Analyzes transactions in <200ms
- **Multi-Model Detection**: Combines Isolation Forest, XGBoost, and Rule Engine
- **Ensemble Risk Scoring**: Dynamic risk scores (0-100)
- **Explainable AI**: SHAP-based explanations for flagged transactions
- **Adaptive Learning**: Feedback loop for continuous improvement
- **Smart Decisions**: Allow / Step-up Authentication / Block

## Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+

### Run Backend

```bash
cd fraud-detection-mvp/backend
pip install -r requirements.txt
python run.py
```

Backend runs at: http://localhost:8000

### Run Frontend

```bash
cd fraud-detection-mvp/frontend
npm install
npm start
```

Frontend runs at: http://localhost:3000

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API info |
| `/health` | GET | Health check |
| `/api/v1/analyze` | POST | Analyze single transaction |
| `/api/v1/simulate` | POST | Simulate transactions |
| `/api/v1/feedback` | POST | Submit fraud feedback |
| `/api/v1/statistics` | GET | System statistics |
| `/api/v1/history` | GET | Transaction history |
| `/api/v1/rules` | GET | View detection rules |
| `/api/v1/feature-importance` | GET | Model feature importance |

## Example API Calls

### Analyze a Transaction

```bash
curl -X POST http://localhost:8000/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "transaction_id": "txn_001",
    "user_id": "user_0001",
    "amount": 5000,
    "merchant_category": "gambling",
    "merchant_name": "BetMGM",
    "timestamp": "2024-01-15T14:30:00",
    "location": "Tokyo",
    "device_id": "Unknown Device",
    "ip_address": "10.0.0.1",
    "payment_method": "credit_card"
  }'
```

### Simulate Transactions

```bash
curl -X POST "http://localhost:8000/api/v1/simulate?n_transactions=20"
```

## Tech Stack

- **Backend**: FastAPI, Python, scikit-learn, XGBoost, SHAP
- **Frontend**: React, Neo-Brutalism UI
- **Models**: Isolation Forest, XGBoost, Rule Engine

## Model Architecture

```
Transaction → Feature Engine → [IF + XGB + Rules] → Ensemble Score → Decision
                                    ↓
                              SHAP Explanations
```

## Risk Levels

| Score | Level | Decision |
|-------|-------|----------|
| 0-30 | LOW | ALLOW |
| 30-60 | MEDIUM | STEP_UP_AUTH |
| 60-100 | HIGH | BLOCK |

## License

MIT License