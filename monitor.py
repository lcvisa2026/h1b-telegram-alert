import os
import requests
import hashlib

BOT_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

STATUS_FILE = "last_status.txt"

# 这里填写你要监控的公开网页地址
TARGET_URL = "https://example.com"


def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    data = {
        "chat_id": CHAT_ID,
        "text": message
    }

    requests.post(url, data=data)


def get_page_status():
    try:
        response = requests.get(
            TARGET_URL,
            timeout=20,
            headers={
                "User-Agent": "Mozilla/5.0"
            }
        )

        text = response.text.lower()

        keywords = [
            "guangzhou",
            "h1b",
            "available",
            "appointment"
        ]

        found = [
            word for word in keywords
            if word in text
        ]

        status = ",".join(found)

        # 用hash保存网页状态
        return hashlib.md5(
            status.encode()
        ).hexdigest()

    except Exception as e:
        return "error"


def read_old_status():
    if os.path.exists(STATUS_FILE):
        with open(STATUS_FILE, "r") as f:
            return f.read().strip()

    return ""


def save_status(status):
    with open(STATUS_FILE, "w") as f:
        f.write(status)


def check_slot():

    current = get_page_status()
    old = read_old_status()

    if current != old:

        send_telegram(
            "🚨 H1B Slot Monitor\n\n"
            "检测到页面状态变化。\n"
            "请登录官方系统确认。"
        )

        save_status(current)


if __name__ == "__main__":
    check_slot()
