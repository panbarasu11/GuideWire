# Kavach AI 
**AI-Powered Parametric Insurance for India's Gig Economy**
*Protect Every Kilometre, Every Rupee*

Kavach AI is a parametric insurance platform designed specifically for the food delivery segment (e.g., Zomato, Swiggy). It protects gig workers from lost wages due to disruptions like extreme weather, social curfews, and platform outages. The system features automated claim-to-payout processing, ensuring zero manual steps and delivering UPI payouts within 90 seconds.

---

## 🚀 Key Features

* **Instant Onboarding:** Workers register in under 3 minutes via a WhatsApp-style flow, utilizing Aadhaar OTP, liveness checks, and facial hashing.
* **Automated Parametric Triggers:** System monitors real-time sensors (weather APIs, traffic feeds, curfew signals) 24/7.
* **Dynamic Premium Engine:** Utilizes Gradient Boosted Trees (GBT/XGBoost) trained on 3-year hyper-local data to dynamically adjust premiums (±₹5-15/week) based on zone risk score, worker history, and seasonal patterns.
* **Instant Payout System:** Validates claims across 5 data sources and initiates Razorpay/UPI sandbox transfers to the worker's VPA in under 90 seconds.
* **Intelligent Dashboards:** Provides a PWA-enabled worker view for earnings protection, and an Insurer/Admin view to track loss ratios, total payouts, and high-risk zone forecasts.

---

## 🛡️ Weekly Pricing & Coverage Plans

The platform uses a weekly subscription model that auto-renews every Monday.

* **Basic Shield (₹29/week):** Coverage of ₹500/day for up to 3 disruption days.
* **Pro Shield (₹49/week) - *Most Popular*:** Coverage of ₹800/day for up to 5 disruption days.
* **Max Shield (₹79/week):** Coverage of ₹1,200/day for up to 7 disruption days.

---

## ⛈️ Supported Triggers (Income-Loss Detection)

Claims are auto-initiated when the following parametric thresholds are breached:

* **Heavy Rainfall:** Rainfall > 15mm/hr for 45+ minutes (Trigger Level 1).
* **Extreme Heat:** Temperature > 44°C for 3+ hours (Trigger Level 1).
* **Flood / Waterlogging:** IMD Orange/Red alert active in the worker's zone (Trigger Level 2).
* **Severe Air Quality:** AQI > 350 (Severe) for 4+ hours (Trigger Level 1).
* **Curfew / Bandh:** Government-issued curfew active in the worker district (Trigger Level 2).
* **Local Zone Strike:** Verified market closure and <30% order fulfillment (Trigger Level 1).
* **App Outage:** Platform API downtime > 45 minutes during peak hours (Trigger Level 1).

---

## 🛑 Advanced Fraud Detection Layers

Kavach AI maintains a target fraud rate of <0.8% and a 94% Straight-Through Processing (STP) rate.

* **GPS Spoofing:** Analyzes worker GPS trails against cell tower data and accelerometer signatures, using anomaly detection on movement velocity to flag spoofing with 97% accuracy.
* **Fake Weather Claims:** Cross-validates claim times and locations against IMD, OpenWeather, satellite imagery, hyperlocal stations, and nearby work activity patterns.
* **Duplicate / Syndicate Fraud:** Maps worker claim clusters using a Graph Neural Network to detect coordinated fake claim rings.
* **Identity Checks:** Uses Aadhaar OTP + liveness check + facial hash at onboarding. Re-verification is triggered if the device fingerprint or GPS baseline shifts significantly.

---

## 💻 Technology Stack

**Frontend**
* Mobile App: React Native
* Admin Portal: Next.js, Tailwind CSS, PWA-enabled

**Backend & Infra**
* Core APIs: Node.js / Express
* Real-time Triggers: GraphQL, WebSockets
* Infrastructure: AWS (EC2 + Lambda + S3), GitHub Actions CI/CD
* Databases: PostgreSQL + PostGIS, Redis (trigger cache)

**AI & ML Microservices**
* Framework: FastAPI (Python)
* Models: scikit-learn, XGBoost (premium pricing), Isolation Forest & LSTM (anomaly/fraud), ARIMA (forecasting)

**Data & Payment Integrations**
* Data APIs: IMD Data Feed, OpenWeatherMap, Google Maps Platform, H3 Geospatial Grid
* Payments (Sandbox): Razorpay Test Mode, Stripe Sandbox, UPI (NPCI Simulator), PhonePe Sandbox, Aadhaar eKYC API (mock)
