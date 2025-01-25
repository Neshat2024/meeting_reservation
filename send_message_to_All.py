import os

import requests
from dotenv import load_dotenv

from models.reserve_bot import SessionLocal
from models.users import Users
from services.log import add_log

session = SessionLocal()
load_dotenv()


def send_msg(text, chat_id):
    try:
        token = os.getenv("TOKEN_RESERVE")
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        # Prepare the payload
        payload = {
            "chat_id": chat_id,
            "text": text
        }
        # Send the request
        response = requests.post(url, data=payload)
        response.raise_for_status()  # Raise an exception for HTTP errors
    except requests.RequestException as e:
        add_log(f"RequestException in send_msg: {e}")
    except Exception as e:
        add_log(f"Exception in send_msg: {e}")


def send_the_text(text):
    try:
        users = session.query(Users).all()
        for user in users:
            send_msg(text, user.chat_id)
    except Exception as e:
        add_log(f"Exception in check_session_sending: {e}")


txt = """
قابلیت های اضافه شده به بات رزرو اتاق جلسات (@Note_Booking_bot)

1- اضافه شدن دستور تنظیمات (/settings) به بات که برای تغییر زبان بات استفاده می شود.

2- اضافه شدن زبان فارسی (با تغییر زبان، تقویم به شمسی تغییر می کند)

3- ارسال پیام جهت تایید رزرو ۲ ساعت قبل از شروع جلسه:
در صورتی که پیام نادیده گرفته شود یا دکمه (باشه ممنون ✅) زده شود، رزرو در حالت خود باقی می ماند. در صورتی که دکمه (لازم ندارم،پاکش کن) انتخاب شود رزرو لغو می گردد. (اگر پس از پایان زمان جلسه روی دکمه ها زده شود اجازه انجام هیچ دستوری داده نخواهد شد.)

4- پس از شروع جلسه یک پیام برای کسی که رزرو کرده ارسال می شود که این پیام حاوی دکمه (⏹️ پایان جلسه) است. هر زمان که این دکمه انتخاب شود باقی زمان جلسه آزاد و قابل رزرو می گردد. (اگر پس از پایان زمان جلسه روی این دکمه زده شود اجازه داده نخواهد شد.)

5- انتخاب بازه دریافت گزارش:
امکان دریافت گزارش امروز - گزارش یک روز خاص و گزارش هفتگی فراهم گردیده است.
"""

send_the_text(txt)
