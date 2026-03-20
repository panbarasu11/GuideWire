# AI-Powered Parametric Insurance for Gig Workers

Gig delivery workers are the backbone of the quick-commerce economy, yet they lack basic income protection against external disruptions like extreme weather or civic restrictions. This project builds an AI-powered parametric insurance platform that automatically monitors environmental conditions and triggers instant payouts for lost wages — no manual claims required.

---

## 1. Persona-Based Scenario & Application Workflow

### The Persona & Scenario

**Meet Raj (26): A Food Delivery Partner in Chennai.**

- **Daily reality:** Raj works 6 days a week for Zomato, earning roughly ₹5,000 weekly. He relies on daily earnings to cover rent, groceries, and his younger sister's school fees — there is no savings buffer.
- **Device context:** He owns a 3-year-old Redmi Note running Android 11, 3GB RAM. He uses mobile data almost exclusively — home Wi-Fi is unreliable. His battery typically hits 30% by 2 PM from navigation and hotspot use.
- **Trust profile:** Raj has never filed an insurance claim. His prior experience with financial products is limited to a Jan Dhan savings account and a failed microfinance loan. He is skeptical of platforms that ask for documents upfront and deeply distrusts fine-print exclusions. He will abandon an onboarding flow the moment it asks for anything he doesn't understand.
- **Language:** Comfortable in Tamil; reads basic English on UI labels but will not parse paragraph-length text in English.
- **The disruption:** A severe cyclone brings 70mm of rainfall to Chennai. Delivery platforms suspend services, streets flood. Raj loses 2 days of work and approximately ₹1,500 in wages.
- **The solution:** Because Raj is on our Standard plan, the system automatically detects the 70mm rainfall threshold in his delivery zone. Before the rain even stops, ₹800 is credited to his UPI wallet — covering his daily lost wage. He filed no paperwork. He received a single Tamil-language push notification: *"Cyclone alert payout sent — ₹800 credited."*

### Application Workflow

1. **Registration:** Worker signs up, verifies their delivery platform ID, and shares their primary working zone.
2. **AI Risk Profiling:** The system analyses historical weather and AQI data for their specific pin code to assign a risk score.
3. **Policy Activation:** Worker selects a weekly coverage plan and pays the micro-premium.
4. **Real-Time Monitoring:** Background APIs continuously track weather, traffic, and civic data in the worker's zone.
5. **Parametric Trigger:** If a specific environmental threshold is crossed (e.g., temperature hits 42°C), a claim is generated.
6. **Verification:** The system cross-references the worker's sensor, cell tower, and network data to confirm physical presence in the disruption zone.
7. **Instant Payout:** Funds are routed instantly via UPI or bank transfer.

---

## 2. Core Mechanics: Premiums, Triggers & Platform

### Weekly Premium Model & Liquidity Backing

Gig workers operate on weekly payout cycles, so annual premiums are unfeasible. We use a **Dynamic Weekly Premium Model** calculated at 1–2% of a worker's average weekly earnings.

**Actuarial basis:** Based on 5 years of IMD historical rainfall data for Chennai, heavy-rain disruption events (>60mm/24h) occur an average of 4–6 times per year in high-risk zones. With an average payout of ₹800 per claim and an assumed 35% claim participation rate among active subscribers (workers who are actually in-zone and working during the disruption), the expected annual payout per subscriber is approximately:

> 5 events × 0.35 participation × ₹800 = **₹1,400/year** (~₹27/week)

A ₹30/week Standard premium generates ~₹1,560/year in collected premium per subscriber, yielding a target loss ratio of approximately **90%** before reinsurance costs. The reinsurer absorbs tail risk above a **1-in-10-year loss threshold** — specifically, any single-event payout that exceeds 300% of the weekly premium pool. This structure follows the Swiss Re parametric reinsurance framework for micro-insurance programmes.

Crucially, parametric triggers like cyclones represent systemic risk — thousands of riders could claim simultaneously. To prevent the liquidity pool from collapsing, our decentralised escrow is backed by a traditional reinsurance partner (e.g., Swiss Re or a regional underwriter specialising in parametric risk). This ensures that even in a city-wide maximum payout event, the capital is guaranteed and instantly available.

