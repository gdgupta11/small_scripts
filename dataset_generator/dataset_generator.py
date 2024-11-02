import random
import time
import uuid
from datetime import datetime
import json

# Define the possible values for each field
LOG_LEVELS = ["INFO", "WARNING", "ERROR"]
USER_IDS = [f"user_{i}" for i in range(1, 101)]
IP_ADDRESSES = [f"192.168.1.{i}" for i in range(1, 101)]
REQUEST_METHODS = ["GET", "POST", "PUT", "DELETE"]
URL_PATHS = ["/home", "/login", "/logout", "/signup", "/products", "/cart", "/checkout"]
STATUS_CODES = [200, 201, 400, 401, 403, 404, 500]

# Define a function to generate a single log entry
def generate_log():
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "level": random.choice(LOG_LEVELS),
        "user_id": random.choice(USER_IDS),
        "ip_address": random.choice(IP_ADDRESSES),
        "method": random.choice(REQUEST_METHODS),
        "url_path": random.choice(URL_PATHS),
        "status_code": random.choice(STATUS_CODES),
        "response_time_ms": round(random.uniform(50, 1000), 2),
        "session_id": str(uuid.uuid4()),
        "message": "Sample log message"
    }
    return log_entry

# Generate logs continuously
def generate_logs(filename="web_app_logs.json", count=100):
    with open(filename, "w") as f:
        for _ in range(count):
            log_entry = generate_log()
            f.write(json.dumps(log_entry) + "\n")
            time.sleep(0.1)  # Simulate log generation frequency

if __name__ == "__main__":
    generate_logs()
