#!/usr/bin/env python3
"""
KAVACH AI - End-to-End Simulation Script
=========================================
Executes 5 test scenarios to validate:
1. Zero-Touch claims processing
2. AI dynamic premium calculation
3. Fraud detection (Ghost Fleet)
4. Low-risk premium discount
5. System health monitoring

Guidewire DevTrails 2026 - Phase 2 Demonstration

Usage:
    python simulation_script.py
    
    Optional flags:
    --api-url http://localhost:8000  (default)
    --scenario 1                     (run specific scenario)
    --verbose                        (detailed output)
"""

import json
import requests
import time
import sys
from typing import Dict, Any, List
from datetime import datetime, timedelta
from colorama import init, Fore, Back, Style
import argparse

# Initialize colorama for cross-platform colored output
init(autoreset=True)

# ============================================================================
# CONFIGURATION
# ============================================================================

API_BASE = "http://localhost:8000/api/v1"
MOCK_DATA_PATH = "mock_data.json"

# Test execution settings
DELAY_BETWEEN_TESTS = 2  # seconds
ORACLE_UPDATE_DELAY = 1   # seconds

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def print_header(text: str):
    """Print formatted section header"""
    print("\n" + "="*80)
    print(f"{Fore.CYAN}{Style.BRIGHT}{text.center(80)}")
    print("="*80 + "\n")

def print_success(text: str):
    """Print success message"""
    print(f"{Fore.GREEN}✓ {text}")

def print_error(text: str):
    """Print error message"""
    print(f"{Fore.RED}✗ {text}")

def print_warning(text: str):
    """Print warning message"""
    print(f"{Fore.YELLOW}⚠ {text}")

def print_info(text: str):
    """Print info message"""
    print(f"{Fore.BLUE}ℹ {text}")

def print_result(label: str, value: Any, highlight: bool = False):
    """Print labeled result"""
    color = Fore.YELLOW if highlight else Fore.WHITE
    print(f"  {Fore.CYAN}{label:30} {color}{value}")

# ============================================================================
# API INTERACTION FUNCTIONS
# ============================================================================

def check_api_health() -> bool:
    """Check if API is running"""
    try:
        response = requests.get(f"{API_BASE.replace('/api/v1', '')}/", timeout=5)
        if response.status_code == 200:
            print_success(f"API is running at {API_BASE}")
            return True
    except requests.exceptions.RequestException as e:
        print_error(f"API not reachable: {e}")
        print_warning("Please start the API server: python app_logic.py")
        return False
    return False

def register_worker(worker_data: Dict) -> str:
    """Register a worker and return worker_id"""
    try:
        response = requests.post(
            f"{API_BASE}/workers/register",
            json=worker_data,
            timeout=10
        )
        
        if response.status_code in [200, 201]:
            result = response.json()
            worker_id = result.get("worker_id")
            print_success(f"Worker registered: {worker_id}")
            return worker_id
        else:
            print_error(f"Registration failed: {response.text}")
            return None
    except Exception as e:
        print_error(f"Registration error: {e}")
        return None

def create_policy(worker_id: str, tier: str = "Basic") -> str:
    """Create a policy for worker"""
    try:
        policy_data = {
            "worker_id": worker_id,
            "tier": tier,
            "duration_weeks": 4
        }
        
        response = requests.post(
            f"{API_BASE}/policies",
            json=policy_data,
            timeout=10
        )
        
        if response.status_code == 201:
            result = response.json()
            policy_id = result.get("policy_id")
            print_success(f"Policy created: {policy_id} ({tier} tier)")
            print_result("Weekly Premium", f"₹{result.get('weekly_premium')}")
            return policy_id
        else:
            print_error(f"Policy creation failed: {response.text}")
            return None
    except Exception as e:
        print_error(f"Policy creation error: {e}")
        return None

def update_oracle(environmental_data: Dict):
    """Update Oracle with environmental data"""
    try:
        response = requests.post(
            f"{API_BASE}/oracle/update",
            json=environmental_data,
            timeout=10
        )
        
        if response.status_code == 200:
            conditions = environmental_data.get("current", {})
            print_info(f"Oracle updated: Rain={conditions.get('rain_mm_24hr')}mm, "
                      f"Temp={conditions.get('temperature_c')}°C, "
                      f"AQI={conditions.get('aqi')}")
            return True
        else:
            print_error(f"Oracle update failed: {response.text}")
            return False
    except Exception as e:
        print_error(f"Oracle update error: {e}")
        return False

