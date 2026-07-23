import os
import requests

BOT_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

STATUS_FILE = "last_status.txt"


def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    data = {
        "chat_id": CHAT_ID,
        "text": message
    }

    requests.post(url, data=data)


def get_current_status():
    """
    这里以后接入真实数据来源
    目前模拟一个广州 H1B 日期
    """

    return "Guangzhou_H1B_2026-10-01"


def read_old_status():
    if os.path.exists(STATUS_FILE):
        with open(STATUS_FILE, "r") as f:
            return f.read().strip()

    return ""


def save_status(status):
    with open(STATUS_FILE, "w") as f:
        f.write(status)


def check_slot():

    current_status = get_current_status()
    old_status = read_old_status()

    if current_status != old_status:

        send_telegram(
            "🚨 H1B Slot Alert\n\n"
            f"地点: Guangzhou\n"
            f"类型: H-1B\n"
            f"状态变化:\n{current_status}\n\n"
            "请登录官方系统确认。"
        )

        save_status(current_status)


if __name__ == "__main__":
    check_slot()
