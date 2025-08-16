#!/bin/bash

echo "Starting IPO Readiness PDF Analyzer in Development Mode..."
echo

# Function to cleanup background processes
cleanup() {
    echo "Shutting down servers..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit 0
}

# Set trap to cleanup on script exit
trap cleanup EXIT INT TERM

echo "Starting Backend Server..."
cd backend
uv run python run.py &
BACKEND_PID=$!

echo "Waiting for backend to start..."
sleep 5

echo "Starting Frontend Server..."
cd ../frontend
npm run dev &
FRONTEND_PID=$!

echo
echo "Both servers are running..."
echo "Backend available at: http://localhost:8000"
echo "Frontend available at: http://localhost:3000"
echo
echo "Press Ctrl+C to stop both servers"

# Wait for background processes
wait