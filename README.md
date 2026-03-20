# AI-Powered Parametric Insurance for Gig Workers

Gig delivery workers are the backbone of the quick-commerce economy, yet they lack basic income protection against external disruptions like extreme weather or civic restrictions. This project builds an AI-powered parametric insurance platform that automatically monitors environmental conditions and triggers instant payouts for lost wages—no manual claims required.

## 1. Persona-Based Scenario & Application Workflow

**The Persona & Scenario**
* **Meet Raj (26):** A Food Delivery Partner in Chennai.
* **The Baseline:** Raj works 6 days a week for Zomato, earning roughly ₹5,000 weekly. He relies on daily earnings to support his family.
* **The Disruption:** A severe cyclone brings 70mm of rainfall to Chennai. Delivery platforms suspend services, and streets flood. Raj loses 2 days of work and approximately ₹1,500 in wages.
* **The Solution:** Because Raj is subscribed to our "Standard" plan, the system automatically detects the 70mm rainfall threshold in his delivery zone. Before the rain even stops, ₹800 is instantly credited to his UPI wallet to cover his daily lost wage. He filed no paperwork.

**Application Workflow**
1.  **Registration:** Worker signs up, verifies their delivery platform ID, and shares their primary working zone.
2.  **AI Risk Profiling:** The system analyzes historical weather and AQI data for their specific pin code to assign a risk score.
3.  **Policy Activation:** Worker selects a weekly coverage plan and pays the micro-premium.
4.  **Real-Time Monitoring:** Background APIs continuously track weather, traffic, and civic data in the worker's zone.
5.  **Parametric Trigger:** If a specific environmental threshold is crossed (e.g., Temperature hits 42°C), a claim is generated.
6.  **Verification:** The system pings the worker's hardware and network data to confirm they are in the affected disruption zone.
7.  **Instant Payout:** Funds are routed instantly via UPI or bank transfer.

---

## 2. Core Mechanics: Premiums, Triggers & Platform

**Weekly Premium Model & Liquidity Backing**
Gig workers operate on weekly payout cycles, so annual premiums are unfeasible. We use a Dynamic Weekly Premium Model calculated at 1% to 2% of a worker's average weekly earnings. 

Crucially, parametric triggers like cyclones represent *systemic risk*—meaning thousands of riders could claim simultaneously. To prevent the liquidity pool from collapsing, our decentralized escrow is backed by a traditional Reinsurance partner (e.g., Swiss Re or a regional underwriter specializing in parametric risk). This ensures that even in a city-wide maximum payout event, the capital is guaranteed and instantly available.

| Plan | Weekly Premium | Coverage (Max Payout) |
| :--- | :--- | :--- |
| Basic | ₹20 | ₹500 |
| Standard | ₹30 | ₹800 |
| Premium | ₹50 | ₹1,200 |

**Parametric Triggers**
Payouts are deterministic and based entirely on objective third-party data.

| Disruption Event | Parametric Condition | Data Source |
| :--- | :--- | :--- |
| Heavy Rain / Flood | Rainfall > 60mm in 24h | OpenWeather API |
| Extreme Heat | Temperature > 42°C | OpenWeather API |
| Severe Pollution | AQI > 300 | AQI Data APIs |
| Civic Curfew | Government Alert Issued | News/Gov API Scrapers |

**Platform Justification: Mobile-First (PWA / React Native)**
This platform must be Mobile. Location tracking requires background GPS and sensor access to verify the worker is in the affected zone. Furthermore, it enables Push Notifications for hazard alerts and seamless one-click premium payments via UPI (GPay, PhonePe).

---

## 3. AI/ML Integration

AI is the brain of this platform, transforming it from a static insurance tool into a dynamic, risk-aware engine.

* **Dynamic Premium Calculation (Predictive ML):** We use a **Random Forest Regressor** to ingest historical local weather data, seasonal trends, and current forecasts. If the model predicts an 80% chance of monsoon floods next week in Chennai, Raj's premium dynamically adjusts to account for the heightened risk probability.
* **Fraud Detection (Anomaly Detection):** To prevent exploitation, an **Isolation Forest** model analyzes claim patterns. It flags anomalies such as velocity checks (ensuring movement consistent with a vehicle) and network clustering (detecting coordinated syndicate attacks).

---

## 4. Adversarial Defense & Anti-Spoofing Strategy

