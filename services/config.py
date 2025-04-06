import os
import re
from datetime import datetime as dt

import jdatetime
from dotenv import load_dotenv
from sqlalchemy.exc import SQLAlchemyError
from telebot import types

from models.users import Users
from services.language import change_num_as_lang
from services.log import add_log

load_dotenv()

commands = [types.BotCommand(command="/start", description="Start menu")]

CANCEL, SELECT, REMOVE = "/cancel", "select", "remove"
BACK_DATE, BACK_MAIN, BACK_USER = "backdate", "backmain", "backuser"
BACK_ROOM = "backroom"
FIRST, SECOND, CONFIRMED = "first", "second", "confirmed"
DAYS_FOR_HEADERS = ["SA", "SU", "MO", "TU", "WE", "TH", "FR"]
DAYS_FOR_HEADERS_FA = ["ش", "۱ش", "۲ش", "۳ش", "۴ش", "۵ش", "ج"]
day_in_persian = {
    "Friday": "جمعه",
    "Thursday": "پنج‌شنبه",
    "Wednesday": "چهارشنبه",
    "Tuesday": "سه‌شنبه",
    "Monday": "دوشنبه",
    "Sunday": "یکشنبه",
    "Saturday": "شنبه",
}
WEEKDAYS_LIST = [
    ["شنبه", "Saturday"],
    ["یکشنبه", "Sunday"],
    ["دوشنبه", "Monday"],
    ["سه‌شنبه", "Tuesday"],
    ["چهارشنبه", "Wednesday"],
    ["پنج‌شنبه", "Thursday"],
    ["جمعه", "Friday"],
]
weekday_map = {
    "monday": 0,
    "tuesday": 1,
    "wednesday": 2,
    "thursday": 3,
    "friday": 4,
    "saturday": 5,
    "sunday": 6,
}
ONE, TWO, THREE = 1, 2, 3
CHECKOUT = "checkout"
FARSI, ENGLISH = "fa", "en"


def get_user(call_or_message, session):
    if isinstance(call_or_message, types.Message):
        chat_id = str(call_or_message.chat.id)
        return session.query(Users).filter_by(chat_id=chat_id).first()
    elif isinstance(call_or_message, types.CallbackQuery):
        chat_id = str(call_or_message.message.chat.id)
        return session.query(Users).filter_by(chat_id=chat_id).first()


def send_cancel_message(message):
    try:
        if message.text.lower() == CANCEL:
            return True
    except SQLAlchemyError as e:
        add_log(f"SQLAlchemyError in send_cancel_message: {e}")
    except Exception as e:
        add_log(f"Exception in send_cancel_message: {e}")


def check_text_in_name(message):
    if send_cancel_message(message):
        return
    elif contains_only_letters(message.text):
        return True
    else:
        return False


def contains_only_letters(text):
    pattern = r"^[a-zA-Z\u0600-\u06FF\s]+$"
    if re.match(pattern, text):
        return True
    return False


def check_text_in_charge(message):
    if send_cancel_message(message):
        return
    elif contains_only_numbers(message.text):
        return True
    else:
        return False


def contains_only_numbers(text):
    text = change_num_as_lang(text, "en")
    try:
        int(text)
        return True
    except ValueError:
        return False


def add_user(message, session):
    try:
        chat_id, uname = str(message.chat.id), message.chat.username
        admins = os.getenv("ADMINS").split("-")
        managers = os.getenv("MANAGERS").split("-")
        if uname in managers:
            user = Users(chat_id=chat_id, username=uname, role="manager")
        elif uname in admins:
            user = Users(chat_id=chat_id, username=uname, role="admin")
        else:
            user = Users(chat_id=chat_id, username=uname)
        session.add(user)
        session.commit()
        user = get_user(message, session)
        return user
    except SQLAlchemyError as e:
        add_log(f"SQLAlchemyError in add_user_in_start: {e}")
    except Exception as e:
        add_log(f"Exception in add_user_in_start: {e}")


def telegram_api_exception(func, error):
    if "message is not modified" in str(error):
        add_log(f"Same content and markup in {func}")
    else:
        add_log(f"An error occurred in {func}: {error}")


def check_role(user, session):
    try:
        admins = os.getenv("ADMINS").split("-")
        managers = os.getenv("MANAGERS").split("-")
        uname, user_role = user.username, user.role
        if uname in admins and uname not in managers and user_role != "admin":
            user.role = "admin"
            session.commit()
        elif uname in managers and user_role != "manager":
            user.role = "manager"
            session.commit()
        elif uname not in admins and uname not in managers and user_role:
            user.role = ""
            session.commit()
    except SQLAlchemyError as e:
        add_log(f"SQLAlchemyError in check_role: {e}")
    except Exception as e:
        add_log(f"Exception in check_role: {e}")


def set_command_in_wraps(user, session, command):
    try:
        user.command = command
        session.commit()
    except SQLAlchemyError as e:
        add_log(f"SQLAlchemyError in set_command_in_wraps: {e}")
    except Exception as e:
        add_log(f"Exception in set_command_in_wraps: {e}")


def change_command_to_none(user, session):
    try:
        user.command = None
        session.commit()
    except SQLAlchemyError as e:
        add_log(f"SQLAlchemyError in change_command_to_none: {e}")
    except Exception as e:
        add_log(f"Exception in change_command_to_none: {e}")


def gregorian_to_jalali(date_str):
    gregorian_date = dt.strptime(date_str, "%Y-%m-%d")
    jalali_date = jdatetime.date.fromgregorian(date=gregorian_date)
    jalali_date_str = jalali_date.strftime("%Y/%m/%d")
    return jalali_date_str


def jalali_to_gregorian(date_str):
    year, month, day = map(int, date_str.split("/"))
    jalali_date = jdatetime.date(year, month, day)
    gregorian_date = jalali_date.togregorian()
    return gregorian_date.strftime("%Y-%m-%d")


def time_difference(time1: str, time2: str) -> int:
    time_format = "%H:%M"
    t1 = dt.strptime(time1, time_format)
    t2 = dt.strptime(time2, time_format)
    difference = (t2 - t1).total_seconds() / 60
    return int(difference)
