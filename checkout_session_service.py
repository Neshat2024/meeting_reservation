import json
import os
import time
from datetime import datetime as dt, timedelta

import pytz
import requests
from dotenv import load_dotenv
from sqlalchemy.exc import SQLAlchemyError

from functions.get_functions import get_date_obj
from models.reservations import Reservations
from models.reserve_bot import SessionLocal
from models.rooms import Rooms
from models.users import Users
from services.config import CONFIRMED, CHECKOUT
from services.language import get_text, BotText
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
            "reply_markup": json.dumps(keyboard),
        }
        # Send the request
        response = requests.post(url, data=payload)
        response.raise_for_status()  # Raise an exception for HTTP errors
    except requests.RequestException as e:
        add_log(f"RequestException in send_msg: {e}")
    except Exception as e:
        add_log(f"Exception in send_msg: {e}")


def check_session_sending():
    processed_reservations = set()  # Set to keep track of processed reservations
    while True:
        try:
            now = dt.now(tehran_tz)
            rooms = session.query(Rooms).all()
            schedule = {}
            for room in rooms:
                schedule = get_schedule_in_check_session(room, schedule)
            for name, reserves in schedule.items():
                user = get_user_by_name(name)
                for reserve in reserves:
                    str_time = f"{reserve[3]} {reserve[1]}"
                    dt_reserve = dt.strptime(str_time, "%Y-%m-%d %H:%M")
                    dt_reserve = tehran_tz.localize(dt_reserve)
                    diff = int((dt_reserve - now).total_seconds() / 60)
                    reservation_id = f"{name}_{str_time}_{reserve[-1]}"
                    if reservation_id not in processed_reservations:
                        if diff == 120:
                            txt = get_text(
                                BotText.REMINDER_MESSAGE, user.language
                            ).format(reserve=reserve[0])
                            buttons = get_buttons_in_check_meeting_time(
                                user, f"cancel_{reserve[-1]}"
                            )
                            send_msg(txt, int(user.chat_id), buttons)
                            processed_reservations.add(reservation_id)
                        elif diff == 0 or diff < 0:
                            txt = get_text(
                                BotText.CHECKOUT_MESSAGE, user.language
                            ).format(reserve=reserve[2])
                            buttons = get_buttons_in_check_meeting_time(
                                user, f"checkout_{reserve[-1]}", "checkout"
                            )
                            send_msg(txt, int(user.chat_id), buttons)
                            processed_reservations.add(reservation_id)
            time.sleep(10)
            session.close()
        except json.JSONDecodeError:
            time.sleep(1)
        except Exception as e:
            add_log(f"Exception in check_session_sending: {e}")
            time.sleep(1)


def get_schedule_in_check_session(room, schedule):
    try:
        now = dt.now(tehran_tz)
        str_date = f"{now.year}-{str(now.month).zfill(2)}-{str(now.day).zfill(2)}"
        end_day = tehran_tz.localize(
            dt(year=now.year, month=now.month, day=now.day, hour=21, minute=1)
        )
        reserves = (
            session.query(Reservations).filter_by(status=CONFIRMED, date=str_date).all()
        )
        for reserve in reserves:
            if str(reserve.room_id) == str(room.id):
                name, date, start, end, color = get_data_in_check_session(reserve)
                start_time = get_date_obj(date, start, True)
                end_time = get_date_obj(date, end, True)
                if now <= start_time <= end_day or start_time <= now <= end_time:
                    start_str = start_time.strftime("%H:%M")
                    if name not in schedule:
                        schedule[name] = [[room.name, start_str, end, date, reserve.id]]
                    else:
                        schedule[name].append(
                            [room.name, start_str, end, date, reserve.id]
                        )
        return schedule
    except SQLAlchemyError as e:
        add_log(f"SQLAlchemyError in get_schedule_in_check_session: {e}")
    except Exception as e:
        add_log(f"Exception in get_schedule_in_check_session: {e}")


def get_user_by_name(name):
    return session.query(Users).filter_by(name=name).first()


def get_data_in_check_session(reserve):
    user = session.query(Users).filter_by(id=reserve.user_id).first()
    return user.name, reserve.date, reserve.start_time, reserve.end_time, user.color


def get_buttons_in_check_meeting_time(user, cb, mode=None):
    if mode == CHECKOUT:
        keyboard = {
            "inline_keyboard": [
                [
                    {
                        "text": get_text(BotText.CHECKOUT_BUTTON, user.language),
                        "callback_data": f"{cb}",
                    }
                ]
            ]
        }
    else:
        keyboard = {
            "inline_keyboard": [
                [
                    {
                        "text": get_text(BotText.OK_REMINDER_BUTTON, user.language),
                        "callback_data": f"ok-before-meeting_{cb.split('_')[1]}",
                    },
                    {
                        "text": get_text(BotText.CANCEL_REMINDER_BUTTON, user.language),
                        "callback_data": f"{cb}",
                    },
                ]
            ]
        }
    return keyboard


check_session_sending()
