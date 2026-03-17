# AI-Powered Parametric Insurance for Gig Workers

Gig delivery workers are the backbone of the quick-commerce economy, yet they lack basic income protection against external disruptions like extreme weather or civic restrictions. This project builds an AI-powered parametric insurance platform that automatically monitors environmental conditions and triggers instant payouts for lost wages—no manual claims required.

---

## 1. Persona-Based Scenario & Application Workflow

### The Persona & Scenario
**Meet Raj (26), a Food Delivery Partner in Chennai.**
* **The Baseline:** Raj works 6 days a week for Zomato, earning roughly ₹5,000 weekly. He relies on daily earnings to support his family.
* **The Disruption:** A severe cyclone brings 70mm of rainfall to Chennai. Delivery platforms suspend services, and streets flood. Raj loses 2 days of work and approximately ₹1,500 in wages.
* **The Solution:** Because Raj is subscribed to our "Standard" plan, the system automatically detects the 70mm rainfall threshold in his delivery zone. Before the rain even stops, ₹800 is instantly credited to his UPI wallet to cover his daily lost wage. He filed no paperwork.

### Application Workflow
1.  **Registration:** Worker signs up, verifies their delivery platform ID, and shares their primary working zone.
2.  **AI Risk Profiling:** The system analyzes historical weather and AQI data for their specific pin code to assign a risk score.
3.  **Policy Activation:** Worker selects a weekly coverage plan and pays the micro-premium.
4.  **Real-Time Monitoring:** Background APIs continuously track weather, traffic, and civic data in the worker's zone.
5.  **Parametric Trigger:** If a specific environmental threshold is crossed (e.g., Temperature hits 42°C), a claim is generated.
6.  **Verification:** The system pings the worker's GPS to confirm they are in the affected disruption zone.
7.  **Instant Payout:** Funds are routed instantly via UPI or bank transfer.

---

## 2. Core Mechanics: Premiums, Triggers & Platform

### Weekly Premium Model
Gig workers operate on weekly payout cycles, so annual premiums are unfeasible. We use a Dynamic Weekly Premium Model calculated at 1% to 2% of a worker's average weekly earnings.

| Plan | Weekly Premium | Coverage (Max Payout) |
| :--- | :--- | :--- |
| **Basic** | ₹20 | ₹500 |
| **Standard** | ₹30 | ₹800 |
| **Premium** | ₹50 | ₹1,200 |

### Parametric Triggers
Payouts are deterministic and based entirely on objective third-party data.

| Disruption Event | Parametric Condition | Data Source |
| :--- | :--- | :--- |
| **Heavy Rain / Flood** | Rainfall > 60mm in 24h | OpenWeather API |
| **Extreme Heat** | Temperature > 42°C | OpenWeather API |
| **Severe Pollution** | AQI > 300 | AQI Data APIs |
| **Civic Curfew** | Government Alert Issued | News/Gov API Scrapers |

### Platform Justification: Mobile-First (PWA / React Native)
This platform must be Mobile. Web-based dashboards are impractical for riders who live on their smartphones. A mobile application (or PWA) is chosen because:
* **Location Tracking:** We need background GPS access to verify the worker is actually in the affected zone when a trigger event occurs.
* **Push Notifications:** Instant alerts ("Hazardous weather detected. Your ₹800 payout has been triggered").
* **UPI Intent Flow:** Seamless one-click premium payments through phone-based UPI apps (GPay, PhonePe).

---

## 3. AI/ML Integration

AI is the brain of this platform, transforming it from a static insurance tool into a dynamic, risk-aware engine.

* **Dynamic Premium Calculation (Predictive ML):** We use a Random Forest Regressor to ingest historical local weather data, seasonal trends, and current forecasts. If the model predicts an 80% chance of monsoon floods next week in Chennai, Raj's premium dynamically adjusts from ₹30 to ₹35 to account for the heightened risk probability.
* **Fraud Detection (Anomaly Detection):** To prevent exploitation, an Isolation Forest model analyzes claim patterns. It flags anomalies such as:
    * **GPS Spoofing:** Sudden, impossible jumps in location (e.g., Chennai to Madurai in 5 minutes) just to claim a weather payout.
    * **Velocity Checks:** Ensuring the device shows movement consistent with a delivery vehicle before the disruption hit.

---

## 4. Tech Stack & Development Plan

### Technology Stack
* **Frontend:** React Native (Mobile App) / Tailwind CSS
* **Backend:** Python (FastAPI) for high-performance API handling
* **Database:** PostgreSQL (User & Policy data) + MongoDB (Event & API logs)
* **AI/ML:** Python, Scikit-learn, Pandas, NumPy
* **APIs:** OpenWeatherMap, Google Maps API, Local AQI providers
* **Payments:** Razorpay UPI API
* **Cloud:** AWS EC2 / Firebase (Auth & Push Notifications)

### Development Plan
* **Weeks 1-2 (Foundation):** Setup user authentication, database schemas, and Google Maps API integration for location tracking.
* **Weeks 3-4 (The Oracle & AI):** Build the continuous background polling for Weather/AQI APIs. Train and deploy the predictive ML models for dynamic pricing.
* **Weeks 5-6 (Triggers & Payments):** Write the parametric smart-trigger logic. Integrate Razorpay for premium collection and automated UPI claim payouts. Build worker dashboard.

---

## 5. Future Roadmap & Relevance
To scale, this platform will eventually aim for B2B2C integration directly with delivery aggregators. Instead of Raj buying the policy individually, platforms like Swiggy could integrate our API to offer this parametric insurance as a built-in perk to retain their top-performing "Star" riders, deducting the ₹30 premium directly from their weekly platform ledger.
