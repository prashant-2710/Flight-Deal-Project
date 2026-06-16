# ✈️ Flight Deal Automation System

A robust, data-driven flight search automation system that monitors flight prices from a departure hub to various global destinations. Built around a clean, modular object-oriented architecture, this application bridges multiple APIs to check prices daily, execute fallback strategy logic, and instantly notify a database of club subscribers via automated SMS and bulk email blasts when prices drop below specified thresholds.

---

## 🚀 System Architecture & Workflow

The system is split across specialized modules to maximize separation of concerns:

1. **`main.py`**: The central engine orchestrating runtime execution. It sets dates, initiates the destination scan, tracks thresholds, and triggers notifications.
2. **`data_manager.py`**: Interacts with the **Sheety API** to pull destination requirements and user registration databases from a synchronized Google Sheet. It also writes price changes back to the sheet.
3. **`flight_search.py`**: Manages downstream communication with **SerpAPI's Google Flights Engine**, processing low-level criteria dynamically.
4. **`flight_data.py`**: Standardizes search responses into clean Python objects, isolates pricing metrics, and maps layout legs to count layover stops.
5. **`notification_manager.py`**: The notification broker. It dispatches immediate SMS alerts via **Twilio** and handles bulk email broad-casts via **SMTPlib (TLS encrypted)** utilizing customized formatting.
