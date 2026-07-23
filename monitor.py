import os
import re
import time
import requests
from datetime import datetime


BOT_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

STATUS_FILE = "last_dates.txt"


SOURCES = [
    {
        "name": "iFlyChina",
        "url": "https://www.iflychina.net/visa/interview_schedule/1530557"
    }
]


KEYWORDS = [
    "h1b",
    "h-1b",
    "guangzhou",
    "广州",
    "appointment",
    "interview",
    "slot",
    "预约"
]


def send_telegram(message, url):

    api = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"


    keyboard = {
        "inline_keyboard": [
            [
                {
                    "text": "🔗 打开来源页面",
                    "url": url
                }
            ]
        ]
    }


    data = {
        "chat_id": CHAT_ID,
        "text": message,
        "reply_markup": str(keyboard).replace("'", '"')
    }


    requests.post(
        api,
        data=data,
        timeout=20
    )



def request_page(url):

    for attempt in range(3):

        try:

            response = requests.get(
                url,
                headers={
                    "User-Agent": "Mozilla/5.0"
                },
                timeout=20
            )

            response.raise_for_status()

            return response.text


        except Exception as e:

            print(
                f"第{attempt+1}次失败:",
                e
            )

            time.sleep(10)


    return None



def extract_dates(text):

    text_lower = text.lower()


    matched_positions = []


    for keyword in KEYWORDS:

        pos = text_lower.find(
            keyword.lower()
        )

        if pos != -1:

            start = max(
                0,
                pos - 300
            )

            end = min(
                len(text),
                pos + 500
            )

            matched_positions.append(
                text[start:end]
            )


    search_area = "\n".join(
        matched_positions
    )


    dates = re.findall(
        r"20\d{2}[-/.]\d{1,2}[-/.]\d{1,2}",
        search_area
    )


    return sorted(
        list(set(dates))
    )



def read_old_dates():

    if not os.path.exists(STATUS_FILE):

        return []


    with open(
        STATUS_FILE,
        "r",
        encoding="utf-8"
    ) as f:

        return f.read().splitlines()



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

    old_dates = read_old_dates()

    current_records = []

    alerts = []


    for source in SOURCES:


        html = request_page(
            source["url"]
        )


        if not html:

            print(
                source["name"],
                "无法读取"
            )

            continue



        dates = extract_dates(
            html
        )


        print(
            source["name"],
            dates
        )



        for date in dates:


            record = (
                source["name"]
                +
                "|"
                +
                date
            )


            current_records.append(
                record
            )


            if record not in old_dates:

                alerts.append(
                    {
                        "source": source["name"],
                        "date": date,
                        "url": source["url"]
                    }
                )



    if alerts:


        message = (
            "🚨🚨 H1B Guangzhou SLOT Alert\n\n"
            f"时间:\n"
            +
            datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )
            +
            "\n\n"
        )


        for item in alerts:

            message += (
                "🟢 新增日期:\n"
                f"{item['date']}\n"
                f"来源:\n{item['source']}\n\n"
            )


        send_telegram(
            message,
            alerts[0]["url"]
        )


    save_dates(
        current_records
    )



if __name__ == "__main__":

    check_slot()
