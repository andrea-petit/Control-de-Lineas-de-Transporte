import requests

SERVER_IP = "192.168.1.44"
PORT = 5000

def detect_api_url():
    try:
        r = requests.get(f"http://127.0.0.1:{PORT}/api/auth/ping", timeout=0.8)
        if r.ok:
            return f"http://127.0.0.1:{PORT}"
    except:
        pass
    try:
        r = requests.get(f"http://{SERVER_IP}:{PORT}/api/auth/ping", timeout=1.0)
        if r.ok:
            return f"http://{SERVER_IP}:{PORT}"
    except:
        pass
    return f"http://{SERVER_IP}:{PORT}"

API_BASE = detect_api_url()

class GlobalState:
    token = None
    usuario = None
    is_admin = False