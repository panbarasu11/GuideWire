# Kavach AI - Parametric Insurance Platform

Kavach AI is an AI-powered parametric insurance platform for gig workers.

## Setup

### ML Service
cd ml-fastapi
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

### Backend
cd backend-node
npm install
npm start

### Frontend
cd frontend-nextjs
npm install
npm run dev
