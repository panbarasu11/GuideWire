"""
KAVACH AI - Backend Core Logic
===============================
A Guidewire-inspired parametric insurance platform for gig workers.
Implements Zero-Touch claims processing with AI-driven risk assessment.

Architecture Philosophy: Configuration over Coding, Separation of Concerns
Mirrors Guidewire PolicyCenter & ClaimCenter design patterns.

Author: Kavach AI Team
Version: 2.0 (Guidewire DevTrails 2026 - Phase 2)
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from enum import Enum
import uuid
import logging
from collections import defaultdict
import asyncio

# Configure logging (Guidewire-style structured logging)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(name)s] - %(levelname)s - %(message)s'
)
logger = logging.getLogger("KavachAI.Core")

# ============================================================================
# CONFIGURATION LAYER (Guidewire: Configuration over Coding)
# ============================================================================

class PolicyTier(str, Enum):
    """
    Enumeration for Kavach Policy Tiers.
    Maps to Guidewire PolicyCenter's Product Model.
    """
    BASIC = "Basic"
    STANDARD = "Standard"
    PREMIUM = "Premium"

class ClaimStatus(str, Enum):
    """
    Claim lifecycle states - mirrors Guidewire ClaimCenter workflow.
    """
    PENDING = "Pending"
    APPROVED = "Approved"
    REJECTED = "Rejected"
    PAID = "Paid"
    FLAGGED_FRAUD = "Flagged_Fraud"

class RiskZone(str, Enum):
    """
    Geographic risk classification for Chennai.
    Used by AI Engine for dynamic pricing.
    """
    LOW_RISK = "Low_Risk"      # Example: Adyar
    MEDIUM_RISK = "Medium_Risk"  # Example: T. Nagar
    HIGH_RISK = "High_Risk"    # Example: Velachery (flood-prone)

# Policy Configuration (Guidewire Product Definition)
POLICY_CONFIG = {
    PolicyTier.BASIC: {
        "base_premium": 30.0,      # ₹30/week
        "rain_threshold": 60.0,    # mm in 24hr
        "payout_amount": 800.0,    # ₹800
        "coverage_perils": ["Heavy Rain"],
        "max_payouts_per_month": 2
    },
    PolicyTier.STANDARD: {
        "base_premium": 50.0,
        "rain_threshold": 50.0,
        "temp_threshold": 40.0,    # °C heatwave
        "aqi_threshold": 250,      # Hazardous AQI
        "payout_amount": 1200.0,
        "coverage_perils": ["Heavy Rain", "Heatwave", "Air Pollution"],
        "max_payouts_per_month": 4
    },
    PolicyTier.PREMIUM: {
        "base_premium": 75.0,
        "rain_threshold": 40.0,
        "temp_threshold": 38.0,
        "aqi_threshold": 200,
        "payout_amount": 1800.0,
        "coverage_perils": ["Heavy Rain", "Heatwave", "Air Pollution", "Cyclone"],
        "max_payouts_per_month": 6,
        "personal_accident_cover": 50000.0  # ₹50,000 PA
    }
}

# ============================================================================
# DATA MODELS (Guidewire Entity Definitions)
# ============================================================================

class WorkerRegistration(BaseModel):
    """
    Gig Worker Onboarding Entity.
    Maps to Guidewire PolicyCenter Account/Contact.
    """
    full_name: str = Field(..., min_length=2, max_length=100)
    phone_number: str = Field(..., regex=r'^\+91[6-9]\d{9}$')
    email: Optional[EmailStr] = None
    aadhar_last4: str = Field(..., regex=r'^\d{4}$', description="Last 4 digits of Aadhaar")
    city: str = Field(default="Chennai")
    zone: RiskZone = Field(default=RiskZone.MEDIUM_RISK)
    gig_platform: str = Field(..., description="Swiggy, Zomato, Dunzo, etc.")
    upi_id: str = Field(..., regex=r'^[\w.-]+@[\w.-]+$')
    
    class Config:
        schema_extra = {
            "example": {
                "full_name": "Raj Kumar",
                "phone_number": "+919876543210",
                "email": "raj.kumar@example.com",
                "aadhar_last4": "4567",
                "city": "Chennai",
                "zone": "Medium_Risk",
                "gig_platform": "Swiggy",
                "upi_id": "raj.kumar@paytm"
            }
        }

class PolicyCreate(BaseModel):
    """
    Policy Issuance Request.
    Maps to Guidewire PolicyCenter Submission.
    """
    worker_id: str
    tier: PolicyTier
    start_date: Optional[datetime] = None
    duration_weeks: int = Field(default=4, ge=1, le=52)
    
class PolicyResponse(BaseModel):
    """
    Active Policy Record - Guidewire Policy Entity.
    """
    policy_id: str
    worker_id: str
    tier: PolicyTier
    weekly_premium: float
    total_premium: float
    start_date: datetime
    end_date: datetime
    status: str
    coverage_details: Dict[str, Any]
    created_at: datetime

class ClaimSegment(BaseModel):
    """
    Guidewire ClaimCenter: ClaimSegment (Line of Business).
    Represents a parametric trigger event.
    """
    claim_id: str
    policy_id: str
    worker_id: str
    trigger_type: str  # "Heavy Rain", "Heatwave", "AQI Spike"
    trigger_value: float
    threshold_breached: float
    timestamp: datetime
    location: Dict[str, float]  # {"lat": 13.0827, "lon": 80.2707}
    
class Exposure(BaseModel):
    """
    Guidewire ClaimCenter: Exposure (Coverage Line).
    Represents the financial impact of a claim.
    """
    exposure_id: str
    claim_id: str
    coverage_type: str
    payout_amount: float
    reserve_amount: float
    status: ClaimStatus

class CheckReport(BaseModel):
    """
    Guidewire ClaimCenter: Payment Check.
    Represents the payout instruction.
    """
    check_id: str
    exposure_id: str
    payee_upi: str
    amount: float
    payment_method: str = "UPI"
    status: str
    issued_at: datetime

# ============================================================================
# IN-MEMORY DATA STORES (Guidewire DB Layer Simulation)
# ============================================================================

# Simulates Guidewire PolicyCenter Database
workers_db: Dict[str, Dict] = {}
policies_db: Dict[str, Dict] = {}

# Simulates Guidewire ClaimCenter Database
claims_db: Dict[str, Dict] = {}
exposures_db: Dict[str, Dict] = {}
checks_db: Dict[str, Dict] = {}

# Oracle Service State (Real-time Environmental Data)
oracle_state = {
    "last_update": None,
    "current_conditions": {
        "rain_mm_24hr": 0.0,
        "temperature_c": 32.0,
        "aqi": 95,
        "wind_speed_kmh": 15.0
    },
    "forecast_7day": []
}

# ============================================================================
# FASTAPI APPLICATION INITIALIZATION
# ============================================================================

app = FastAPI(
    title="Kavach AI - Parametric Insurance API",
    description="Guidewire-inspired Zero-Touch claims for gig workers",
    version="2.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS Configuration (Production: Restrict to specific origins)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# BUSINESS LOGIC LAYER
# ============================================================================

def generate_id(prefix: str) -> str:
    """Generate Guidewire-style entity IDs (e.g., POL-12345678)"""
    return f"{prefix}-{str(uuid.uuid4())[:8].upper()}"

def calculate_premium(tier: PolicyTier, zone: RiskZone, ai_adjustment: float = 0.0) -> float:
    """
    Premium Calculation Engine.
    Base premium + AI dynamic adjustment (±₹5).
    
    In production, this would call ai_engine.py's DynamicPremiumModel.
    """
    base = POLICY_CONFIG[tier]["base_premium"]
    # Zone multiplier
    zone_factor = {
        RiskZone.LOW_RISK: 0.9,
        RiskZone.MEDIUM_RISK: 1.0,
        RiskZone.HIGH_RISK: 1.15
    }
    adjusted = base * zone_factor[zone] + ai_adjustment
    return round(adjusted, 2)

async def verify_worker_identity(aadhar_last4: str) -> bool:
    """
    Mock ID Verification Service.
    In production: Integrate with DigiLocker/UIDAI eKYC.
    """
    # Simulate async API call
    await asyncio.sleep(0.1)
    # Simple validation: reject if all same digit (e.g., "0000")
    return len(set(aadhar_last4)) > 1

def check_fraud_indicators(claim_data: Dict, policy_data: Dict) -> tuple[bool, str]:
    """
    Pre-check before invoking AI FraudShield.
    Guidewire: Business Rules before ML model.
    
    Returns: (is_suspicious, reason)
    """
    # Rule 1: Check if GPS location is within Chennai bounds
    lat, lon = claim_data["location"]["lat"], claim_data["location"]["lon"]
    if not (12.8 <= lat <= 13.3 and 80.1 <= lon <= 80.4):
        return True, "Location outside Chennai service area"
    
    # Rule 2: Check claim frequency (anti-abuse)
    worker_claims = [c for c in claims_db.values() 
                     if c["worker_id"] == policy_data["worker_id"]]
    month_claims = [c for c in worker_claims 
                    if (datetime.now() - c["timestamp"]).days <= 30]
    
    max_allowed = POLICY_CONFIG[policy_data["tier"]]["max_payouts_per_month"]
    if len(month_claims) >= max_allowed:
        return True, f"Monthly payout limit reached ({max_allowed})"
    
    return False, "Passed pre-checks"

# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.get("/")
async def health_check():
    """API Health Check - Guidewire System Status Endpoint"""
    return {
        "status": "operational",
        "service": "Kavach AI Core",
        "version": "2.0.0",
        "timestamp": datetime.now().isoformat(),
        "components": {
            "policy_center": "UP",
            "claim_center": "UP",
            "oracle_service": "UP" if oracle_state["last_update"] else "INITIALIZING"
        }
    }

@app.post("/api/v1/workers/register", status_code=201)
async def register_worker(worker: WorkerRegistration):
    """
    Worker Onboarding Endpoint.
    Guidewire PolicyCenter: Account Creation.
    
    Flow:
    1. Validate input data
    2. Mock ID verification (Aadhaar)
    3. Create worker account
    4. Return worker_id for policy issuance
    """
    logger.info(f"Registration attempt: {worker.full_name}, Phone: {worker.phone_number}")
    
    # ID Verification (Mock DigiLocker integration)
    is_verified = await verify_worker_identity(worker.aadhar_last4)
    if not is_verified:
        logger.warning(f"ID verification failed for {worker.phone_number}")
        raise HTTPException(
            status_code=400,
            detail="Aadhaar verification failed. Please check last 4 digits."
        )
    
    # Check for duplicate phone number
    for w_id, w_data in workers_db.items():
        if w_data["phone_number"] == worker.phone_number:
            logger.info(f"Returning existing worker: {w_id}")
            return {
                "worker_id": w_id,
                "message": "Worker already registered",
                "existing": True
            }
    
    # Create new worker account
    worker_id = generate_id("WRK")
    workers_db[worker_id] = {
        **worker.dict(),
        "worker_id": worker_id,
        "registration_date": datetime.now(),
        "verification_status": "Verified",
        "total_policies": 0
    }
    
    logger.info(f"Worker registered successfully: {worker_id}")
    return {
        "worker_id": worker_id,
        "message": "Registration successful! You can now purchase a Kavach policy.",
        "verification_status": "Verified",
        "next_step": "POST /api/v1/policies to activate coverage"
    }

@app.post("/api/v1/policies", status_code=201)
async def create_policy(policy_req: PolicyCreate):
    """
    Policy Issuance Endpoint.
    Guidewire PolicyCenter: Submission → Quote → Bind.
    
    Flow:
    1. Validate worker exists
    2. Calculate premium (base + AI adjustment)
    3. Create policy record
    4. Activate coverage
    """
    # Validate worker
    if policy_req.worker_id not in workers_db:
        raise HTTPException(status_code=404, detail="Worker not found. Please register first.")
    
    worker = workers_db[policy_req.worker_id]
    
    # Calculate premium (in production, call ai_engine.DynamicPremiumModel)
    # For now, use simple calculation
    weekly_premium = calculate_premium(
        tier=policy_req.tier,
        zone=RiskZone(worker["zone"]),
        ai_adjustment=0.0  # Will be replaced by AI model
    )
    
    total_premium = weekly_premium * policy_req.duration_weeks
    
    # Generate policy
    policy_id = generate_id("POL")
    start_date = policy_req.start_date or datetime.now()
    end_date = start_date + timedelta(weeks=policy_req.duration_weeks)
    
    policy_data = {
        "policy_id": policy_id,
        "worker_id": policy_req.worker_id,
        "tier": policy_req.tier,
        "weekly_premium": weekly_premium,
        "total_premium": total_premium,
        "start_date": start_date,
        "end_date": end_date,
        "status": "Active",
        "coverage_details": POLICY_CONFIG[policy_req.tier],
        "created_at": datetime.now(),
        "claims_count": 0
    }
    
    policies_db[policy_id] = policy_data
    workers_db[policy_req.worker_id]["total_policies"] += 1
    
    logger.info(f"Policy issued: {policy_id} for worker {policy_req.worker_id}")
    
    return PolicyResponse(**policy_data)

@app.get("/api/v1/policies/{policy_id}")
async def get_policy(policy_id: str):
    """Retrieve Policy Details - Guidewire PolicyCenter Query"""
    if policy_id not in policies_db:
        raise HTTPException(status_code=404, detail="Policy not found")
    return policies_db[policy_id]

@app.get("/api/v1/workers/{worker_id}/policies")
async def get_worker_policies(worker_id: str):
    """Get all policies for a worker"""
    if worker_id not in workers_db:
        raise HTTPException(status_code=404, detail="Worker not found")
    
    worker_policies = [p for p in policies_db.values() if p["worker_id"] == worker_id]
    return {
        "worker_id": worker_id,
        "total_policies": len(worker_policies),
        "policies": worker_policies
    }

@app.put("/api/v1/policies/{policy_id}/cancel")
async def cancel_policy(policy_id: str):
    """Policy Cancellation - Guidewire PolicyCenter Cancel Transaction"""
    if policy_id not in policies_db:
        raise HTTPException(status_code=404, detail="Policy not found")
    
    policy = policies_db[policy_id]
    if policy["status"] == "Cancelled":
        return {"message": "Policy already cancelled"}
    
    policy["status"] = "Cancelled"
    policy["cancelled_at"] = datetime.now()
    
    logger.info(f"Policy cancelled: {policy_id}")
    return {"message": "Policy cancelled successfully", "policy_id": policy_id}

# ============================================================================
# ORACLE SERVICE (Background Worker)
# ============================================================================

@app.post("/api/v1/oracle/update")
async def update_environmental_data(data: Dict[str, Any]):
    """
    Oracle Service: External API endpoint to update environmental conditions.
    In production, this would be called by a cron job polling:
    - OpenWeatherMap API (rain, temp, wind)
    - AQI API (air quality)
    - IMD (Indian Meteorological Department) for cyclone alerts
    
    Simulates: Guidewire's External Data Integration patterns.
    """
    oracle_state["last_update"] = datetime.now()
    oracle_state["current_conditions"].update(data.get("current", {}))
    oracle_state["forecast_7day"] = data.get("forecast", [])
    
    logger.info(f"Oracle updated: Rain={data.get('current', {}).get('rain_mm_24hr', 'N/A')}mm, "
                f"Temp={data.get('current', {}).get('temperature_c', 'N/A')}°C")
    
    return {
        "status": "updated",
        "timestamp": oracle_state["last_update"],
        "conditions": oracle_state["current_conditions"]
    }

@app.get("/api/v1/oracle/current")
async def get_current_conditions():
    """Get current environmental data for dashboard"""
    if not oracle_state["last_update"]:
        return {
            "status": "no_data",
            "message": "Oracle service initializing. Data will be available shortly."
        }
    
    return {
        "status": "active",
        "last_update": oracle_state["last_update"],
        "data": oracle_state["current_conditions"],
        "data_age_minutes": (datetime.now() - oracle_state["last_update"]).seconds // 60
    }

# ============================================================================
# ZERO-TOUCH CLAIMS ENGINE (Core Innovation)
# ============================================================================

@app.post("/api/v1/claims/auto-adjudicate")
async def auto_adjudicate_claims(background_tasks: BackgroundTasks):
    """
    Zero-Touch Claims Processor.
    Guidewire ClaimCenter: Automated Claims Adjudication.
    
    Workflow:
    1. Scan all active policies
    2. Check if environmental thresholds breached (Oracle data)
    3. Create ClaimSegment for each trigger
    4. Run fraud detection (ai_engine.FraudShield)
    5. Create Exposure and approve/reject
    6. Issue CheckReport for approved claims
    7. Update policy payout counter
    
    Runs as background task (cron: every 15 minutes in production).
    """
    logger.info("Starting auto-adjudication cycle...")
    
    if not oracle_state["last_update"]:
        return {"status": "skipped", "reason": "Oracle data not available"}
    
    conditions = oracle_state["current_conditions"]
    processed_claims = []
    
    # Scan active policies
    active_policies = [p for p in policies_db.values() 
                       if p["status"] == "Active" and p["end_date"] > datetime.now()]
    
    for policy in active_policies:
        tier_config = POLICY_CONFIG[policy["tier"]]
        worker = workers_db[policy["worker_id"]]
        
        # Check parametric triggers
        triggered = False
        trigger_type = None
        trigger_value = None
        threshold = None
        
        # Rain trigger
        if "Heavy Rain" in tier_config["coverage_perils"]:
            if conditions["rain_mm_24hr"] >= tier_config["rain_threshold"]:
                triggered = True
                trigger_type = "Heavy Rain"
                trigger_value = conditions["rain_mm_24hr"]
                threshold = tier_config["rain_threshold"]
        
        # Heatwave trigger (Standard/Premium only)
        if not triggered and "Heatwave" in tier_config.get("coverage_perils", []):
            if conditions["temperature_c"] >= tier_config.get("temp_threshold", 999):
                triggered = True
                trigger_type = "Heatwave"
                trigger_value = conditions["temperature_c"]
                threshold = tier_config["temp_threshold"]
        
        # AQI trigger (Standard/Premium only)
        if not triggered and "Air Pollution" in tier_config.get("coverage_perils", []):
            if conditions["aqi"] >= tier_config.get("aqi_threshold", 999):
                triggered = True
                trigger_type = "Air Pollution"
                trigger_value = conditions["aqi"]
                threshold = tier_config["aqi_threshold"]
        
        if not triggered:
            continue
        
        # Create Claim Segment
        claim_id = generate_id("CLM")
        claim_data = {
            "claim_id": claim_id,
            "policy_id": policy["policy_id"],
            "worker_id": policy["worker_id"],
            "trigger_type": trigger_type,
            "trigger_value": trigger_value,
            "threshold_breached": threshold,
            "timestamp": datetime.now(),
            "location": {"lat": 13.0827, "lon": 80.2707},  # Mock Chennai coords
            "status": ClaimStatus.PENDING
        }
        
        # Fraud Detection (Business Rules + AI)
        is_suspicious, fraud_reason = check_fraud_indicators(claim_data, policy)
        
        if is_suspicious:
            claim_data["status"] = ClaimStatus.FLAGGED_FRAUD
            claim_data["fraud_reason"] = fraud_reason
            claims_db[claim_id] = claim_data
            logger.warning(f"Claim {claim_id} flagged: {fraud_reason}")
            processed_claims.append({
                "claim_id": claim_id,
                "status": "Flagged_Fraud",
                "reason": fraud_reason
            })
            continue
        
        # Approve claim
        claim_data["status"] = ClaimStatus.APPROVED
        claims_db[claim_id] = claim_data
        
        # Create Exposure
        exposure_id = generate_id("EXP")
        payout_amount = tier_config["payout_amount"]
        exposure_data = {
            "exposure_id": exposure_id,
            "claim_id": claim_id,
            "coverage_type": trigger_type,
            "payout_amount": payout_amount,
            "reserve_amount": payout_amount,  # Guidewire reserves
            "status": ClaimStatus.APPROVED,
            "created_at": datetime.now()
        }
        exposures_db[exposure_id] = exposure_data
        
        # Issue Payment Check
        check_id = generate_id("CHK")
        check_data = {
            "check_id": check_id,
            "exposure_id": exposure_id,
            "payee_upi": worker["upi_id"],
            "amount": payout_amount,
            "payment_method": "UPI",
            "status": "Issued",
            "issued_at": datetime.now()
        }
        checks_db[check_id] = check_data
        
        # Update claim status to PAID
        claim_data["status"] = ClaimStatus.PAID
        claim_data["check_id"] = check_id
        
        # Update policy claims counter
        policy["claims_count"] += 1
        
        logger.info(f"✅ Claim {claim_id} processed: ₹{payout_amount} to {worker['upi_id']}")
        processed_claims.append({
            "claim_id": claim_id,
            "status": "Paid",
            "amount": payout_amount,
            "trigger": trigger_type
        })
    
    return {
        "status": "completed",
        "timestamp": datetime.now(),
        "total_processed": len(processed_claims),
        "claims": processed_claims
    }

@app.get("/api/v1/claims")
async def get_all_claims():
    """Retrieve all claims - Guidewire ClaimCenter Search"""
    return {
        "total_claims": len(claims_db),
        "claims": list(claims_db.values())
    }

@app.get("/api/v1/claims/{claim_id}")
async def get_claim_details(claim_id: str):
    """Get detailed claim information including exposure and payment"""
    if claim_id not in claims_db:
        raise HTTPException(status_code=404, detail="Claim not found")
    
    claim = claims_db[claim_id]
    exposure = next((e for e in exposures_db.values() if e["claim_id"] == claim_id), None)
    check = None
    
    if exposure:
        check = next((c for c in checks_db.values() if c["exposure_id"] == exposure["exposure_id"]), None)
    
    return {
        "claim": claim,
        "exposure": exposure,
        "payment": check
    }

@app.get("/api/v1/workers/{worker_id}/claims")
async def get_worker_claims(worker_id: str):
    """Get all claims for a worker"""
    if worker_id not in workers_db:
        raise HTTPException(status_code=404, detail="Worker not found")
    
    worker_claims = [c for c in claims_db.values() if c["worker_id"] == worker_id]
    return {
        "worker_id": worker_id,
        "total_claims": len(worker_claims),
        "claims": worker_claims
    }

# ============================================================================
# DASHBOARD DATA AGGREGATION
# ============================================================================

@app.get("/api/v1/dashboard/summary")
async def get_dashboard_summary():
    """
    Aggregated dashboard data for frontend.
    Combines Oracle, Policy, and Claims data.
    """
    active_policies = [p for p in policies_db.values() if p["status"] == "Active"]
    recent_claims = sorted(
        claims_db.values(),
        key=lambda x: x["timestamp"],
        reverse=True
    )[:10]
    
    return {
        "system_status": "operational",
        "environmental": oracle_state["current_conditions"],
        "last_oracle_update": oracle_state["last_update"],
        "statistics": {
            "total_workers": len(workers_db),
            "active_policies": len(active_policies),
            "total_claims": len(claims_db),
            "approved_claims": len([c for c in claims_db.values() if c["status"] == ClaimStatus.PAID]),
            "flagged_fraud": len([c for c in claims_db.values() if c["status"] == ClaimStatus.FLAGGED_FRAUD])
        },
        "recent_claims": recent_claims
    }

@app.get("/api/v1/dashboard/worker/{worker_id}")
async def get_worker_dashboard(worker_id: str):
    """
    Personalized dashboard for specific worker (Raj).
    Shows: current policy, risk level, premium, recent claims.
    """
    if worker_id not in workers_db:
        raise HTTPException(status_code=404, detail="Worker not found")
    
    worker = workers_db[worker_id]
    active_policy = next(
        (p for p in policies_db.values() 
         if p["worker_id"] == worker_id and p["status"] == "Active"),
        None
    )
    
    worker_claims = [c for c in claims_db.values() if c["worker_id"] == worker_id]
    
    # Calculate risk level based on Oracle data
    conditions = oracle_state["current_conditions"]
    risk_level = "Safe"
    risk_color = "green"
    
    if active_policy:
        config = POLICY_CONFIG[active_policy["tier"]]
        if conditions["rain_mm_24hr"] >= config.get("rain_threshold", 999) * 0.8:
            risk_level = "High Risk"
            risk_color = "amber"
        elif conditions["temperature_c"] >= config.get("temp_threshold", 999) * 0.9:
            risk_level = "High Risk"
            risk_color = "amber"
        elif conditions["aqi"] >= config.get("aqi_threshold", 999) * 0.8:
            risk_level = "High Risk"
            risk_color = "amber"
    
    return {
        "worker": worker,
        "active_policy": active_policy,
        "current_conditions": oracle_state["current_conditions"],
        "risk_assessment": {
            "level": risk_level,
            "color": risk_color
        },
        "claims_history": worker_claims,
        "lifetime_payouts": sum(
            POLICY_CONFIG[c.get("policy_tier", "Basic")]["payout_amount"]
            for c in worker_claims
            if c["status"] == ClaimStatus.PAID
        )
    }

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting Kavach AI Core Server...")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
