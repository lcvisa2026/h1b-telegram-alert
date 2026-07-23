import os
import requests
import hashlib
from datetime import datetime


BOT_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

STATUS_FILE = "last_status.txt"


# iFlyChina H1B 信息页面
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


def get_page_info():

    response = requests.get(
        TARGET_URL,
        headers={
            "User-Agent": "Mozilla/5.0"
        },
        timeout=20
    )

    response.raise_for_status()

    text = response.text.lower()


    keywords = [
        "guangzhou",
        "广州",
        "h1b",
        "h-1b",
        "available",
        "appointment",
        "slot",
        "放号",
        "预约",
        "日期"
    ]


    found_keywords = []

    for word in keywords:
        if word.lower() in text:
            found_keywords.append(word)


    # 提取网页前部分作为摘要
    summary = response.text[:800]


    # 生成页面状态指纹
    fingerprint = hashlib.md5(
        (
            ",".join(found_keywords)
            +
            summary
        ).encode("utf-8")
    ).hexdigest()


    return fingerprint, found_keywords, summary



def read_old_status():

    if os.path.exists(STATUS_FILE):

        with open(
            STATUS_FILE,
            "r",
            encoding="utf-8"
        ) as f:
            return f.read().strip()

    return ""



def save_status(status):

    with open(
        STATUS_FILE,
        "w",
        encoding="utf-8"
    ) as f:
        f.write(status)



def check_slot():

    try:

        current_status, keywords, summary = get_page_info()

    except Exception as e:

        print(
            "网页读取失败:",
            e
        )

        return


    old_status = read_old_status()


    if current_status != old_status:


        now = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )


        message = (
            "🚨 H1B Guangzhou Monitor\n\n"
            f"时间: {now}\n\n"
            f"发现关键词:\n"
            f"{', '.join(keywords)}\n\n"
            "页面发生变化，请查看：\n"
            f"{TARGET_URL}\n\n"
            "摘要:\n"
            f"{summary[:300]}"
        )


        send_telegram(message)


        save_status(current_status)



if __name__ == "__main__":

    check_slot()
