from flask import Flask, request, jsonify
from datetime import datetime, timedelta
import threading
import time

app = Flask(__name__)

# In-memory log store: { service_name: [ { "timestamp": datetime, "message": str }, ... ] }
logs = {}
logs_lock = threading.Lock()

def cleanup_logs():
    """
    Background thread that runs every minute and removes logs older than 1 hour.
    """
    while True:
        time.sleep(60)
        cutoff = datetime.utcnow() - timedelta(hours=1)
        with logs_lock:
            for service in list(logs.keys()):
                logs[service] = [log for log in logs[service] if log['timestamp'] >= cutoff]
                if not logs[service]:
                    del logs[service]

cleanup_thread = threading.Thread(target=cleanup_logs, daemon=True)
cleanup_thread.start()

@app.route('/logs', methods=['POST'])
def ingest_log():
    """
    Ingest a log entry via a POST request with a JSON payload.
    Expected payload:
    {
      "service_name": "auth-service",
      "timestamp": "2025-03-17T10:15:00Z",
      "message": "User login successful"
    }
    """
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Invalid JSON payload'}), 400

    service_name = data.get('service_name')
    timestamp_str = data.get('timestamp')
    message = data.get('message')

    if not (service_name and timestamp_str and message):
        return jsonify({'error': 'Missing fields in payload'}), 400

    try:
        if timestamp_str.endswith("Z"):
            timestamp_str = timestamp_str[:-1]
        log_time = datetime.fromisoformat(timestamp_str)
    except ValueError:
        return jsonify({'error': 'Invalid timestamp format. Use ISO 8601 format.'}), 400

    log_entry = {
        'timestamp': log_time,
        'message': message
    }

    with logs_lock:
        if service_name not in logs:
            logs[service_name] = []
        logs[service_name].append(log_entry)

    return jsonify({'status': 'Log ingested successfully'}), 200

@app.route('/logs', methods=['GET'])
def get_logs():
    """
    Retrieve logs for a given service between start and end timestamps.
    Example request:
      GET /logs?service=auth-service&start=2025-03-17T10:00:00Z&end=2025-03-17T10:30:00Z
    Response:
      [
         {"timestamp": "2025-03-17T10:05:00Z", "message": "User attempted login"},
         {"timestamp": "2025-03-17T10:15:00Z", "message": "User login successful"}
      ]
    """
    service = request.args.get('service')
    start_str = request.args.get('start')
    end_str = request.args.get('end')

    if not (service and start_str and end_str):
        return jsonify({'error': 'Missing query parameters: service, start, and end are required'}), 400

    try:
        if start_str.endswith("Z"):
            start_str = start_str[:-1]
        if end_str.endswith("Z"):
            end_str = end_str[:-1]
        start_time = datetime.fromisoformat(start_str)
        end_time = datetime.fromisoformat(end_str)
    except ValueError:
        return jsonify({'error': 'Invalid timestamp format in query parameters.'}), 400

    with logs_lock:
        service_logs = logs.get(service, [])
        filtered_logs = [log for log in service_logs if start_time <= log['timestamp'] <= end_time]
        filtered_logs.sort(key=lambda log: log['timestamp'])
        response_logs = [
            {'timestamp': log['timestamp'].isoformat() + 'Z', 'message': log['message']}
            for log in filtered_logs
        ]

    return jsonify(response_logs), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)
