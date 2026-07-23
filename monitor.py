import os
import requests
import hashlib
from datetime import datetime

BOT_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

STATUS_FILE = "last_status.txt"

# 后续替换成你要监控的公开页面
TARGET_URL = "https://example.com"


def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    data = {
        "chat_id": CHAT_ID,
        "text": message
    }

    requests.post(url, data=data)


def get_page_info():

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
        "appointment",
        "slot"
    ]

    found_keywords = []

    for word in keywords:
        if word in text:
            found_keywords.append(word)

    # 取网页文字前500字符作为摘要
    summary = response.text[:500]

    # 生成状态指纹
    fingerprint = hashlib.md5(
        (
            ",".join(found_keywords)
            + summary
        ).encode()
    ).hexdigest()

    return fingerprint, found_keywords, summary


def read_old_status():

    if os.path.exists(STATUS_FILE):
        with open(STATUS_FILE, "r") as f:
            return f.read().strip()

    return ""


def save_status(status):

    with open(STATUS_FILE, "w") as f:
        f.write(status)


def check_slot():

    try:
        current, keywords, summary = get_page_info()

    except Exception as e:
        print(e)
        return


    old = read_old_status()


    if current != old:

        now = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        message = (
            "🚨 H1B Slot Monitor\n\n"
            f"时间: {now}\n"
            f"关键词: {', '.join(keywords)}\n\n"
            "页面发生变化，请检查。\n\n"
            f"摘要:\n{summary[:300]}"
        )

        send_telegram(message)

        save_status(current)



if __name__ == "__main__":
    check_slot()