def trigger_auto_adjudication() -> Dict:
    """Trigger auto-adjudication and return results"""
    try:
        response = requests.post(
            f"{API_BASE}/claims/auto-adjudicate",
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print_info(f"Auto-adjudication completed: {result.get('total_processed')} claims processed")
            return result
        else:
            print_error(f"Auto-adjudication failed: {response.text}")
            return {}
    except Exception as e:
        print_error(f"Auto-adjudication error: {e}")
        return {}

def get_claim_details(claim_id: str) -> Dict:
    """Get full claim details including exposure and payment"""
    try:
        response = requests.get(
            f"{API_BASE}/claims/{claim_id}",
            timeout=10
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            print_error(f"Failed to fetch claim details: {response.text}")
            return {}
    except Exception as e:
        print_error(f"Claim fetch error: {e}")
        return {}

# ============================================================================
# AI MODEL TESTING
# ============================================================================

def test_premium_model(zone: str, forecast: List[Dict]) -> Dict:
    """Test AI premium calculation (requires ai_engine.py)"""
    try:
        from ai_engine import KavachAIService
        
        ai_service = KavachAIService()
        ai_service.initialize()
        
        result = ai_service.calculate_dynamic_premium(zone, forecast)
        
        print_info("AI Premium Calculation:")
        print_result("Zone", zone)
        print_result("Base Premium", f"₹{result['base_premium']}")
        print_result("AI Adjustment", f"₹{result['ai_adjustment']:+.2f}", highlight=True)
        print_result("Final Premium", f"₹{result['final_premium']}", highlight=True)
        print_result("Risk Level", result['risk_level'])
        
        return result
    except ImportError:
        print_warning("ai_engine.py not available - skipping AI premium test")
        return {"base_premium": 30.0, "ai_adjustment": 0.0, "final_premium": 30.0, "risk_level": "Medium"}

def test_fraud_detection(behavior_data: Dict) -> Dict:
    """Test fraud detection model"""
    try:
        from ai_engine import KavachAIService
        
        ai_service = KavachAIService()
        ai_service.initialize()
        
        result = ai_service.verify_claim_legitimacy(behavior_data)
        
        print_info("Fraud Detection Analysis:")
        print_result("Fraud Detected", "YES" if result['is_fraud'] else "NO", 
                    highlight=result['is_fraud'])
        print_result("Fraud Score", f"{result['fraud_score']:.3f}", highlight=result['is_fraud'])
        print_result("Recommendation", result['recommendation'])
        print_result("Confidence", result['confidence'])
        
        if result['is_fraud']:
            print(f"\n  {Fore.RED}Explanation: {result['explanation']}")
        
        return result
    except ImportError:
        print_warning("ai_engine.py not available - skipping fraud detection")
        return {"is_fraud": False, "fraud_score": 0.0, "recommendation": "APPROVE", "confidence": "Low"}

# ============================================================================
# SCENARIO EXECUTION
# ============================================================================

def run_scenario(scenario_data: Dict, mock_data: Dict, verbose: bool = False):
    """Execute a single test scenario"""
    scenario_id = scenario_data["id"]
    scenario_name = scenario_data["name"]
    description = scenario_data["description"]
    
    print_header(f"SCENARIO {scenario_id}: {scenario_name}")
    print(f"{Fore.WHITE}{description}\n")
    
    # Step 1: Register worker (use Raj by default)
    worker_profile = mock_data["worker_profiles"]["raj"].copy()
    
    # Override zone if specified in scenario
    if "zone" in scenario_data:
        worker_profile["zone"] = scenario_data["zone"]
    
    print(f"{Fore.MAGENTA}[1] WORKER REGISTRATION")
    worker_id = register_worker(worker_profile)
    
    if not worker_id:
        print_error("Scenario aborted - worker registration failed")
        return False
    
    time.sleep(0.5)
    
    # Step 2: Create policy
    print(f"\n{Fore.MAGENTA}[2] POLICY CREATION")
    policy_tier = scenario_data.get("policy_tier", "Basic")
    policy_id = create_policy(worker_id, policy_tier)
    
    if not policy_id:
        print_error("Scenario aborted - policy creation failed")
        return False
    
    time.sleep(0.5)
    
    # Step 3: AI Premium Calculation
    print(f"\n{Fore.MAGENTA}[3] AI PREMIUM CALCULATION")
    forecast = scenario_data["environmental_data"]["forecast"]
    zone = worker_profile["zone"]
    premium_result = test_premium_model(zone, forecast)
    
    time.sleep(0.5)
    
    # Step 4: Update Oracle with environmental data
    print(f"\n{Fore.MAGENTA}[4] ORACLE SERVICE UPDATE")
    oracle_updated = update_oracle(scenario_data["environmental_data"])
    
    if not oracle_updated:
        print_warning("Oracle update failed, but continuing...")
    
    time.sleep(ORACLE_UPDATE_DELAY)
    
    # Step 5: Fraud Detection (if behavior data provided)
    if "worker_behavior" in scenario_data:
        print(f"\n{Fore.MAGENTA}[5] FRAUD DETECTION ANALYSIS")
        fraud_result = test_fraud_detection(scenario_data["worker_behavior"])
    else:
        fraud_result = {"is_fraud": False, "fraud_score": 0.0}
    
    time.sleep(0.5)
    
    # Step 6: Trigger Auto-Adjudication
    print(f"\n{Fore.MAGENTA}[6] ZERO-TOUCH CLAIMS ADJUDICATION")
    adjudication_result = trigger_auto_adjudication()
    
    # Step 7: Validate Results
    print(f"\n{Fore.MAGENTA}[7] RESULT VALIDATION")
    expected = scenario_data["expected_outcome"]
    
    claims_processed = adjudication_result.get("claims", [])
    
    # Validation checks
    validation_passed = True
    
    if expected["claim_status"] == "No_Trigger":
        if len(claims_processed) == 0:
            print_success("✓ Correctly identified no trigger condition")
        else:
            print_error("✗ Unexpected claim triggered")
            validation_passed = False
    else:
        if len(claims_processed) > 0:
            claim = claims_processed[0]
            
            # Check claim status
            if claim["status"] == expected["claim_status"]:
                print_success(f"✓ Claim status matches: {claim['status']}")
            else:
                print_error(f"✗ Claim status mismatch: Expected {expected['claim_status']}, Got {claim['status']}")
                validation_passed = False
            
            # Check payout amount (if approved)
            if claim["status"] == "Paid":
                if abs(claim["amount"] - expected["payout_amount"]) < 0.01:
                    print_success(f"✓ Payout amount correct: ₹{claim['amount']}")
                else:
                    print_error(f"✗ Payout mismatch: Expected ₹{expected['payout_amount']}, Got ₹{claim['amount']}")
                    validation_passed = False
            
            # Check fraud detection
            if expected["fraud_detected"]:
                if claim["status"] == "Flagged_Fraud":
                    print_success("✓ Fraud correctly detected and flagged")
                else:
                    print_error("✗ Fraud not detected")
                    validation_passed = False
        else:
            print_error("✗ No claims processed, but trigger expected")
            validation_passed = False
    
    # Final verdict
    print(f"\n{Fore.MAGENTA}{'='*80}")
    if validation_passed:
        print(f"{Back.GREEN}{Fore.BLACK} SCENARIO {scenario_id} PASSED ✓ {Style.RESET_ALL}")
    else:
        print(f"{Back.RED}{Fore.WHITE} SCENARIO {scenario_id} FAILED ✗ {Style.RESET_ALL}")
    print(f"{Fore.MAGENTA}{'='*80}\n")
    
    return validation_passed

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(description="Kavach AI Simulation Test Suite")
    parser.add_argument("--api-url", default="http://localhost:8000", help="API base URL")
    parser.add_argument("--scenario", type=int, help="Run specific scenario (1-5)")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    # Update API base URL
    global API_BASE
    API_BASE = f"{args.api_url}/api/v1"
    
    # Print banner
    print(f"\n{Fore.CYAN}{Style.BRIGHT}")
    print("╔═══════════════════════════════════════════════════════════════════════════════╗")
    print("║                        KAVACH AI - SIMULATION TEST SUITE                      ║")
    print("║                    Guidewire DevTrails 2026 - Phase 2                         ║")
    print("╚═══════════════════════════════════════════════════════════════════════════════╝")
    print(Style.RESET_ALL)
    
    # Check API health
    print_header("SYSTEM HEALTH CHECK")
    if not check_api_health():
        print_error("Cannot proceed without API server. Exiting.")
        sys.exit(1)
    
    time.sleep(1)
    
    # Load mock data
    print_header("LOADING TEST DATA")
    try:
        with open(MOCK_DATA_PATH, 'r') as f:
            mock_data = json.load(f)
        print_success(f"Loaded {len(mock_data['test_scenarios'])} test scenarios")
    except Exception as e:
        print_error(f"Failed to load mock_data.json: {e}")
        sys.exit(1)
    
    time.sleep(1)
    
    # Execute scenarios
    scenarios = mock_data["test_scenarios"]
    
    if args.scenario:
        # Run specific scenario
        scenario = next((s for s in scenarios if s["id"] == args.scenario), None)
        if scenario:
            results = [run_scenario(scenario, mock_data, args.verbose)]
        else:
            print_error(f"Scenario {args.scenario} not found")
            sys.exit(1)
    else:
        # Run all scenarios
        results = []
        for i, scenario in enumerate(scenarios, 1):
            result = run_scenario(scenario, mock_data, args.verbose)
            results.append(result)
            
            # Delay between scenarios
            if i < len(scenarios):
                time.sleep(DELAY_BETWEEN_TESTS)
    
    # Final summary
    print_header("SIMULATION SUMMARY")
    
    passed = sum(results)
    total = len(results)
    
    print_result("Total Scenarios", total)
    print_result("Passed", passed, highlight=True)
    print_result("Failed", total - passed, highlight=(total - passed > 0))
    print_result("Success Rate", f"{(passed/total)*100:.1f}%", highlight=True)
    
    if passed == total:
        print(f"\n{Back.GREEN}{Fore.BLACK} ALL TESTS PASSED ✓ {Style.RESET_ALL}")
        print(f"{Fore.GREEN}\nKavach AI is production-ready for Guidewire DevTrails 2026!")
    else:
        print(f"\n{Back.YELLOW}{Fore.BLACK} SOME TESTS FAILED ⚠ {Style.RESET_ALL}")
        print(f"{Fore.YELLOW}\nPlease review failed scenarios and debug.")
    
    print("\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Fore.YELLOW}Simulation interrupted by user. Exiting...")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Fore.RED}Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
