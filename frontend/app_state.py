import requests
import os
import sys

SERVER_IP = "192.168.0.105"
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


def resources_path(relative_path):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    # Use the directory containing this file as the base
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_dir, relative_path)

class GlobalState:
    token = None
    usuario = None
    role= None
    is_admin = False