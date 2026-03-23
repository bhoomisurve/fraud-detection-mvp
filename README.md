# Fraud Shield

AI-powered real-time fraud detection system.

## Overview

A production-ready MVP that analyzes financial transactions in real-time and assigns risk scores using an ensemble of machine learning models.

### Tech Stack
- **Backend**: FastAPI, Python, scikit-learn, XGBoost, SHAP
- **Frontend**: React
- **ML Models**: Isolation Forest, XGBoost, Rule Engine

### Architecture

```
Transaction → Feature Engine → [Isolation Forest + XGBoost + Rules] → Ensemble Score → Decision
```

### Risk Levels

| Score | Level | Action |
|-------|-------|--------|
| 0-30 | LOW | Allow |
| 30-60 | MEDIUM | Step-up Authentication |
| 60-100 | HIGH | Block |

## Local Development

### Prerequisites
- Python 3.10+
- Node.js 18+

### Run Backend

```bash
cd backend
pip install -r requirements.txt
python run.py
```

API runs at http://localhost:8000

### Run Frontend

```bash
cd frontend
npm install
npm start
```

Dashboard runs at http://localhost:3000

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| POST | `/api/v1/analyze` | Analyze single transaction |
| POST | `/api/v1/simulate` | Simulate transactions |
| GET | `/api/v1/statistics` | System statistics |
| POST | `/api/v1/feedback` | Submit fraud feedback |

### Example Request

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

## Deployment

### Deploy Backend to Render

1. Go to https://dashboard.render.com
2. Click **New** → **Web Service**
3. Connect GitHub and select this repository
4. Configure:
   - **Root Directory**: `backend`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python -m uvicorn app.api.main:app --host 0.0.0.0 --port $PORT`
   - **Plan**: Free
5. Click **Create Web Service**

### Deploy Frontend to Vercel

1. Go to https://vercel.com/new
2. Import this GitHub repository
3. Configure:
   - **Root Directory**: `frontend`
   - **Environment Variable**: `REACT_APP_API_URL` = your Render backend URL
4. Click **Deploy**

## License

MIT