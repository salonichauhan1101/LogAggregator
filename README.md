# LogAggregator

A Python-based **Distributed Log Aggregation Service** built with Flask.

This project provides REST APIs to ingest and query logs from multiple services, supports thread-safe concurrent access, auto-expiration of logs older than 1 hour, and ensures logs are returned in sorted order even if ingested out-of-order.


## 🚀 Features

- ✅ REST API for **log ingestion**
- ✅ REST API for **log querying**
- ✅ Logs stored **in memory** and auto-expire after 1 hour
- ✅ Handles **unordered log ingestion**
- ✅ **Thread-safe** using `threading.Lock`
- ✅ Auto-cleanup via background thread


## ⚙️ How to Run Locally

### 🔧 1. Install dependencies

Make sure you're in your virtual environment, then run:

pip install flask

2. Run the Flask app
python app.py
By default, it runs on http://127.0.0.1:5000

🛠️ API Endpoints
🔹 POST /logs
Ingest a new log entry.

✅ Example Request:

curl -X POST http://127.0.0.1:5000/logs \
     -H "Content-Type: application/json" \
     -d '{
           "service_name": "auth-service",
           "timestamp": "2025-03-17T10:15:00Z",
           "message": "User login successful"
         }'
✅ Sample Payload:
{
  "service_name": "auth-service",
  "timestamp": "2025-03-17T10:15:00Z",
  "message": "User login successful"
}

🔹 GET /logs
Query logs for a given service within a time range.

✅ Example Request:
curl "http://127.0.0.1:5000/logs?service=auth-service&start=2025-03-17T10:00:00Z&end=2025-03-17T10:30:00Z"
✅ Example Response:
[
  {
    "timestamp": "2025-03-17T10:15:00Z",
    "message": "User login successful"
  }
]
🧹 Log Expiry
A background thread runs every 60 seconds and removes logs older than 1 hour.

All logs are stored in memory in this format:

logs = {
  "service-name": [
    { "timestamp": datetime, "message": str },
    ...
  ]
}
📁 Project Structure
LogAggregator/
├── app.py            # Flask app with API endpoints
├── venv/             # Virtual environment (excluded in .gitignore)
├── .gitignore
└── README.md