| Plan | Weekly Premium | Coverage (Max Payout) |
|------|---------------|----------------------|
| Basic | ₹20 | ₹500 |
| Standard | ₹30 | ₹800 |
| Premium | ₹50 | ₹1,200 |

### Parametric Triggers

Payouts are deterministic and based entirely on objective third-party data.

| Disruption Event | Parametric Condition | Data Source |
|-----------------|---------------------|-------------|
| Heavy Rain / Flood | Rainfall > 60mm in 24h | OpenWeather API |
| Extreme Heat | Temperature > 42°C | OpenWeather API |
| Severe Pollution | AQI > 300 | AQI Data APIs |
| Civic Curfew | Government Alert Issued | News/Gov API Scrapers |

### Platform Justification: Mobile-First (PWA / React Native)

This platform must be mobile. Location tracking requires background GPS and sensor access to verify the worker is in the affected zone. It also enables push notifications for hazard alerts and seamless one-click premium payments via UPI (GPay, PhonePe). All UI text is rendered in the device's system language; Tamil and Hindi localisation is a launch requirement, not a roadmap item.

---

## 3. AI/ML Integration

AI is the brain of this platform, transforming it from a static insurance tool into a dynamic, risk-aware engine.

### Dynamic Premium Calculation (Predictive ML)

We use a **Random Forest Regressor** to compute personalised weekly risk scores that feed directly into premium adjustments.

**Input features (training set):**

| Feature | Description |
|---------|-------------|
| `rolling_7d_rainfall_mm` | 7-day cumulative rainfall for the worker's pin code |
| `forecast_rain_probability_7d` | IMD/OpenWeather 7-day probabilistic rainfall forecast |
| `historical_disruption_rate_zone` | Zone-level disruption frequency (last 3 years) |
| `current_aqi` | Real-time AQI reading for the zone |
| `season_indicator` | Monsoon / pre-monsoon / dry season categorical flag |
| `day_of_week` | Weekday vs. weekend (affects baseline earnings at risk) |
| `prior_claim_count_worker` | Worker's personal claim history (last 52 weeks) |
| `platform_suspension_history` | Historical frequency of Zomato/Swiggy suspensions in zone |

**Training labels:** Weekly payout events from simulated historical data (bootstrapped from IMD records and Zomato zone-suspension logs). The model is retrained monthly on a rolling 104-week window.

**Output:** A `risk_multiplier` (0.8–2.0×) applied to the base plan premium. The multiplier is capped at 2.0× to prevent predatory pricing during high-risk seasons and floored at 0.8× to reward low-risk zones. Pricing changes are communicated to the worker 7 days in advance with a plain-language explanation.

### Fraud Detection (Anomaly Detection)

To prevent exploitation, an **Isolation Forest** model analyses claim patterns at the time of trigger. It flags anomalies across two dimensions:

- **Velocity checks:** Movement pattern inconsistent with a vehicle in active delivery (e.g., stationary for >45 minutes during a claimed disruption window).
- **Network clustering:** Multiple claims from devices sharing IP subnets, WiFi fingerprints, or exhibiting zero gyroscope variance — indicative of emulator or spoofing syndicate activity.

---

## 4. Adversarial Defense & Anti-Spoofing Strategy

### The Market Crash Scenario

Simple GPS verification is insufficient. A sophisticated syndicate of 500 delivery workers exploited a beta platform by organising via Telegram and using GPS-spoofing applications to fake their locations. While resting safely at home, they tricked the system into triggering mass false payouts for red-alert weather zones, instantly draining the liquidity pool.

To protect our platform and outsmart these syndicates without draining users' phone batteries, we rely on a **3-pillar defence system**.

---

### Pillar 1: Dynamic AI Work Signatures

To differentiate between a genuinely stranded delivery partner and a bad actor spoofing their location, our AI relies on "Work Signatures" via Activity Correlation.

**Battery-safe implementation:** Continuous sensor polling would kill a gig worker's battery. Instead, our app records basic GPS every 15 minutes. Heavy sensor fusion (accelerometer and gyroscope) is only activated when the local weather API flags a High-Risk Alert for the worker's zone.

