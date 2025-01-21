import json
import os
import time

import pytz
import requests
from dotenv import load_dotenv
from datetime import datetime as dt, timedelta

from functions.view_weekly_schedule import get_schedule_employees
from models.reserve_bot import SessionLocal
from models.rooms import Rooms
from models.users import Users
from services.log import add_log

session = SessionLocal()
tehran_tz = pytz.timezone("Asia/Tehran")
load_dotenv()


def send_msg(text, chat_id, keyboard):
    try:
        token = os.getenv("TOKEN_RESERVE")
        url = f"https://api.telegram.org/bot{token}/sendMessage"

        # Prepare the payload
        payload = {
            "chat_id": chat_id,
            "text": text,
            "reply_markup": json.dumps(keyboard)
        }

        # Send the request
        response = requests.post(url, data=payload)
        response.raise_for_status()  # Raise an exception for HTTP errors

    except requests.RequestException as e:
        add_log(f"RequestException in send_msg: {e}", )
    except Exception as e:
        add_log(f"Exception in send_msg: {e}")


def get_before_meeting_buttons():
    keyboard = {
        "inline_keyboard": [
            [
                {"text": "🆗", "callback_data": "ok-before-meeting"},
                {"text": "❌ Cancel", "callback_data": "cancel"}
                ########## callback ##########
            ]
        ]
    }
    return keyboard


# Example usage
# send_msg("Hello, this is a message with inline buttons!", "6950791995")
def check_session_sending():
    while True:
        try:
            today = dt.now(tehran_tz)
            today = dt(year=today.year, month=today.month, day=today.day)
            tomorrow = today + timedelta(days=1)
            rooms = session.query(Rooms).all()
            for room in rooms:
                schedule, employees = get_schedule_employees(session, room, [today, tomorrow])
            print(schedule)
            for name, reserve in schedule.items():
                user = get_user_by_name(name)
                str_time = f"{reserve[0][3]} {reserve[0][1]}"
                dt_reserve = dt.strptime(str_time, "%Y-%m-%d %H:%M")
                print(user.username, user.chat_id)
                print(reserve[0][1:])
            time.sleep(10)
        except json.JSONDecodeError:
            time.sleep(1)
        except Exception as e:
            add_log(f"Exception in check_session_sending: {e}")
            time.sleep(1)


def get_user_by_name(name):
    return session.query(Users).filter_by(name=name).first()


check_session_sending()
