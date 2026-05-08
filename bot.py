import requests
import json
import os

API_URL = "https://adhahi.dz/api/v1/public/wilaya-quotas"
STATE_FILE = "state.json"

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# ===== PROXY =====
PROXY_USER = os.getenv("PROXY_USER")
PROXY_PASS = os.getenv("PROXY_PASS")
PROXY_IP = os.getenv("PROXY_IP")
PROXY_PORT = os.getenv("PROXY_PORT")

proxy_url = None
proxies = None

if all([PROXY_USER, PROXY_PASS, PROXY_IP, PROXY_PORT]):
    proxy_url = f"http://{PROXY_USER}:{PROXY_PASS}@{PROXY_IP}:{PROXY_PORT}"
    proxies = {
        "http": proxy_url,
        "https": proxy_url
    }


session = requests.Session()


# ===== TELEGRAM =====
def send_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={
        "chat_id": CHAT_ID,
        "text": text
    })


# ===== STATE =====
def load_state():
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}


def save_state(state):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False)


# ===== FETCH DATA =====
def get_data():
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://adhahi.dz/register",
        "Origin": "https://adhahi.dz",
        "Accept": "application/json"
    }

    try:
        response = session.get(
            API_URL,
            headers=headers,
            proxies=proxies,
            timeout=20
        )
        response.raise_for_status()
        return response.json()

    except Exception as e:
        print("Fetch error:", e)
        return None


# ===== PARSE =====
def extract_statuses(data):
    return {
        0: data[27],
        1: data[9]
    }


# ===== MAIN =====
def main():
    old_state = load_state()

    data = get_data()

    if not data:
        print("No data fetched.")
        return

    current_state = extract_statuses(data)

    for wilaya, status in current_state.items():
        old_status = old_state.get(wilaya)

        if old_status != status:
            send_message(f"📢 Update in {wilaya}\n\n{status}")

    save_state(current_state)


if __name__ == "__main__":
    main()