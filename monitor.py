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

    data = {
        "chat_id": CHAT_ID,
        "text": message
    }

    requests.post(
        url,
        data=data,
        timeout=20
    )


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


    # 去重 + 排序

    dates = sorted(
        list(set(dates))
    )


    return dates



def read_old_dates():

    if os.path.exists(STATUS_FILE):

        with open(
            STATUS_FILE,
            "r",
            encoding="utf-8"
        ) as f:

            return f.read().splitlines()

    return []



def save_dates(dates):

    with open(
        STATUS_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        for d in dates:

            f.write(
                d + "\n"
            )



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



    if current_dates != old_dates:


        added = [
            d for d in current_dates
            if d not in old_dates
        ]


        removed = [
            d for d in old_dates
            if d not in current_dates
        ]



        now = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )


        message = (
            "🚨 H1B Guangzhou Slot Alert\n\n"
            f"时间: {now}\n\n"
        )


        if added:

            message += (
                "🟢 新增日期:\n"
                +
                "\n".join(added)
                +
                "\n\n"
            )


        if removed:

            message += (
                "🔴 消失日期:\n"
                +
                "\n".join(removed)
                +
                "\n\n"
            )


        message += (
            "当前日期列表:\n"
            +
            (
                "\n".join(current_dates)
                if current_dates
                else "无"
            )
            +
            "\n\n来源:\n"
            +
            TARGET_URL
        )


        send_telegram(message)


        save_dates(current_dates)



if __name__ == "__main__":

    check_slot()