**Verification logic:** Once active, the AI verifies physical reality. A legitimate gig worker in a storm has a movement pattern consistent with riding a bike — characteristic vibration, lean angles, stop-and-start traffic signatures. Static devices or perfect linear movements generated by spoofing apps are flagged immediately.

---

### Pillar 2: Defeating Coordinated Fraud Rings

Beyond basic GPS, the system analyses specific data points to detect organised fraud:

- **Sensor fusion verification:** Cross-reference Cell Tower IDs and WiFi SSID fingerprints against reported latitude/longitude.
- **Hardware attestation:** Google Play Integrity API (Android) and DeviceCheck (iOS) confirm the app is running on a genuine, unrooted device, blocking emulators designed to inject fake location data.
- **Syndicate clustering:** If multiple claims trigger simultaneously from devices sharing IP subnets, overlapping WiFi fingerprints, or exhibiting zero gyroscope variance, the AI flags it as a coordinated attack.

---

### Pillar 3: Protecting Honest Workers — The False Positive & Appeals Flow

The anti-fraud system is only as good as its ability to protect legitimate claimants. Severe storms knock out cell towers, causing honest workers to appear offline or stationary. **A flagged claim is never a rejected claim.**

**Soft-flag workflow:**

1. If a claim cannot be immediately verified (connectivity loss, ambiguous sensor data), it moves to an asynchronous **"Pending Verification"** queue. The instant payout is paused — not denied.
2. The worker receives a push notification: *"Your claim is being verified — funds will arrive within 24 hours if confirmed."*

**Secondary resolution (zero-dependency):** Rather than relying on Swiggy/Zomato APIs (which often go offline during extreme weather), the app uses **secure local caching**. During a network drop, the app encrypts and caches accelerometer and cell-tower telemetry locally. Once the worker reconnects, the app automatically uploads this payload — proving physical presence during the disruption, clearing the flag, and releasing the funds.

**Human review escalation:** Claims that remain unresolved after automated secondary verification are escalated to a human reviewer within 48 hours. Workers can also initiate a manual appeal via a single in-app button, which submits their cached telemetry alongside a free-text description. Target resolution: 72 hours. Workers are not penalised (no premium increase, no claim history mark) for claims that are flagged and subsequently cleared.

**Isolation Forest false positive rate:** Our target false positive rate is <2% of valid claims. This is monitored monthly; if it exceeds 3% in any rolling 4-week window, the detection thresholds are automatically loosened and flagged for model retraining.

---

## 5. Tech Stack & Development Plan

### Technology Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React Native (Mobile App) / Tailwind CSS |
| Backend | Python (FastAPI) |
| Database | PostgreSQL (User & Policy data) + MongoDB (Event & API logs) |
| AI/ML | Python, Scikit-learn, Pandas, NumPy |
| APIs | OpenWeatherMap, Google Maps API, Local AQI providers |
| Payments | Razorpay UPI API |
| Cloud | AWS EC2 / Firebase (Auth & Push Notifications) |
| Attestation | Google Play Integrity API (Android), DeviceCheck (iOS) |

### Development Plan

- **Weeks 1–2 (Foundation):** User authentication, database schemas, Maps API integration, Tamil/Hindi i18n setup.
- **Weeks 3–4 (The Oracle & AI):** Continuous background polling for weather APIs. Train Random Forest on historical IMD data. Build Isolation Forest baseline with simulated fraud vectors.
- **Weeks 5–6 (Triggers & Payments):** Parametric smart-trigger logic. Razorpay integration for premium collection and automated UPI claim payouts. Soft-flag queue and local caching fallback.

---

## 6. Future Roadmap & Relevance

To scale, this platform will eventually aim for **B2B2C integration** directly with delivery aggregators. Instead of Raj buying the policy individually, platforms like Swiggy could integrate our API to offer parametric insurance as a built-in perk. By subsidising the ₹30 premium directly from their weekly platform ledger, aggregators can retain their top-performing "Star" riders and build immense loyalty — ensuring their fleet feels protected no matter what disruptions occur.

A secondary roadmap item is **multi-peril bundling**: combining weather, AQI, and civic curfew triggers into a single unified policy, reducing per-peril pricing overhead and increasing weekly coverage value for the worker.
