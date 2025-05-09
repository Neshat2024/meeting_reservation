import json
import logging
import os
import sys
import time
from datetime import datetime as dt, timedelta

import pytz
import requests
import telebot
from sqlalchemy.exc import SQLAlchemyError

from services.language import get_text, BotText

tehran_tz = pytz.timezone("Asia/Tehran")


def main():
    if len(sys.argv) < 2:
        print("Usage: python checkout_session_service.py <instance_name>")
        sys.exit(1)

    # Initialize settings with the specified instance
    from settings import settings as stg

    global stg  # Declare stg as global before using it
    stg.initialize(f".env.{sys.argv[1]}")

    from models.rooms import Rooms
    from models.reserve_bot import SessionLocal
    from services.log import add_log

    global session, add_log

    session = SessionLocal()

    t = f"checkout_session_service is running for {sys.argv[1]} ..."
    print(t)
    add_log(t, checkout=True)

    processed_reservations = set()
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
                    # reserve = [room.name, start_str, end, date, reserve.id]
                    reservation_id, dt_reserve = get_reservation_id(name, reserve)
                    diff = int((dt_reserve - now).total_seconds() / 60)
                    condition_1 = (
                        f"{reservation_id}_first" not in processed_reservations
                    )
                    condition_2 = (
                        f"{reservation_id}_second" not in processed_reservations
                    )
                    if condition_1 and diff == 120:
                        txt = get_text(BotText.REMINDER_MESSAGE, user.language).format(
                            reserve=reserve[0]
                        )
                        buttons = get_buttons_in_check_meeting_time(
                            user, f"cancel_{reserve[-1]}"
                        )
                        send_msg(txt, int(user.chat_id), buttons)
                        processed_reservations.add(f"{reservation_id}_first")
                    elif condition_2 and diff <= 0:
                        txt = get_text(BotText.CHECKOUT_MESSAGE, user.language).format(
                            reserve=reserve[2]
                        )
                        buttons = get_buttons_in_check_meeting_time(
                            user, f"checkout_{reserve[-1]}", "checkout"
                        )
                        send_msg(txt, int(user.chat_id), buttons)
                        processed_reservations.add(f"{reservation_id}_second")
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
        from settings import CONFIRMED
        from models.reservations import Reservations

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
    from models.users import Users

    return session.query(Users).filter_by(name=name).first()


def get_reservation_id(name, reserve):
    str_time = f"{reserve[3]} {reserve[1]}"
    dt_reserve = dt.strptime(str_time, "%Y-%m-%d %H:%M")
    dt_reserve = tehran_tz.localize(dt_reserve)
    reservation_id = f"{name}_{str_time}_{reserve[-1]}"
    return reservation_id, dt_reserve


def get_data_in_check_session(reserve):
    from models.users import Users

    try:
        user = session.query(Users).filter_by(id=reserve.user_id).first()
        return user.name, reserve.date, reserve.start_time, reserve.end_time, user.color
    except SQLAlchemyError as e:
        add_log(f"SQLAlchemyError in get_data_in_check_session: {e}")
    except Exception as e:
        add_log(f"Exception in get_data_in_check_session: {e}")


def get_buttons_in_check_meeting_time(user, cb, mode=None):
    from settings import CHECKOUT

    if mode == CHECKOUT:
        keyboard = {
            "inline_keyboard": [
                [
                    {
                        "text": get_text(BotText.CHECKOUT_BUTTON, user.language),
                        "callback_data": cb,
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
                        "callback_data": cb,
                    },
                ]
            ]
        }
    return keyboard


def send_msg(text, chat_id, keyboard):
    try:
        token = stg.TOKEN_RESERVE
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        # Prepare the payload
        payload = {
            "chat_id": chat_id,
            "text": text,
            "reply_markup": json.dumps(keyboard),
        }
        proxies = {}
        if stg.PROXY_HOST and stg.PROXY_PORT:
            proxy_url = f"socks5h://{stg.PROXY_HOST}:{stg.PROXY_PORT}"
            proxies = {"http": proxy_url, "https": proxy_url}
        # Send the request
        response = requests.post(url, data=payload, proxies=proxies)
        response.raise_for_status()  # Raise an exception for HTTP errors
    except requests.RequestException as e:
        add_log(f"RequestException in send_msg: {e}")
    except Exception as e:
        add_log(f"Exception in send_msg: {e}")


def get_date_obj(date, time_str, add_a_minute=False):
    if add_a_minute:
        the_time = dt.strptime(time_str, "%H:%M")
        the_time += timedelta(minutes=1)
        time_str = the_time.strftime("%H:%M")
    dt_time = dt.strptime(f"{date} {time_str}", "%Y-%m-%d %H:%M")
    return tehran_tz.localize(dt_time)


if __name__ == "__main__":
    main()
