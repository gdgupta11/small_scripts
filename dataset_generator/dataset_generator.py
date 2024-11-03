import random
import time
import uuid
from datetime import datetime
import json
from prometheus_client import Counter, Histogram, generate_latest
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

# Define the possible values for each field
LOG_LEVELS = ["INFO", "WARNING", "ERROR"]
USER_IDS = [f"user_{i}" for i in range(1, 101)]
IP_ADDRESSES = [f"192.168.1.{i}" for i in range(1, 101)]
REQUEST_METHODS = ["GET", "POST", "PUT", "DELETE"]
URL_PATHS = ["/home", "/login", "/logout", "/signup", "/products", "/cart", "/checkout"]
STATUS_CODES = [200, 201, 400, 401, 403, 404, 500]

# Add error messages and patterns
ERROR_PATTERNS = {
    "INFO": [
        "Request completed successfully",
        "User logged in successfully",
        "Cart updated",
        "Order processed"
    ],
    "WARNING": [
        "High response time detected",
        "Rate limit approaching",
        "Low memory warning",
        "Cache miss"
    ],
    "ERROR": [
        "Database connection failed",
        "Authentication failed",
        "Invalid request payload",
        "Internal server error"
    ]
}

# Define Prometheus metrics
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'path', 'status']
)

http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'path']
)

# Define a function to generate a single log entry
def generate_log():
    timestamp = time.time()
    level = random.choice(LOG_LEVELS)
    method = random.choice(REQUEST_METHODS)
    path = random.choice(URL_PATHS)
    status_code = random.choice(STATUS_CODES)
    response_time = random.uniform(0.05, 1.0)
    
    # Update Prometheus metrics
    http_requests_total.labels(
        method=method,
        path=path,
        status=str(status_code)
    ).inc()
    
    http_request_duration_seconds.labels(
        method=method,
        path=path
    ).observe(response_time)
    
    log_entry = {
        "timestamp": timestamp,
        "level": level,
        "user_id": random.choice(USER_IDS),
        "ip_address": random.choice(IP_ADDRESSES),
        "method": method,
        "url_path": path,
        "status_code": status_code,
        "response_time_ms": round(response_time * 1000, 2),
        "session_id": str(uuid.uuid4()),
        "message": random.choice(ERROR_PATTERNS[level])
    }
    return log_entry

# Generate logs continuously
def generate_logs(filename="web_app_logs.json", count=100, prometheus_port=8000):
    # Start Prometheus metrics endpoint
    metrics_server = HTTPServer(('localhost', prometheus_port), MetricsHandler)
    server_thread = threading.Thread(target=metrics_server.serve_forever)
    server_thread.daemon = True
    server_thread.start()
    
    # Generate logs
    with open(filename, "w") as f:
        try:
            for _ in range(count):
                log_entry = generate_log()
                f.write(json.dumps(log_entry) + "\n")
                time.sleep(0.1)
        except KeyboardInterrupt:
            metrics_server.shutdown()

class MetricsHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'text/plain')
        self.end_headers()
        self.wfile.write(generate_latest())

if __name__ == "__main__":
    generate_logs()
