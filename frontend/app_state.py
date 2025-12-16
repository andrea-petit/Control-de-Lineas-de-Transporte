import requests
import os
import sys
import json

SERVER_IP = "192.168.0.105"
PORT = 5000

CONFIG_FILE = os.path.join(os.path.dirname(__file__), "config.json")

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
                return config.get('server_ip', SERVER_IP)
        except:
            pass
    return SERVER_IP

def save_config():
    config = {'server_ip': GlobalState.server_ip}
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f)
    except:
        pass

def detect_api_url():
    try:
        r = requests.get(f"http://127.0.0.1:{PORT}/api/auth/ping", timeout=0.8)
        if r.ok:
            return f"http://127.0.0.1:{PORT}"
    except:
        pass
    server_ip = load_config()
    try:
        r = requests.get(f"http://{server_ip}:{PORT}/api/auth/ping", timeout=1.0)
        if r.ok:
            return f"http://{server_ip}:{PORT}"
    except:
        pass
    return f"http://{server_ip}:{PORT}"

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
    server_ip = load_config()

def set_server_ip(new_ip):
    GlobalState.server_ip = new_ip
    save_config()
    global API_BASE
    API_BASE = detect_api_url()