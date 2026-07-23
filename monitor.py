import os
import re
import requests
from datetime import datetime


BOT_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

STATUS_FILE = "last_date.txt"


TARGET_URL = "https://www.iflychina.net/visa/interview_schedule/1530557"


def send_telegram(message):

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    data = {
        "chat_id": CHAT_ID,
        "text": message
    }

    requests.post(
        url,
        data=data,
        timeout=20
    )


def get_dates_from_page():

    response = requests.get(
        TARGET_URL,
        headers={
            "User-Agent": "Mozilla/5.0"
        },
        timeout=20
    )

    response.raise_for_status()

    text = response.text


    # 匹配：
    # 2026-09-15
    # 2026/09/15
    # 2026.09.15

    dates = re.findall(
        r"20\d{2}[-/.]\d{1,2}[-/.]\d{1,2}",
        text
    )


    # 去重 + 排序

    dates = list(set(dates))

    dates.sort()


    return dates



def read_old_date():

    if os.path.exists(STATUS_FILE):

        with open(
            STATUS_FILE,
            "r",
            encoding="utf-8"
        ) as f:

            return f.read().strip()

    return ""



def save_date(date):

    with open(
        STATUS_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(date)



def check_slot():

    try:

        dates = get_dates_from_page()

    except Exception as e:

        print(e)
        return


    if not dates:

        print("没有找到日期")

        return


    # 取最早日期

    current_date = dates[0]


    old_date = read_old_date()


    if current_date != old_date:


        now = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )


        message = (
            "🚨 H1B Guangzhou Slot Alert\n\n"
            f"时间: {now}\n\n"
            f"旧日期:\n{old_date or '无'}\n\n"
            f"新日期:\n{current_date}\n\n"
            "请登录官方系统确认。\n\n"
            f"来源:\n{TARGET_URL}"
        )


        send_telegram(message)


        save_date(current_date)



if __name__ == "__main__":

    check_slot()
