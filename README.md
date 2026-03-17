# 🛡️ AI-Powered Parametric Insurance for Gig Workers

![License](https://img.shields.io/badge/License-MIT-blue.svg)
![Python](https://img.shields.io/badge/Backend-Python_FastAPI-green.svg)
![React](https://img.shields.io/badge/Frontend-React.js-blue.svg)
![Machine Learning](https://img.shields.io/badge/AI-Scikit_Learn-orange.svg)

## 📌 Overview
Gig delivery workers in India (Swiggy, Zomato, Amazon, Zepto, etc.) depend heavily on daily earnings. When extreme weather (heavy rain, heatwaves), severe pollution, or curfews strike, their income halts. Traditional insurance doesn't cover this "lost time." 

This project is an **AI-powered parametric insurance platform** that automatically protects gig workers from income loss. Instead of filing manual claims, the system monitors environmental APIs and triggers **instant payouts** the moment predefined disruption thresholds are crossed.

---

## 🎯 The Problem & Persona
**Meet Raj (26), a Food Delivery Partner in Chennai:**
- **Earnings:** ₹4000–₹6000/week working 6 days.
- **Pain Point:** If heavy rain floods the streets, he loses ₹1000+ in a single day. 
- **The Solution:** Raj pays a micro-premium of ₹30/week. When rainfall exceeds 60mm in his zone, he automatically receives ₹800 directly to his UPI—no paperwork required.

---

## ✨ Core Features
- **⚡ Smart Parametric Triggers:** Payouts are automatically triggered based on real-time API data (Weather, AQI, Gov Alerts).
- **🧠 AI Risk Profiling & Dynamic Pricing:** Uses Machine Learning to predict risk levels based on location, weather history, and pollution data to adjust weekly premiums.
- **🛡️ Fraud Detection:** AI-driven anomaly detection to prevent GPS spoofing and duplicate claims.
- **💸 Instant UPI Payouts:** Zero wait time for claim processing.

---

## ⚙️ How It Works (The Workflow)
1. **Registration:** Worker signs up and selects a coverage plan.
2. **Risk Profiling:** AI analyzes historical data for their specific delivery zone.
3. **Continuous Monitoring:** Background workers constantly poll OpenWeather, AQI, and local alert APIs.
4. **Threshold Crossed:** E.g., Temperature hits 42°C.
5. **Instant Claim Processing:** The system verifies the worker's active location.
6. **Payout:** Compensation is instantly routed to the worker's wallet/bank.

---

## 📊 Subscription Plans & Triggers

### Weekly Micro-Premiums
| Plan | Weekly Premium | Coverage (Max Payout) |
| :--- | :--- | :--- |
| **Basic** | ₹20 | ₹500 |
| **Standard** | ₹30 | ₹800 |
| **Premium** | ₹50 | ₹1200 |

### Parametric Thresholds
| Event | Trigger Condition | Data Source |
| :--- | :--- | :--- |
| **Heavy Rain** | Rainfall > 60mm | OpenWeather API |
| **Extreme Heat** | Temperature > 42°C | OpenWeather API |
| **Pollution** | AQI > 300 | AQI API |
| **Curfew/Riot** | Government Alert Issued | News/Gov Data Feeds |

---

## 💻 Technology Stack

* **Frontend:** React.js, Tailwind CSS (Mobile-first)
* **Backend:** Python (FastAPI / Flask) or Node.js
* **AI / ML:** Python, Scikit-learn, Pandas, NumPy (Random Forest, Anomaly Detection)
* **Database:** PostgreSQL (Relational/Policies) + MongoDB (Event Logs)
* **APIs:** OpenWeather API, AQI API, Google Maps API
* **Payments:** Razorpay / Stripe (Sandbox)
* **Deployment:** AWS / Vercel / Firebase

---

## 🚀 Getting Started

### Prerequisites
- Node.js (v16+)
- Python (3.9+)
- API Keys for OpenWeather and Razorpay

### Installation
1. **Clone the repository:**
   ```bash
   git clone [https://github.com/yourusername/gig-parametric-insurance.git](https://github.com/yourusername/gig-parametric-insurance.git)
   cd gig-parametric-insurance
