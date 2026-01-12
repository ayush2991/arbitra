# Arbitra 🚀

Arbitra is an agentic AI-powered trading simulation platform. It demonstrates how an autonomous agent can make real-time trading decisions based on market fluctuations.

## Features

- **Autonomous Agent**: A Python-based trading agent that implements simple trend-following logic.
- **Real Market Data**: Live security price updates from Yahoo Finance (AAPL, GOOGL, BTC, ETH).
- **Modern Trading Dashboard**: A sleek, dark-themed UI built with React and Vanilla CSS.
- **Real-time Analytics**: Visualized capital evolution and trade history.

## Tech Stack

- **Frontend**: React (Vite), Vanilla CSS, Framer Motion, Recharts, Lucide Icons.
- **Backend**: Python (FastAPI), yfinance, Pandas, Numpy, Uvicorn.

## Getting Started

### Prerequisites

- Node.js (v18+)
- Python (v3.10+)

### Setup & Running

#### 1. Backend
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt  # Or manually install fastapi uvicorn pandas numpy python-multipart
python3 main.py
```

#### 2. Frontend
```bash
cd frontend
npm install
npm run dev -- --port 5173
```

Navigate to `http://localhost:5173` to see the dashboard.

## Project Structure

- `frontend/`: React application.
- `backend/`: FastAPI server and trading logic.
- `.agent/`: Agent-specific workflows and task documentation.

## License

MIT