*Market Crash Scenario Pivot: Simple GPS verification is officially obsolete. Recently, a sophisticated syndicate of 500 delivery workers exploited a beta platform by organizing via Telegram and using advanced GPS-spoofing applications to fake their locations. While resting safely at home, they tricked the system into triggering mass false payouts for red-alert weather zones, instantly draining the liquidity pool.*

To protect our platform and outsmart these syndicates without draining our users' phone batteries, we rely on a robust 3-pillar defense system:

**1. The Differentiation: Dynamic AI Work Signatures**
To differentiate between a genuinely stranded delivery partner and a bad actor spoofing their location, our AI relies on "Work Signatures" via Activity Correlation. 
* *The Battery-Safe Implementation:* Continuous sensor polling would kill a gig worker's battery. Instead, our app only records basic GPS every 15 minutes. Heavy sensor fusion (Accelerometer and Gyroscope) is *only* activated dynamically when the local weather API flags a "High-Risk Alert" for their zone. 
* *The Verification:* Once active, the AI verifies the physical reality of the user. A legitimate gig worker in a storm has a movement pattern consistent with riding a bike (vibration, lean angles, stop-and-start traffic). Static devices resting at home or perfect, linear simulated movements generated by spoofing apps are flagged immediately as bots.

**2. The Data: Defeating Coordinated Fraud Rings**
Beyond basic GPS coordinates, our system analyzes specific data points to detect a coordinated fraud ring:
* **Sensor Fusion Verification:** We cross-reference Cell Tower IDs and WiFi SSID fingerprints against the reported latitude/longitude.
* **Hardware Attestation:** We utilize Google Play Integrity API (Android) and DeviceCheck (iOS) to ensure the app is running on a genuine, unrooted device, preventing the use of emulators designed to inject fake location data.
* **Syndicate Clustering:** If multiple claims trigger simultaneously from devices sharing similar IP subnets, overlapping WiFi fingerprints, or exhibiting zero gyroscope variance, the AI flags it as a coordinated Telegram syndicate attack.

**3. The UX Balance: Protecting the Honest Worker via Local Caching**
We must handle "flagged" claims without unfairly penalizing honest gig workers who might just be experiencing a genuine network drop in bad weather. 
* **The Soft-Flag Workflow:** Severe storms knock out cell towers. If a claim drops because the device loses connectivity, the claim is *not* rejected. Instead, the instant payout is paused, and the claim moves to an asynchronous "Pending Verification" queue.
* **Secondary Resolution (Zero-Dependency):** Instead of relying on Swiggy/Zomato APIs (which often go offline during extreme weather anyway), our app relies on secure local caching. During a network drop, the app encrypts and caches the accelerometer and cell-tower telemetry locally on the device. Once the storm passes and the worker reconnects to Wi-Fi, the app automatically uploads this payload, proving they were physically out on their bike during the disruption, clearing the flag and releasing the funds.

---

## 5. Tech Stack & Development Plan

**Technology Stack**
* **Frontend:** React Native (Mobile App) / Tailwind CSS
* **Backend:** Python (FastAPI) for high-performance API handling
* **Database:** PostgreSQL (User & Policy data) + MongoDB (Event & API logs)
* **AI/ML:** Python, Scikit-learn, Pandas, NumPy
* **APIs:** OpenWeatherMap, Google Maps API, Local AQI providers
* **Payments:** Razorpay UPI API
* **Cloud:** AWS EC2 / Firebase (Auth & Push Notifications)

**Development Plan**
* **Weeks 1-2 (Foundation):** Setup user authentication, database schemas, and Maps API integration.
* **Weeks 3-4 (The Oracle & AI):** Build continuous background polling for Weather APIs. Train predictive ML models for pricing and Isolation Forest for anti-spoofing.
* **Weeks 5-6 (Triggers & Payments):** Write parametric smart-trigger logic. Integrate Razorpay for premium collection and automated UPI claim payouts.

---

## 6. Future Roadmap & Relevance

To scale, this platform will eventually aim for B2B2C integration directly with delivery aggregators. Instead of Raj buying the policy individually, platforms like Swiggy could integrate our API to offer this parametric insurance as a built-in perk. By subsidizing the ₹30 premium directly from their weekly platform ledger, aggregators can retain their top-performing "Star" riders and build immense loyalty, ensuring their fleet feels protected no matter what disruptions occur.
