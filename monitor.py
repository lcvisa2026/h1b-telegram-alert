import os
import re
import requests
from datetime import datetime


BOT_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

STATUS_FILE = "last_dates.txt"

TARGET_URL = "https://www.iflychina.net/visa/interview_schedule/1530557"


def send_telegram(message):

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    keyboard = {
        "inline_keyboard": [
            [
                {
                    "text": "🔗 打开监控页面",
                    "url": TARGET_URL
                }
            ]
        ]
    }

    data = {
        "chat_id": CHAT_ID,
        "text": message,
        "reply_markup": str(keyboard).replace("'", '"')
    }

    response = requests.post(
        url,
        data=data,
        timeout=20
    )

    print(response.text)



def get_dates():

    response = requests.get(
        TARGET_URL,
        headers={
            "User-Agent": "Mozilla/5.0"
        },
        timeout=20
    )

    response.raise_for_status()

    text = response.text


    dates = re.findall(
        r"20\d{2}[-/.]\d{1,2}[-/.]\d{1,2}",
        text
    )


    dates = sorted(
        list(set(dates))
    )


    print("当前日期:", dates)


    return dates



def read_old_dates():

    if not os.path.exists(STATUS_FILE):
        return []


    with open(
        STATUS_FILE,
        "r",
        encoding="utf-8"
    ) as f:

        dates = f.read().splitlines()


    if dates == ["none"]:
        return []


    return dates



def save_dates(dates):

    with open(
        STATUS_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        for date in dates:
            f.write(date + "\n")



def check_slot():

    try:

        current_dates = get_dates()

    except Exception as e:

        print(
            "读取失败:",
            e
        )

        return


    old_dates = read_old_dates()


    # 只关注新增日期

    new_dates = [
        d for d in current_dates
        if d not in old_dates
    ]


    if new_dates:


        now = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )


        message = (
            "🚨🚨 H1B Guangzhou SLOT Alert\n\n"
            f"⏰ 时间:\n{now}\n\n"
            "🟢 新增可用日期:\n\n"
            +
            "\n".join(new_dates)
            +
            "\n\n"
            "请尽快确认预约情况。\n\n"
            "来源:\n"
            +
            TARGET_URL
        )


        send_telegram(message)


    # 无论有没有新增，都更新状态

    save_dates(current_dates)



if __name__ == "__main__":

    check_slot()
