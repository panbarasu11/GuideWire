# Kavach AI – Zero-Touch Parametric Insurance Platform

**Guidewire DevTrails 2026 - Phase 2**  
*AI-Powered Insurance for Chennai's Gig Economy*

---

## 🎯 Executive Summary

**Kavach AI** is a next-generation parametric insurance platform designed specifically for gig delivery workers in Chennai, India. The system eliminates traditional claims processing through AI-driven automation, providing instant payouts when weather or environmental triggers are met.

**Key Innovation:** Zero-Touch Claims Processing  
**Technology Stack:** FastAPI + Random Forest ML + Isolation Forest Fraud Detection  
**Guidewire Architecture:** Mirrors PolicyCenter & ClaimCenter design patterns

---

## 📋 Table of Contents

1. [Project Overview](#project-overview)
2. [Architecture & Design Philosophy](#architecture--design-philosophy)
3. [Guidewire Component Mapping](#guidewire-component-mapping)
4. [System Components](#system-components)
5. [Installation & Setup](#installation--setup)
6. [Running the Application](#running-the-application)
7. [API Documentation](#api-documentation)
8. [Testing & Simulation](#testing--simulation)
9. [Deployment Guide](#deployment-guide)
10. [Future Roadmap](#future-roadmap)

---

## 🎨 Project Overview

### Problem Statement

Gig delivery workers in Chennai face:
- **Weather Disruptions:** Monsoon rains (>60mm/24hr), heatwaves (>40°C), cyclones
- **Income Loss:** Unable to work = No earnings
- **Insurance Gap:** Traditional insurance is complex, expensive, and has slow claims

### Solution: Kavach AI

A **parametric insurance** platform that:
1. **Automatically detects** when weather thresholds are breached (Oracle Service)
2. **Instantly approves** legitimate claims using AI (Zero-Touch Engine)
3. **Transfers money** to worker's UPI within minutes (₹800-₹1800 payouts)
4. **Prevents fraud** using ML-based Ghost Fleet detection

### Persona: Meet Raj

- **Name:** Raj Kumar
- **Age:** 28
- **Job:** Swiggy delivery partner in Velachery, Chennai
- **Need:** Protection against monsoon rains that prevent deliveries
- **Policy:** Kavach Basic (₹30/week, ₹800 payout if rain >60mm)

---

## 🏗️ Architecture & Design Philosophy

### Guidewire Principles Applied

1. **Configuration over Coding**
   - Policy tiers (Basic/Standard/Premium) defined in `POLICY_CONFIG` dict
   - No hardcoded logic – all thresholds configurable
   
2. **Separation of Concerns**
   - `app_logic.py` = Business layer (FastAPI endpoints)
   - `ai_engine.py` = Intelligence layer (ML models)
   - `dashboard.html` = Presentation layer (UI)

3. **Entity-Driven Design**
   - Workers → Guidewire `Account/Contact`
   - Policies → Guidewire `PolicyPeriod`
   - Claims → Guidewire `Claim` with `ClaimSegment`, `Exposure`, `CheckReport`

### System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                      KAVACH AI PLATFORM                      │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐      ┌──────────────┐      ┌───────────┐ │
│  │   Frontend   │◄────►│   FastAPI    │◄────►│  AI Layer │ │
│  │ (dashboard.  │      │  (app_logic  │      │(ai_engine)│ │
│  │    html)     │      │     .py)     │      │   .py     │ │
│  └──────────────┘      └──────┬───────┘      └─────┬─────┘ │
│                                │                     │        │
│                                ▼                     ▼        │
│                    ┌───────────────────┐  ┌────────────────┐│
│                    │   Policy DB       │  │  ML Models     ││
│                    │   Claims DB       │  │  - Random      ││
│                    │   Workers DB      │  │    Forest      ││
│                    └───────────────────┘  │  - Isolation   ││
│                                            │    Forest      ││
│                    ┌───────────────────┐  └────────────────┘│
│                    │  Oracle Service   │                     │
│                    │  (Weather APIs)   │                     │
│                    └───────────────────┘                     │
└─────────────────────────────────────────────────────────────┘
```

---

## 🗺️ Guidewire Component Mapping

### PolicyCenter Equivalents

| Kavach AI Component | Guidewire PolicyCenter Entity | Description |
|---------------------|-------------------------------|-------------|
| `WorkerRegistration` | `Account` + `Contact` | Gig worker's profile |
| `PolicyCreate` | `Submission` | Policy application |
| `PolicyResponse` | `PolicyPeriod` | Active insurance policy |
| `POLICY_CONFIG` | Product Definition | Coverage terms & pricing |
| `calculate_premium()` | Rating Engine | Premium calculation |
| `PolicyTier` enum | Product/Coverage Type | Basic/Standard/Premium |

**Key Differences:**
- Guidewire: Complex underwriting workflow (Quote → Bind → Issuance)
- Kavach AI: Instant issuance (IoT-verified workers, parametric triggers)

---

### ClaimCenter Equivalents

| Kavach AI Component | Guidewire ClaimCenter Entity | Description |
|---------------------|------------------------------|-------------|
| `ClaimSegment` | `ClaimSegment` | Represents the incident/trigger |
| `Exposure` | `Exposure` | Coverage line with payout amount |
| `CheckReport` | `Payment/Check` | Payment instruction |
| `auto_adjudicate_claims()` | Automated Adjudication | Zero-Touch decisioning |
| `check_fraud_indicators()` | Business Rules | Pre-ML fraud checks |
| `FraudShield` (AI) | ML-based SIU | Special Investigations Unit |

**Workflow Comparison:**

**Traditional Guidewire ClaimCenter:**
```
FNOL → Assignment → Investigation → Adjudication → Payment
(3-7 days)
```

**Kavach AI Zero-Touch:**
```
Oracle Trigger → AI Fraud Check → Auto-Approve → Instant UPI
(< 5 minutes)
```

---

## 🧩 System Components

### 1. `app_logic.py` – Backend Core

**Purpose:** FastAPI application serving REST APIs

**Key Endpoints:**

| Endpoint | Method | Purpose | Guidewire Equivalent |
|----------|--------|---------|----------------------|
| `/workers/register` | POST | Onboard new worker | PolicyCenter Account Creation |
| `/policies` | POST | Issue policy | PolicyCenter Submission → Bind |
| `/policies/{id}` | GET | Retrieve policy | PolicyCenter Policy Inquiry |
| `/oracle/update` | POST | Update environmental data | External Data Integration |
| `/claims/auto-adjudicate` | POST | Process claims | ClaimCenter Automated Adjudication |
| `/dashboard/summary` | GET | Dashboard data | Custom BI/Analytics |

**Database Schema (In-Memory):**

```python
workers_db = {
    "WRK-12345678": {
        "worker_id": "WRK-12345678",
        "full_name": "Raj Kumar",
        "phone_number": "+919876543210",
        "zone": "Velachery",
        "upi_id": "raj.kumar@paytm"
    }
}

policies_db = {
    "POL-ABCD1234": {
        "policy_id": "POL-ABCD1234",
        "worker_id": "WRK-12345678",
        "tier": "Basic",
        "weekly_premium": 30.0,
        "status": "Active"
    }
}

claims_db = {
    "CLM-XYZ789AB": {
        "claim_id": "CLM-XYZ789AB",
        "policy_id": "POL-ABCD1234",
        "trigger_type": "Heavy Rain",
        "trigger_value": 65.0,
        "status": "Paid"
    }
}
```

**Production Note:** Replace in-memory dicts with PostgreSQL/MongoDB for persistence.

---

### 2. `ai_engine.py` – Intelligence Layer

**Components:**

#### A. DynamicPremiumModel (Random Forest Regressor)

**Purpose:** Adjust base premium (₹30) by ±₹5 based on risk

**Features:**
- `zone_risk_score` (8.5 for flood-prone Velachery, 4.2 for safe Adyar)
- `forecast_rain_sum_7d` (Predicted monsoon intensity)
- `forecast_temp_avg_7d` (Heatwave risk)
- `month` (Seasonal patterns: monsoon Oct-Dec)

**Training Data:** 1000 synthetic samples based on Chennai historical weather

**Example:**
```python
forecast = [
    {'rain_mm': 45, 'temp_c': 30},
    {'rain_mm': 60, 'temp_c': 29},
    # ... 5 more days
]

adjustment = model.predict_adjustment("Velachery", forecast)
# Output: +₹4.50 (high-risk zone + heavy forecast)

final_premium = 30 + 4.50 = ₹34.50/week
```

---

#### B. FraudShield (Isolation Forest)

**Purpose:** Detect "Ghost Fleet" attacks

**Attack Scenario:**
- Fraudster uses spoofed GPS to fake being in storm zone
- Device is actually stationary (not delivering)
- Submits claim immediately when rain threshold hit

**Detection Features:**
- `gps_variance_km`: How much device moved (legitimate: 5-15km, fraud: <0.5km)
- `avg_speed_kmh`: Average speed (legitimate: 10-20kmh, fraud: <2kmh)
- `sensor_consistency`: GPS vs. accelerometer match (fraud: mismatch)
- `claim_hour`: Time of claim (fraud: odd hours like 3 AM)

**Example:**
```python
# Legitimate claim
behavior = {
    'gps_variance_km': 8.5,
    'avg_speed_kmh': 15.0,
    'claim_hour': 19,
    'sensor_consistency': 0.85
}
# Result: fraud_score = 0.12 → APPROVE

# Fraudulent claim
fraud_behavior = {
    'gps_variance_km': 0.1,   # Stationary
    'avg_speed_kmh': 0.3,     # Not moving
    'claim_hour': 3,          # Suspicious hour
    'sensor_consistency': 0.25 # Sensors don't match
}
# Result: fraud_score = 0.89 → FLAGGED_FRAUD
```

---

### 3. `dashboard.html` – Mobile-First UI

**Design Principles:**
- **High-Contrast:** WCAG AAA compliance for outdoor visibility
- **Low-Resource:** Optimized for 3GB RAM devices (Redmi Note)
- **Bilingual:** English ⇄ Tamil toggle
- **Touch-Friendly:** 48px minimum tap targets

**Key UI Elements:**

1. **Protection Shield** (Visual Status)
   - 🟢 Green = Safe (no weather threats)
   - 🟡 Amber = High Risk (approaching threshold)
   - 🔵 Blue = Payout Processed (claim paid)

2. **Real-Time Ticker**
   - Rain (mm in 24hr)
   - Temperature (°C)
   - AQI (Air Quality Index)

3. **Dynamic Premium Display**
   - Weekly premium with AI adjustment
   - Risk level explanation

4. **Toast Notification**
   - Popup: "Parametric Trigger Hit! ₹800 sent to GPay"

**Technology:**
- Single-file HTML (no build step)
- Tailwind CSS (CDN)
- Lucide Icons (lightweight)
- Vanilla JavaScript (no frameworks)

---

### 4. `mock_data.json` – Test Scenarios

**5 Test Cases:**

1. **Cyclone Hit** – Heavy rain (125mm) → ₹800 payout
2. **Heatwave** – Extreme temp (42°C) → ₹1200 payout (Standard tier)
3. **Ghost Fleet** – Fraud detected → Claim rejected
4. **Low-Risk Discount** – Clear weather in Adyar → Premium reduced to ₹25.80
5. **System Healthy** – No triggers, normal operation

---

### 5. `simulation_script.py` – Automated Testing

**Purpose:** End-to-end validation of all components

**Test Flow:**
```
1. Register worker → POST /workers/register
2. Create policy → POST /policies
3. Test AI premium → ai_engine.calculate_dynamic_premium()
4. Update Oracle → POST /oracle/update
5. Test fraud → ai_engine.verify_claim_legitimacy()
6. Trigger claims → POST /claims/auto-adjudicate
7. Validate results → Assert expected outcomes
```

**Usage:**
```bash
# Run all scenarios
python simulation_script.py

# Run specific scenario
python simulation_script.py --scenario 3

# Verbose output
python simulation_script.py --verbose
```

---

## 🚀 Installation & Setup

### Prerequisites

- **Python 3.9+** ([Download](https://www.python.org/downloads/))
- **pip** (comes with Python)
- **Git** (optional, for version control)

### Step-by-Step Installation

```bash
# 1. Clone or download the project
cd kavach-ai

# 2. Create virtual environment
python -m venv venv

# 3. Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Verify installation
python --version  # Should be 3.9+
pip list          # Should show FastAPI, scikit-learn, etc.
```

---

## 🎮 Running the Application

### 1. Start the API Server

```bash
python app_logic.py
```

**Expected Output:**
```
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

**Access Points:**
- API Docs (Swagger): http://localhost:8000/api/docs
- Health Check: http://localhost:8000/

---

### 2. Open the Dashboard

Open `dashboard.html` in a browser:

```bash
# Option 1: Direct file open
# Navigate to project folder and double-click dashboard.html

# Option 2: Simple HTTP server (recommended)
python -m http.server 8080
# Then visit: http://localhost:8080/dashboard.html
```

**Dashboard Features:**
- Real-time environmental data
- AI-calculated premium
- Protection shield status
- Language toggle (English ⇄ Tamil)

---

### 3. Run Simulations

```bash
python simulation_script.py
```

**Expected Output:**
```
╔═══════════════════════════════════════════════════════════╗
║            KAVACH AI - SIMULATION TEST SUITE              ║
║          Guidewire DevTrails 2026 - Phase 2               ║
╚═══════════════════════════════════════════════════════════╝

[SYSTEM HEALTH CHECK]
✓ API is running at http://localhost:8000/api/v1

[SCENARIO 1: Cyclone Hit - Zero Touch Success]
...
 SCENARIO 1 PASSED ✓

[SIMULATION SUMMARY]
Total Scenarios: 5
Passed: 5
Failed: 0
Success Rate: 100.0%

 ALL TESTS PASSED ✓
```

---

## 📡 API Documentation

### Core Endpoints

#### 1. Worker Registration

```http
POST /api/v1/workers/register
Content-Type: application/json

{
  "full_name": "Raj Kumar",
  "phone_number": "+919876543210",
  "email": "raj.kumar@example.com",
  "aadhar_last4": "4567",
  "city": "Chennai",
  "zone": "Velachery",
  "gig_platform": "Swiggy",
  "upi_id": "raj.kumar@paytm"
}
```

**Response:**
```json
{
  "worker_id": "WRK-A1B2C3D4",
  "message": "Registration successful!",
  "verification_status": "Verified"
}
```

---

#### 2. Policy Creation

```http
POST /api/v1/policies
Content-Type: application/json

{
  "worker_id": "WRK-A1B2C3D4",
  "tier": "Basic",
  "duration_weeks": 4
}
```

**Response:**
```json
{
  "policy_id": "POL-X9Y8Z7W6",
  "worker_id": "WRK-A1B2C3D4",
  "tier": "Basic",
  "weekly_premium": 30.0,
  "total_premium": 120.0,
  "start_date": "2026-04-04T10:00:00",
  "end_date": "2026-05-02T10:00:00",
  "status": "Active"
}
```

---

#### 3. Oracle Update (Environmental Data)

```http
POST /api/v1/oracle/update
Content-Type: application/json

{
  "current": {
    "rain_mm_24hr": 65.0,
    "temperature_c": 32.0,
    "aqi": 95
  },
  "forecast": [
    {"rain_mm": 45, "temp_c": 30},
    {"rain_mm": 60, "temp_c": 29}
  ]
}
```

---

#### 4. Auto-Adjudicate Claims

```http
POST /api/v1/claims/auto-adjudicate
```

**Response:**
```json
{
  "status": "completed",
  "timestamp": "2026-04-04T14:30:00",
  "total_processed": 1,
  "claims": [
    {
      "claim_id": "CLM-F5E4D3C2",
      "status": "Paid",
      "amount": 800.0,
      "trigger": "Heavy Rain"
    }
  ]
}
```

---

## 🧪 Testing & Simulation

### Manual Testing Workflow

1. **Register Raj:**
```bash
curl -X POST http://localhost:8000/api/v1/workers/register \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Raj Kumar",
    "phone_number": "+919876543210",
    "aadhar_last4": "4567",
    "zone": "Velachery",
    "gig_platform": "Swiggy",
    "upi_id": "raj.kumar@paytm"
  }'
```

2. **Create Policy (use worker_id from step 1):**
```bash
curl -X POST http://localhost:8000/api/v1/policies \
  -H "Content-Type: application/json" \
  -d '{
    "worker_id": "WRK-XXXXXX",
    "tier": "Basic"
  }'
```

3. **Trigger Rain Event:**
```bash
curl -X POST http://localhost:8000/api/v1/oracle/update \
  -H "Content-Type: application/json" \
  -d '{
    "current": {"rain_mm_24hr": 65.0, "temperature_c": 32, "aqi": 95}
  }'
```

4. **Process Claims:**
```bash
curl -X POST http://localhost:8000/api/v1/claims/auto-adjudicate
```

5. **Check Results:**
```bash
curl http://localhost:8000/api/v1/claims
```

---

### Automated Test Suite

Run all scenarios:
```bash
python simulation_script.py
```

Expected outcomes:
- ✅ Scenario 1: Cyclone triggers ₹800 payout
- ✅ Scenario 2: Heatwave triggers ₹1200 payout (Standard)
- ✅ Scenario 3: Fraud detected and blocked
- ✅ Scenario 4: Premium discount for low risk
- ✅ Scenario 5: Normal operation, no triggers

---

## 🚢 Deployment Guide

### Production Deployment (AWS/Azure/GCP)

1. **Database Setup**
```bash
# Replace in-memory dicts with PostgreSQL
pip install psycopg2-binary sqlalchemy
```

2. **Environment Variables**
```bash
# .env file
DATABASE_URL=postgresql://user:pass@localhost/kavachdb
ORACLE_API_KEY=your_weather_api_key
UPI_GATEWAY_URL=https://payment-gateway.com
GUIDEWIRE_CLOUD_URL=https://your-instance.guidewire.com
```

3. **Production Server**
```bash
# Use Gunicorn instead of Uvicorn dev server
gunicorn app_logic:app -w 4 -k uvicorn.workers.UvicornWorker
```

4. **Nginx Reverse Proxy**
```nginx
server {
    listen 80;
    server_name kavachai.com;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

### Guidewire Cloud Integration

#### PolicyCenter Integration

1. **Install Guidewire Cloud SDK:**
```bash
pip install guidewire-cloud-sdk  # (Proprietary - contact Guidewire)
```

2. **Map Entities:**
```python
# Map Kavach Worker to Guidewire Account
guidewire_account = {
    "AccountNumber": worker["worker_id"],
    "AccountHolderContact": {
        "FirstName": worker["full_name"].split()[0],
        "LastName": worker["full_name"].split()[-1],
        "PrimaryPhone": worker["phone_number"]
    }
}
```

3. **Create Submission:**
```python
# Use Guidewire API
response = guidewire_client.create_submission(
    product_code="KavachBasic",
    effective_date=datetime.now(),
    account_number=worker["worker_id"]
)
```

---

#### ClaimCenter Integration

1. **Webhook Setup:**
```python
# Configure ClaimCenter to call Kavach AI on FNOL
@app.post("/webhooks/guidewire/fnol")
async def handle_fnol(claim_data: Dict):
    # Trigger auto-adjudication
    result = await auto_adjudicate_claims()
    
    # Update Guidewire ClaimCenter
    guidewire_client.update_claim(
        claim_number=claim_data["ClaimNumber"],
        status="Approved",
        payment_amount=800.0
    )
```

2. **Payment Integration:**
```python
# Use Guidewire Payment Gateway
guidewire_client.create_payment(
    check_number=check_id,
    payee=worker["upi_id"],
    amount=payout_amount,
    payment_method="UPI_INSTANT"
)
```

---

## 🗺️ Future Roadmap

### Phase 3: Advanced Features

1. **IoT Integration**
   - Real-time GPS tracking from delivery partner apps
   - Live accelerometer data for fraud prevention
   - Integration with Swiggy/Zomato APIs

2. **Enhanced AI Models**
   - LSTM for time-series weather prediction
   - Computer Vision for claim photo verification
   - NLP chatbot for policy queries (Tamil + English)

3. **Blockchain Integration**
   - Smart contracts for instant payouts
   - Immutable claim history
   - Transparent premium calculation

4. **Expanded Coverage**
   - Personal Accident (PA) insurance
   - Two-wheeler damage coverage
   - Medical expense reimbursement

5. **Multi-City Rollout**
   - Bengaluru (traffic congestion triggers)
   - Mumbai (monsoon + flooding)
   - Delhi (air quality + winter smog)

---

## 📞 Support & Contact

**Project Lead:** Kavach AI Team  
**Email:** support@kavachai.com  
**Documentation:** https://docs.kavachai.com  
**Guidewire DevTrails:** Phase 2 Submission

---

## 📄 License

MIT License - See LICENSE file for details

---

## 🙏 Acknowledgments

- **Guidewire Software:** For ClaimCenter and PolicyCenter architecture inspiration
- **Chennai Gig Workers:** For real-world insights on weather challenges
- **OpenWeatherMap & IMD:** For weather data APIs
- **scikit-learn Community:** For ML model frameworks

---

## 🏆 Guidewire DevTrails 2026 - Phase 2 Checklist

- [x] **Zero-Touch Claims:** Auto-adjudication implemented
- [x] **AI Premium Model:** Random Forest with ±₹5 adjustment
- [x] **Fraud Detection:** Isolation Forest (Ghost Fleet defense)
- [x] **Mobile Dashboard:** High-contrast UI for 3GB RAM devices
- [x] **Tamil Support:** Bilingual interface
- [x] **5 Test Scenarios:** All passing in `simulation_script.py`
- [x] **Guidewire Mapping:** Documented PolicyCenter & ClaimCenter equivalents
- [x] **Production-Ready:** FastAPI + ML models + comprehensive docs

---

**Ready for Guidewire DevTrails 2026 Judging! 🚀**
