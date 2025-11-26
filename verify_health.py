import urllib.request
import json
import sys
import time

def check_health():
    url = "http://127.0.0.1:8000/health"
    retries = 5
    for i in range(retries):
        try:
            with urllib.request.urlopen(url) as response:
                if response.getcode() == 200:
                    data = json.loads(response.read().decode())
                    print(f"Health check passed: {data}")
                    if data.get("status") == "ok" and data.get("database") == "connected":
                        sys.exit(0)
                    else:
                        sys.exit(1)
                else:
                    print(f"Health check failed with status: {response.getcode()}")
        except Exception as e:
            print(f"Attempt {i+1} failed: {e}")
            time.sleep(2)
    sys.exit(1)

if __name__ == "__main__":
    check_health()
