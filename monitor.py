import os
import re
import requests
from datetime import datetime


BOT_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

STATUS_FILE = "last_dates.txt"


# 多来源配置
SOURCES = [
    {
        "name": "iFlyChina",
        "url": "https://www.iflychina.net/visa/interview_schedule/1530557"
    },

    # 以后增加来源，在这里继续添加
    # {
    #     "name": "Source2",
    #     "url": "https://example.com"
    # }
]


def send_telegram(message):

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    keyboard = {
        "inline_keyboard": [
            [
                {
                    "text": "🔗 打开来源页面",
                    "url": message.split("来源链接:")[-1].strip()
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
        url,
        data=data,
        timeout=20
    )



def get_dates_from_source(source):

    response = requests.get(
        source["url"],
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


    return dates



def read_old_dates():

    if not os.path.exists(STATUS_FILE):
        return []


    with open(
        STATUS_FILE,
        "r",
        encoding="utf-8"
    ) as f:

        return f.read().splitlines()



def save_dates(all_dates):

    with open(
        STATUS_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        for item in all_dates:
            f.write(item + "\n")



def check_slot():

    old_dates = read_old_dates()

    new_saved_dates = []

    alerts = []


    for source in SOURCES:

        try:

            dates = get_dates_from_source(source)

        except Exception as e:

            print(
                source["name"],
                "失败:",
                e
            )

            continue


        for date in dates:

            record = (
                source["name"]
                +
                "|"
                +
                date
            )


            new_saved_dates.append(record)


            if record not in old_dates:

                alerts.append(
                    {
                        "source": source["name"],
                        "date": date,
                        "url": source["url"]
                    }
                )



    if alerts:

        now = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )


        message = (
            "🚨🚨 H1B Guangzhou SLOT Alert\n\n"
            f"时间:\n{now}\n\n"
        )


        for alert in alerts:

            message += (
                "🟢 新增日期:\n"
                f"{alert['date']}\n"
                f"来源:\n{alert['source']}\n"
                f"来源链接:\n{alert['url']}\n\n"
            )


        send_telegram(message)



    save_dates(new_saved_dates)



if __name__ == "__main__":

    check_slot()
