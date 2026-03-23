#!/bin/bash

echo "========================================"
echo "  FRAUD SHIELD - Starting MVP"
echo "========================================"
echo ""

# Start backend
echo "Starting Backend Server..."
cd backend
pip install -r requirements.txt
python run.py &
BACKEND_PID=$!
cd ..

# Wait for backend
echo "Waiting for backend to initialize..."
sleep 10

# Start frontend
echo "Starting Frontend Server..."
cd frontend
npm install
npm start &
FRONTEND_PID=$!
cd ..

echo ""
echo "========================================"
echo "  Backend: http://localhost:8000"
echo "  Frontend: http://localhost:3000"
echo "========================================"
echo ""
echo "Press Ctrl+C to stop servers..."

# Wait for interrupt
trap "kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait