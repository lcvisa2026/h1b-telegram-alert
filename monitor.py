import os
import requests

BOT_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")


def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    data = {
        "chat_id": CHAT_ID,
        "text": message
    }

    response = requests.post(url, data=data)

    print(response.text)


def check_slot():
    # 模拟发现广州 H1B slot
    slot_found = True

    if slot_found:
        send_telegram(
            "🚨 H1B Slot Alert\n\n"
            "地点: Guangzhou\n"
            "类型: H-1B\n"
            "状态: 发现可预约日期\n\n"
            "请登录官方预约系统确认。"
        )


if __name__ == "__main__":
    check_slot()
