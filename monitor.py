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

    requests.post(url, data=data)


def check_slot():
    # 后续这里接入合法的数据来源
    # 当前先测试通知功能

    slot_found = False

    if slot_found:
        send_telegram(
            "🚨 H1B Guangzhou Slot Alert!\n"
            "发现新的可预约日期，请登录官方系统确认。"
        )


if __name__ == "__main__":
    check_slot()
