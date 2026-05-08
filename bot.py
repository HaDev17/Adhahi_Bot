import requests
import json
import os
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

session = requests.Session()

retries = Retry(
    total=5,
    backoff_factor=1,
    status_forcelist=[500, 502, 503, 504]
)

headers = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json",
    "Referer": "https://adhahi.dz/register"
}

session.mount("https://", HTTPAdapter(max_retries=retries))
session.get("https://adhahi.dz/register", headers=headers, timeout=20)

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

API_URL = "https://adhahi.dz/api/v1/public/wilaya-quotas"

STATE_FILE = "state.json"

TARGET_WILAYAS = ["المسيلة", "البويرة"]
def send_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    requests.post(url, data={
        "chat_id": CHAT_ID,
        "text": text
    })


def load_state():
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}


def save_state(state):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False)


def get_data():

    try:
        response = requests.get(
            API_URL,
            headers=headers,
            timeout=(5, 20)  # connect + read timeout
        )
        response.raise_for_status()
        return response.json()

    except requests.exceptions.RequestException as e:
        print("Request error:", e)
        return None


def extract_statuses(data):

    results = {}

    for item in data:

        wilaya_name = item.get("wilayaNameAr")

        if wilaya_name in TARGET_WILAYAS:
            results[wilaya_name] = item

    return results

def main():

    old_state = load_state()

    data = get_data()
    if not data:   # 👈 أهم سطر
        print("No data fetched. Exiting safely.")
        return

    current_state = extract_statuses(data)

    print(current_state)

    for wilaya, status in current_state.items():

        old_status = old_state.get(wilaya)

        if old_status != status:

            message = (
                f"📢 تحديث جديد\n\n"
                f"🏙️ الولاية: {wilaya}\n"
                f"📦 الحالة: {status['available']}"
            )
            send_message(message)

    save_state(current_state)


if __name__ == "__main__":
    main()