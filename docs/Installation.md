# Installation Guide

## Prerequisites
- Node.js (v18+ or v20+)
- Python (v3.10+)
- PostgreSQL / Neon PostgreSQL instance

## Local Development Setup

### 1. Backend Setup
```bash
cd backend
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

### 3. Database Setup
Execute initial migrations or run schema script:
```bash
psql -U <user> -d <database_name> -f database/schema.sql
```
