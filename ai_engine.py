"""
KAVACH AI - Intelligence Layer
================================
AI-powered Risk Assessment and Fraud Detection for Parametric Insurance.

Components:
1. DynamicPremiumModel - Random Forest Regressor for risk-based pricing
2. FraudShield - Isolation Forest for adversarial fraud detection

Guidewire Integration: Extends ClaimCenter with ML-driven decisioning.

Author: Kavach AI Team
Version: 2.0 (Guidewire DevTrails 2026 - Phase 2)
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, IsolationForest
from sklearn.preprocessing import LabelEncoder
from typing import Dict, List, Tuple, Optional
import logging
from datetime import datetime, timedelta
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("KavachAI.Intelligence")

# ============================================================================
# CONFIGURATION
# ============================================================================

# Chennai Risk Zones (Historical flood/heat data)
CHENNAI_ZONES = {
    "Velachery": {"risk_score": 8.5, "avg_rain_mm": 145, "flood_history": 12},
    "Tambaram": {"risk_score": 7.8, "avg_rain_mm": 132, "flood_history": 9},
    "Adyar": {"risk_score": 4.2, "avg_rain_mm": 98, "flood_history": 3},
    "T. Nagar": {"risk_score": 6.1, "avg_rain_mm": 115, "flood_history": 5},
    "Anna Nagar": {"risk_score": 5.3, "avg_rain_mm": 105, "flood_history": 4},
    "Mylapore": {"risk_score": 5.8, "avg_rain_mm": 110, "flood_history": 6},
    "Perungudi": {"risk_score": 8.2, "avg_rain_mm": 140, "flood_history": 10},
    "Sholinganallur": {"risk_score": 7.5, "avg_rain_mm": 128, "flood_history": 8}
}

# Base premium before AI adjustment
BASE_PREMIUM = 30.0  # ₹30/week

# AI adjustment range
AI_ADJUSTMENT_MIN = -5.0  # ₹5 discount for low-risk
AI_ADJUSTMENT_MAX = 5.0   # ₹5 surcharge for high-risk

# ============================================================================
# DYNAMIC PREMIUM MODEL (Random Forest Regressor)
# ============================================================================

class DynamicPremiumModel:
    """
    AI-Powered Premium Adjustment Engine.
    
    Purpose: Adjust base premium (±₹5) based on:
    - Historical risk zone data (e.g., Velachery flood-prone)
    - 7-day weather forecast (predicted rain/temp)
    - Seasonal patterns (monsoon vs. summer)
    - Worker's delivery zone
    
    Algorithm: Random Forest Regressor
    - Input Features: zone_risk_score, forecast_rain_sum, forecast_temp_avg, month, day_of_week
    - Output: premium_adjustment (-5.0 to +5.0)
    
    Guidewire Context: Extends PolicyCenter's rating engine with ML predictions.
    """
    
    def __init__(self):
        self.model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            min_samples_split=5,
            random_state=42
        )
        self.is_trained = False
        self.feature_names = [
            'zone_risk_score',
            'forecast_rain_sum_7d',
            'forecast_temp_avg_7d',
            'month',
            'day_of_week'
        ]
        logger.info("DynamicPremiumModel initialized")
    
    def generate_training_data(self, n_samples: int = 1000) -> Tuple[pd.DataFrame, np.ndarray]:
        """
        Generate synthetic training data based on Chennai historical patterns.
        
        In production, this would use:
        - 2+ years of actual policy data
        - Claim frequency by zone
        - Historical weather patterns
        - Payout ratios (loss ratio analysis)
        """
        np.random.seed(42)
        
        zones = list(CHENNAI_ZONES.keys())
        data = []
        
        for _ in range(n_samples):
            zone = np.random.choice(zones)
            zone_info = CHENNAI_ZONES[zone]
            
            # Simulate 7-day forecast
            month = np.random.randint(1, 13)
            
            # Monsoon months (Oct-Dec) have higher rain
            if month in [10, 11, 12]:
                forecast_rain = np.random.uniform(50, 200)
                forecast_temp = np.random.uniform(28, 35)
            # Summer (Mar-May)
            elif month in [3, 4, 5]:
                forecast_rain = np.random.uniform(0, 30)
                forecast_temp = np.random.uniform(35, 42)
            # Rest of year
            else:
                forecast_rain = np.random.uniform(10, 80)
                forecast_temp = np.random.uniform(30, 38)
            
            # Calculate target: premium adjustment
            # Logic: Higher risk = higher premium, approaching storm = higher premium
            risk_factor = zone_info["risk_score"] / 10.0  # Normalize to 0-1
            rain_factor = min(forecast_rain / 150.0, 1.0)  # Cap at 1
            temp_factor = max((forecast_temp - 38) / 4.0, 0)  # Heat stress
            
            # Combined adjustment
            adjustment = (risk_factor * 3.0 + rain_factor * 2.0 + temp_factor * 1.5) - 2.5
            adjustment = np.clip(adjustment, AI_ADJUSTMENT_MIN, AI_ADJUSTMENT_MAX)
            
            # Add some noise
            adjustment += np.random.normal(0, 0.5)
            adjustment = np.clip(adjustment, AI_ADJUSTMENT_MIN, AI_ADJUSTMENT_MAX)
            
            data.append({
                'zone_risk_score': zone_info["risk_score"],
                'forecast_rain_sum_7d': forecast_rain,
                'forecast_temp_avg_7d': forecast_temp,
                'month': month,
                'day_of_week': np.random.randint(0, 7),
                'premium_adjustment': round(adjustment, 2)
            })
        
        df = pd.DataFrame(data)
        X = df[self.feature_names]
        y = df['premium_adjustment'].values
        
        return X, y
    
    def train(self, X: Optional[pd.DataFrame] = None, y: Optional[np.ndarray] = None):
        """
        Train the premium model.
        If no data provided, generates synthetic training set.
        """
        if X is None or y is None:
            logger.info("Generating synthetic training data...")
            X, y = self.generate_training_data(n_samples=1000)
        
        logger.info(f"Training Random Forest on {len(X)} samples...")
        self.model.fit(X, y)
        self.is_trained = True
        
        # Calculate feature importance
        importances = self.model.feature_importances_
        feature_importance = dict(zip(self.feature_names, importances))
        logger.info(f"Feature Importance: {feature_importance}")
        
        return feature_importance
    
    def predict_adjustment(
        self,
        zone: str,
        forecast_7day: List[Dict],
        current_date: Optional[datetime] = None
    ) -> float:
        """
        Predict premium adjustment for a worker.
        
        Args:
            zone: Delivery zone (e.g., "Velachery")
            forecast_7day: List of forecast dicts with 'rain_mm' and 'temp_c'
            current_date: Date for seasonal context (default: now)
        
        Returns:
            Premium adjustment in ₹ (-5.0 to +5.0)
        """
        if not self.is_trained:
            logger.warning("Model not trained. Training with synthetic data...")
            self.train()
        
        if current_date is None:
            current_date = datetime.now()
        
        # Get zone risk score
        zone_info = CHENNAI_ZONES.get(zone, {"risk_score": 6.0})  # Default medium risk
        
        # Process forecast
        forecast_rain_sum = sum(day.get('rain_mm', 0) for day in forecast_7day)
        forecast_temps = [day.get('temp_c', 32) for day in forecast_7day if 'temp_c' in day]
        forecast_temp_avg = np.mean(forecast_temps) if forecast_temps else 32.0
        
        # Create feature vector
        features = pd.DataFrame([{
            'zone_risk_score': zone_info["risk_score"],
            'forecast_rain_sum_7d': forecast_rain_sum,
            'forecast_temp_avg_7d': forecast_temp_avg,
            'month': current_date.month,
            'day_of_week': current_date.weekday()
        }])
        
        # Predict
        adjustment = self.model.predict(features)[0]
        adjustment = np.clip(adjustment, AI_ADJUSTMENT_MIN, AI_ADJUSTMENT_MAX)
        
        logger.info(f"Premium adjustment for {zone}: ₹{adjustment:.2f}")
        return round(adjustment, 2)
    
    def get_base_premium(self) -> float:
        """Return base premium before adjustment"""
        return BASE_PREMIUM

# ============================================================================
# FRAUDSHIELD - ADVERSARIAL FRAUD DETECTION
# ============================================================================

class FraudShield:
    """
    AI-Powered Fraud Detection using Isolation Forest.
    
    Purpose: Detect "Ghost Fleet" attacks where fraudsters:
    - Spoof GPS coordinates to fake being in storm zones
    - Submit claims while actually stationary
    - Use sensor data manipulation
    
    Algorithm: Isolation Forest (Anomaly Detection)
    - Input Features: gps_variance, speed_pattern, claim_timing, sensor_consistency
    - Output: fraud_score (0-1), is_fraud (boolean)
    
    Guidewire Context: Pre-check before ClaimCenter payment approval.
    
    Example Attack Scenario:
    - Legitimate: Worker in Velachery during cyclone, moving 15km/hr avg
    - Fraudulent: "Worker" claims in Velachery, GPS shows 0km/hr for 6 hours
    """
    
    def __init__(self, contamination: float = 0.05):
        """
        Initialize Isolation Forest.
        
        Args:
            contamination: Expected fraud rate (5% = 0.05)
        """
        self.model = IsolationForest(
            n_estimators=100,
            contamination=contamination,
            random_state=42,
            max_samples='auto'
        )
        self.is_trained = False
        self.fraud_threshold = 0.6  # Anomaly score threshold
        
        self.feature_names = [
            'gps_variance_km',      # How much GPS moved during claim period
            'avg_speed_kmh',        # Average movement speed
            'speed_std_dev',        # Speed consistency
            'claim_hour',           # Time of day (fraud often at odd hours)
            'sensor_consistency',   # Mock: accelerometer vs. GPS match
            'time_to_claim_minutes' # How quickly claim filed after trigger
        ]
        logger.info("FraudShield initialized")
    
    def generate_training_data(self, n_samples: int = 1000) -> pd.DataFrame:
        """
        Generate synthetic training data:
        - 95% legitimate claims (workers actively delivering)
        - 5% fraudulent claims (stationary "ghost fleet")
        """
        np.random.seed(42)
        
        data = []
        n_fraud = int(n_samples * 0.05)
        n_legit = n_samples - n_fraud
        
        # Legitimate claims (active delivery workers)
        for _ in range(n_legit):
            data.append({
                'gps_variance_km': np.random.uniform(2.0, 15.0),  # Moved 2-15km
                'avg_speed_kmh': np.random.uniform(8.0, 25.0),    # Typical delivery speed
                'speed_std_dev': np.random.uniform(3.0, 8.0),     # Normal variance
                'claim_hour': np.random.choice([11, 12, 13, 18, 19, 20]),  # Peak hours
                'sensor_consistency': np.random.uniform(0.7, 1.0),  # Good match
                'time_to_claim_minutes': np.random.uniform(30, 180),  # Filed within 3hrs
                'is_fraud': 0
            })
        
        # Fraudulent claims (spoofed GPS, stationary)
        for _ in range(n_fraud):
            data.append({
                'gps_variance_km': np.random.uniform(0.0, 0.5),   # Barely moved
                'avg_speed_kmh': np.random.uniform(0.0, 2.0),     # Stationary
                'speed_std_dev': np.random.uniform(0.0, 1.0),     # Too consistent
                'claim_hour': np.random.choice([2, 3, 4, 23]),    # Odd hours
                'sensor_consistency': np.random.uniform(0.2, 0.5),  # Sensors don't match
                'time_to_claim_minutes': np.random.uniform(1, 20),  # Filed immediately
                'is_fraud': 1
            })
        
        df = pd.DataFrame(data)
        return df
    
    def train(self, X: Optional[pd.DataFrame] = None):
        """
        Train the fraud detection model.
        Uses only legitimate data (unsupervised learning).
        """
        if X is None:
            logger.info("Generating synthetic fraud training data...")
            df = self.generate_training_data(n_samples=1000)
            # Isolation Forest trains on normal data only
            X = df[df['is_fraud'] == 0][self.feature_names]
        
        logger.info(f"Training Isolation Forest on {len(X)} legitimate samples...")
        self.model.fit(X)
        self.is_trained = True
        logger.info("FraudShield training complete")
    
    def detect_fraud(self, claim_behavior: Dict) -> Tuple[bool, float, str]:
        """
        Analyze claim behavior for fraud indicators.
        
        Args:
            claim_behavior: Dict with keys matching feature_names
        
        Returns:
            (is_fraud, fraud_score, explanation)
        
        Example Input:
        {
            'gps_variance_km': 0.2,      # Barely moved
            'avg_speed_kmh': 0.5,        # Stationary
            'speed_std_dev': 0.1,
            'claim_hour': 3,             # 3 AM
            'sensor_consistency': 0.3,   # Accelerometer shows no movement
            'time_to_claim_minutes': 5   # Filed immediately
        }
        """
        if not self.is_trained:
            logger.warning("FraudShield not trained. Training with synthetic data...")
            self.train()
        
        # Create feature vector
        features = pd.DataFrame([{
            feat: claim_behavior.get(feat, 0)
            for feat in self.feature_names
        }])
        
        # Predict: -1 = outlier (fraud), 1 = inlier (legit)
        prediction = self.model.predict(features)[0]
        
        # Get anomaly score (lower = more anomalous)
        anomaly_score = self.model.score_samples(features)[0]
        
        # Convert to fraud probability (0-1 scale)
        # Isolation Forest scores are typically in range [-0.5, 0.5]
        # Normalize to 0-1 where 1 = high fraud risk
        fraud_score = 1.0 / (1.0 + np.exp(anomaly_score * 5))  # Sigmoid transform
        fraud_score = round(fraud_score, 3)
        
        is_fraud = fraud_score > self.fraud_threshold
        
        # Generate explanation
        explanation = self._explain_decision(claim_behavior, fraud_score, is_fraud)
        
        logger.info(f"Fraud analysis: Score={fraud_score}, Fraud={is_fraud}")
        return is_fraud, fraud_score, explanation
    
    def _explain_decision(self, behavior: Dict, score: float, is_fraud: bool) -> str:
        """
        Generate human-readable explanation for fraud decision.
        Guidewire: Audit trail for claim decisions.
        """
        if not is_fraud:
            return "Legitimate claim - normal delivery behavior pattern detected"
        
        red_flags = []
        
        if behavior.get('gps_variance_km', 0) < 1.0:
            red_flags.append("GPS shows minimal movement during storm")
        
        if behavior.get('avg_speed_kmh', 0) < 3.0:
            red_flags.append("Device appears stationary")
        
        if behavior.get('sensor_consistency', 1.0) < 0.5:
            red_flags.append("GPS and accelerometer data mismatch (possible spoofing)")
        
        if behavior.get('claim_hour', 12) in [0, 1, 2, 3, 4, 23]:
            red_flags.append("Claim filed during unusual hours")
        
        if behavior.get('time_to_claim_minutes', 60) < 10:
            red_flags.append("Suspiciously fast claim submission")
        
        explanation = f"FRAUD ALERT (Score: {score:.2f}): " + "; ".join(red_flags)
        return explanation

# ============================================================================
# INTEGRATED AI SERVICE
# ============================================================================

class KavachAIService:
    """
    Unified AI service combining premium and fraud models.
    Used by app_logic.py for intelligent decision-making.
    """
    
    def __init__(self):
        self.premium_model = DynamicPremiumModel()
        self.fraud_shield = FraudShield(contamination=0.05)
        logger.info("KavachAIService initialized")
    
    def initialize(self):
        """Train both models with synthetic data"""
        logger.info("Initializing AI models...")
        
        # Train premium model
        premium_importance = self.premium_model.train()
        logger.info(f"Premium model ready. Key features: {premium_importance}")
        
        # Train fraud shield
        self.fraud_shield.train()
        logger.info("Fraud shield ready")
        
        logger.info("✅ All AI models initialized successfully")
    
    def calculate_dynamic_premium(
        self,
        zone: str,
        forecast_7day: List[Dict]
    ) -> Dict[str, float]:
        """
        Calculate premium with AI adjustment.
        
        Returns:
            {
                'base_premium': 30.0,
                'ai_adjustment': -2.5,
                'final_premium': 27.5,
                'risk_level': 'Low'
            }
        """
        base = self.premium_model.get_base_premium()
        adjustment = self.premium_model.predict_adjustment(zone, forecast_7day)
        final = base + adjustment
        
        # Determine risk level
        if adjustment < -2:
            risk_level = "Low"
        elif adjustment > 2:
            risk_level = "High"
        else:
            risk_level = "Medium"
        
        return {
            'base_premium': base,
            'ai_adjustment': adjustment,
            'final_premium': round(final, 2),
            'risk_level': risk_level
        }
    
    def verify_claim_legitimacy(
        self,
        claim_behavior: Dict
    ) -> Dict[str, any]:
        """
        Run fraud detection on claim.
        
        Returns:
            {
                'is_fraud': False,
                'fraud_score': 0.23,
                'explanation': '...',
                'recommendation': 'APPROVE'
            }
        """
        is_fraud, score, explanation = self.fraud_shield.detect_fraud(claim_behavior)
        
        if is_fraud:
            recommendation = "REJECT - Manual review required"
        elif score > 0.4:
            recommendation = "HOLD - Additional verification recommended"
        else:
            recommendation = "APPROVE"
        
        return {
            'is_fraud': is_fraud,
            'fraud_score': score,
            'explanation': explanation,
            'recommendation': recommendation,
            'confidence': 'High' if score < 0.3 or score > 0.7 else 'Medium'
        }

# ============================================================================
# STANDALONE TESTING & DEMONSTRATION
# ============================================================================

if __name__ == "__main__":
    print("="*60)
    print("KAVACH AI - Intelligence Layer Demo")
    print("="*60)
    
    # Initialize service
    ai_service = KavachAIService()
    ai_service.initialize()
    
    print("\n" + "="*60)
    print("TEST 1: Dynamic Premium Calculation")
    print("="*60)
    
    # Scenario: Raj in Velachery during monsoon season
    forecast_monsoon = [
        {'rain_mm': 45, 'temp_c': 30},
        {'rain_mm': 60, 'temp_c': 29},
        {'rain_mm': 75, 'temp_c': 28},
        {'rain_mm': 55, 'temp_c': 30},
        {'rain_mm': 40, 'temp_c': 31},
        {'rain_mm': 50, 'temp_c': 30},
        {'rain_mm': 65, 'temp_c': 29}
    ]
    
    result = ai_service.calculate_dynamic_premium("Velachery", forecast_monsoon)
    print(f"\n📍 Zone: Velachery (High-Risk, Flood-Prone)")
    print(f"📅 Season: Monsoon (Heavy Rain Forecast)")
    print(f"💰 Base Premium: ₹{result['base_premium']}")
    print(f"🤖 AI Adjustment: ₹{result['ai_adjustment']:+.2f}")
    print(f"✅ Final Premium: ₹{result['final_premium']}")
    print(f"⚠️  Risk Level: {result['risk_level']}")
    
    # Scenario: Raj in Adyar during summer
    forecast_summer = [
        {'rain_mm': 0, 'temp_c': 38},
        {'rain_mm': 2, 'temp_c': 39},
        {'rain_mm': 0, 'temp_c': 40},
        {'rain_mm': 1, 'temp_c': 38},
        {'rain_mm': 0, 'temp_c': 37},
        {'rain_mm': 3, 'temp_c': 39},
        {'rain_mm': 0, 'temp_c': 38}
    ]
    
    result2 = ai_service.calculate_dynamic_premium("Adyar", forecast_summer)
    print(f"\n📍 Zone: Adyar (Low-Risk)")
    print(f"📅 Season: Summer (Low Rain, Moderate Heat)")
    print(f"💰 Base Premium: ₹{result2['base_premium']}")
    print(f"🤖 AI Adjustment: ₹{result2['ai_adjustment']:+.2f}")
    print(f"✅ Final Premium: ₹{result2['final_premium']}")
    print(f"⚠️  Risk Level: {result2['risk_level']}")
    
    print("\n" + "="*60)
    print("TEST 2: Fraud Detection (Ghost Fleet Attack)")
    print("="*60)
    
    # Legitimate claim: Active delivery during storm
    legit_claim = {
        'gps_variance_km': 8.5,      # Moved 8.5km during shift
        'avg_speed_kmh': 15.0,       # Normal delivery speed
        'speed_std_dev': 4.2,        # Normal variance
        'claim_hour': 19,            # 7 PM (peak hours)
        'sensor_consistency': 0.85,  # GPS and sensors match
        'time_to_claim_minutes': 90  # Filed 1.5hrs after trigger
    }
    
    result3 = ai_service.verify_claim_legitimacy(legit_claim)
    print("\n🚴 Legitimate Claim: Raj actively delivering during rain")
    print(f"Fraud Score: {result3['fraud_score']:.3f}")
    print(f"Decision: {result3['recommendation']}")
    print(f"Explanation: {result3['explanation']}")
    
    # Fraudulent claim: Stationary device, spoofed GPS
    fraud_claim = {
        'gps_variance_km': 0.1,      # Barely moved
        'avg_speed_kmh': 0.3,        # Stationary
        'speed_std_dev': 0.05,       # Too consistent
        'claim_hour': 3,             # 3 AM (suspicious)
        'sensor_consistency': 0.25,  # Sensors don't match GPS
        'time_to_claim_minutes': 3   # Filed immediately
    }
    
    result4 = ai_service.verify_claim_legitimacy(fraud_claim)
    print("\n🚨 Fraudulent Claim: Ghost Fleet (Spoofed GPS)")
    print(f"Fraud Score: {result4['fraud_score']:.3f}")
    print(f"Decision: {result4['recommendation']}")
    print(f"Explanation: {result4['explanation']}")
    
    print("\n" + "="*60)
    print("AI Models Ready for Production Integration")
    print("="*60)
