import os
import random
from datetime import datetime as dt, timedelta

import jdatetime
import pytz
from dotenv import load_dotenv
from sqlalchemy.exc import SQLAlchemyError
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton as btn

from models.reservations import Reservations
from models.rooms import Rooms
from models.users import Users
from services.config import DAYS_FOR_HEADERS, CONFIRMED, FIRST, SECOND, gregorian_to_jalali, day_in_persian, FARSI, \
    DAYS_FOR_HEADERS_FA, get_user
from services.language import get_text, BotText, change_num_as_lang, convert_to_persian_numerals
from services.log import add_log

tehran_tz = pytz.timezone("Asia/Tehran")
load_dotenv()
admins = os.getenv("ADMINS").split("-")


def create_date_buttons(first_cb, user):
    start_date, end_date, days_of_week = get_start_end_week_date(user)
    markup = add_row_buttons([start_date, end_date, days_of_week], first_cb, user)
    return markup


def get_start_end_week_date(user):
    if user.language == FARSI:
        days_of_week = DAYS_FOR_HEADERS_FA
    else:
        days_of_week = DAYS_FOR_HEADERS
    start_date = dt.now(tehran_tz)
    end_date = start_date + timedelta(days=7)
    return start_date, end_date, days_of_week


def add_row_buttons(start_end_days, first_cb, user):
    if user.language == FARSI:
        row, markup = get_date_buttons_in_persian(start_end_days, first_cb)
    else:
        row, markup = get_date_buttons(start_end_days, first_cb)
    markup = add_free_buttons(row, markup, user)
    return markup


def get_date_buttons_in_persian(start_end_days, first_cb):
    start, end, days, row = start_end_days[0], start_end_days[1], start_end_days[2], []
    markup = InlineKeyboardMarkup(row_width=7)
    markup.row(*[btn(text=day, callback_data="NON") for day in reversed(days)])
    start_day_of_week = (start.weekday() + 2) % 7
    for _ in range(start_day_of_week):
        row.append(btn(text="__", callback_data="NON"))
    while start <= end:
        jalali_date = jdatetime.date.fromgregorian(date=start)
        jalali_day = jalali_date.day
        date = start.strftime('%Y-%m-%d')
        k = btn(text=convert_to_persian_numerals(str(jalali_day)), callback_data=f"{first_cb}_{date}")
        row.append(k)
        start += timedelta(days=1)
        if len(row) == 7:
            markup.row(*reversed(row))
            row = []
    return row, markup


def get_date_buttons(start_end_days, first_cb):
    start, end, days, row = start_end_days[0], start_end_days[1], start_end_days[2], []
    markup = InlineKeyboardMarkup(row_width=3)
    markup.row(*[btn(text=day, callback_data="NON") for day in days])
    start_day_of_week = (start.weekday() + 2) % 7
    for _ in range(start_day_of_week):
        row.append(btn(text="__", callback_data="NON"))
    while start <= end:
        date = start.strftime('%Y-%m-%d')
        k = btn(text=start.day, callback_data=f"{first_cb}_{date}")
        row.append(k)
        start += timedelta(days=1)
        if len(row) == 7:
            markup.row(*row)
            row = []
    return row, markup


def add_free_buttons(row, markup, user):
    if row and user.language == FARSI:
        while len(row) < 7:
            row.append(btn(text="__", callback_data="NON"))
        markup.row(*reversed(row))
    elif row:
        while len(row) < 7:
            row.append(btn(text="__", callback_data="NON"))
        markup.row(*row)
    return markup


def get_room_name(room_id, session):
    try:
        try:
            room_id = int(room_id)
            room = session.query(Rooms).filter_by(id=room_id).first()
            if room:
                return room.name
        except ValueError:
            return room_id
    except SQLAlchemyError as e:
        add_log(f"SQLAlchemyError in get_room_name: {e}")
    except Exception as e:
        add_log(f"Exception in get_room_name: {e}")


def get_txt_in_cb(h_m, call, session):
    user = get_user(call, session)
    h, m = h_m
    if m == 45:
        txt = f"{h}:{m}-{h + 1}"
    elif m == 0:
        txt = f"{h}-{h}:{m + 15}"
    else:
        txt = f"{h}:{m}-{h}:{m + 15}"
    txt = change_num_as_lang(txt, user.language)
    return txt


def get_reserved_hours(call, session):
    try:
        room, date = get_room_date_as_call(call)
        reserved_rows = session.query(Reservations).filter_by(room_id=room, date=date, status=CONFIRMED).all()
        reserved_times = [(row.start_time, row.end_time, row.date) for row in reserved_rows]
        reserved_hours = get_reserved_hours_as_query(reserved_times)
        return reserved_hours
    except Exception as e:
        add_log(f"Exception in get_reserved_hours: {e}")


def get_room_date_as_call(call):
    try:
        call_list = call.data.split("_")
        if len(call_list) > 3:
            room, date = call_list[3], call_list[2]
        else:
            room, date = call_list[1], call_list[2]
        return room, date
    except Exception as e:
        add_log(f"Exception in get_room_date_as_call: {e}")


def get_reserved_hours_as_query(reserved_times):
    reserved_hours = []
    now = dt.now(tehran_tz)
    for s_e in reserved_times:
        start, end = s_e[0], s_e[1]
        end_time = get_date_obj(s_e[2], end)
        s_hour, s_min = int(start.split(":")[0]), int(start.split(":")[1])
        e_hour, e_min = int(end.split(":")[0]), int(end.split(":")[1])
        s_time_min = (60 * s_hour) + s_min
        e_time_min = (60 * e_hour) + e_min
        for h in range(s_hour, e_hour + 1):
            for m in range(0, 60 + 1, 15):
                time_min = (60 * h) + m
                condition = get_condition([s_time_min, time_min, e_time_min])
                if condition and now < end_time:
                    h_m = f"{str(h).zfill(2)}:{str(m).zfill(2)}"
                    str_hour = h_m if m != 60 else f"{str(h + 1).zfill(2)}:00"
                    reserved_hours.append(str_hour)
                else:
                    pass
    return reserved_hours


def get_condition(s_t_e):
    s_time_min, time_min, e_time_min = s_t_e
    return s_time_min <= time_min < e_time_min


def get_date_in_db(call, session):
    try:
        room, user_id, date, s_time, e_time = get_data_in_process_button(call, session)
        return session.query(Reservations).filter(
            (Reservations.room_id == room) &
            (Reservations.user_id == user_id) &
            (Reservations.date == date) &
            (Reservations.status != CONFIRMED)
        ).first()
    except SQLAlchemyError as e:
        add_log(f"SQLAlchemyError in get_date_in_db: {e}")
    except Exception as e:
        add_log(f"Exception in get_date_in_db: {e}")


def get_hour_buttons(call, session):
    date_in_db, db_status = get_date_and_status(call, session)
    hours, reserved_hours = get_hours_and_reserved(call, session, date_in_db)
    room, date = get_room_date_as_call(call)
    markup, buttons = InlineKeyboardMarkup(row_width=2), []
    for h in range(8, 21):
        for m in range(0, 46, 15):
            time = f"{h:02}:{m:02}"
            cb = get_callbacks(date, room, time)
            if time in reserved_hours:
                buttons.append(btn(text="🟨", callback_data=f"who_{date}_{room}_{time}"))
            elif db_status == FIRST or db_status == SECOND:
                buttons.append(
                    get_new_buttons(
                        [db_status, time, hours, reserved_hours, get_txt_in_cb([h, m], call, session), cb, call.id]))
            else:
                buttons.append(btn(text=get_txt_in_cb([h, m], call, session), callback_data=cb[0]))
            if len(buttons) == 2:
                markup.row(*buttons)
                buttons = []
    if buttons:
        markup.row(*buttons)
    return markup


def get_date_and_status(call, session):
    try:
        call_list = call.data.split("_")
        if len(call_list) <= 3:
            return None, None
        date_in_db = get_date_in_db(call, session)
        db_status = None if date_in_db is None else date_in_db.status
        return date_in_db, db_status
    except Exception as e:
        add_log(f"Exception in get_date_and_status: {e}")


def get_hours_and_reserved(call, session, date_in_db):
    try:
        hours = [] if date_in_db is None else get_hours_as_db_status(date_in_db)
        reserved_hours = get_reserved_hours(call, session)
        return hours, reserved_hours
    except Exception as e:
        add_log(f"Exception in get_hours_and_reserved: {e}")


def get_hours_as_db_status(date_in_db):
    if date_in_db.status == FIRST:
        hours = [date_in_db.start_time]
    else:
        reserved_times = [(date_in_db.start_time, date_in_db.end_time, date_in_db.date)]
        hours = get_reserved_hours_as_query(reserved_times)
    return hours


def get_reserved_hours_as_db_status(reserved_times):
    reserved_hours = []
    for s_e in reserved_times:
        start, end = s_e[0], s_e[1]
        s_hour, s_min = int(start.split(":")[0]), int(start.split(":")[1])
        e_hour, e_min = int(end.split(":")[0]), int(end.split(":")[1])
        start_time_as_min = (60 * s_hour) + s_min
        end_time_as_min = (60 * e_hour) + e_min
        for h in range(s_hour, e_hour + 1):
            for m in range(0, 60 + 1, 15):
                time_as_min = (60 * h) + m
                if start_time_as_min <= time_as_min < end_time_as_min:
                    h_m = f"{str(h).zfill(2)}:{str(m).zfill(2)}"
                    str_hour = h_m if m != 60 else f"{str(h + 1).zfill(2)}:00"
                    reserved_hours.append(str_hour)
                else:
                    pass
    return reserved_hours


def get_new_buttons(data):
    db_status, str_time, hours = data[0], data[1], data[2]
    reserved_hours, txt, callback, call_id = data[3], data[4], data[5], data[6]
    select_cb, remove_cb = callback[0], callback[1]
    if db_status == FIRST and str_time in hours:
        return btn(text="▶️", callback_data=remove_cb)
    elif db_status == SECOND and str_time == hours[0]:
        return btn(text="▶️", callback_data=remove_cb)
    elif db_status == SECOND and str_time == hours[-1]:
        return btn(text="◀️", callback_data=remove_cb)
    elif db_status == SECOND and str_time in hours:
        return btn(text="✅", callback_data=select_cb)
    else:
        return btn(text=txt, callback_data=select_cb)


def get_callbacks(date, room, str_time):
    select_cb = f"time_select_{date}_{room}_{str_time}"
    remove_cb = f"time_remove_{date}_{room}_{str_time}"
    return [select_cb, remove_cb]


def get_date_query_in_add_time(call, session):
    try:
        room, user_id, date, s_time, e_time = get_data_in_process_button(call, session)
        return session.query(Reservations).filter_by(room_id=room, user_id=user_id, date=date).all()
    except SQLAlchemyError as e:
        add_log(f"SQLAlchemyError in get_date_query_in_add_time: {e}")
    except Exception as e:
        add_log(f"Exception in get_date_query_in_add_time: {e}")


def get_data_in_process_button(call, session):
    try:
        chat_id = str(call.message.chat.id)
        call_list = call.data.split("_")
        date, room, s_time = call_list[2], call_list[3], call_list[4]
        e_time = get_end_time(s_time)
        user_id = session.query(Users).filter_by(chat_id=chat_id).first().id
        return room, user_id, date, s_time, e_time
    except SQLAlchemyError as e:
        add_log(f"SQLAlchemyError in get_data_in_process_button: {e}")
    except Exception as e:
        add_log(f"Exception in get_data_in_process_button: {e}")


def get_end_time(s_time):
    s_hour, s_min = s_time.split(":")
    s_hour, s_min = int(s_hour), int(s_min)
    if s_min == 45:
        return f"{str(s_hour + 1).zfill(2)}:00"
    else:
        return f"{str(s_hour).zfill(2)}:{str(s_min + 15).zfill(2)}"


def get_reservation_in_confirm(call, session):
    try:
        room, date = get_room_date_as_call(call)
        user = get_user(call, session)
        return session.query(Reservations).filter(
            (Reservations.room_id == room) &
            (Reservations.user_id == user.id) &
            (Reservations.date == date) &
            ((Reservations.status == FIRST) | (Reservations.status == SECOND))
        ).first()
    except SQLAlchemyError as e:
        add_log(f"SQLAlchemyError in get_reservation_in_confirm: {e}")
    except Exception as e:
        add_log(f"Exception in get_reservation_in_confirm: {e}")


def get_data_in_create_image(reserve, session):
    user = session.query(Users).filter_by(id=reserve.user_id).first()
    return user.name, reserve.date, reserve.start_time, reserve.end_time, user.color


def generate_random_hex_color():
    red = random.randint(0, 255)
    green = random.randint(0, 255)
    blue = random.randint(0, 255)
    hex_color = "#{:02x}{:02x}{:02x}".format(red, green, blue)

    return hex_color


def set_end_time_in_process_start(e_min, e_hour, reserve):
    if e_min == 45:
        reserve.end_time = f"{str(e_hour + 1).zfill(2)}:00"
    else:
        reserve.end_time = f"{str(e_hour).zfill(2)}:{str(e_min + 15).zfill(2)}"


def calc_duration(s_in_min, e_in_min):
    if e_in_min - s_in_min < 240:
        return True
    else:
        return False


def get_second_data_in_start(e_time_call, session, reserve):
    e_time, call = e_time_call
    e_hour, e_min = int(e_time.split(":")[0]), int(e_time.split(":")[1])
    s_time = reserve.start_time
    s_hour, s_min = int(s_time.split(":")[0]), int(s_time.split(":")[1])
    user = get_user(call, session)
    is_admin = True if user.username in admins else False
    s_in_min, e_in_min = (60 * s_hour) + s_min, (60 * e_hour) + e_min
    ok_duration = calc_duration(s_in_min, e_in_min)
    return s_in_min, e_in_min, e_min, e_hour, ok_duration, is_admin


def future_date(reserve):
    end_time = f"{reserve.date} {reserve.end_time}"
    reserve_date = dt.strptime(end_time, "%Y-%m-%d %H:%M")
    reserve_date = tehran_tz.localize(reserve_date)
    current_date = dt.now(tehran_tz)
    return reserve_date > current_date


def get_start_in_edit_data_one(call, session, reserve):
    e_time = call.data.split("_")[3]
    s_time = reserve.start_time
    reserved_times = [(s_time, e_time, reserve.date)]
    hours = get_reserved_hours_as_query(reserved_times)
    reserved_hours = get_reserved_hours_in_edit(call, session)
    return hours, reserved_hours


def get_hour_buttons_in_edit(call, session):
    hours, reserved_hours = get_hours_and_reserved_in_edit(call, session)
    markup, buttons = InlineKeyboardMarkup(row_width=2), []
    for h in range(8, 21):
        for m in range(0, 46, 15):
            time = f"{h:02}:{m:02}"
            cb = get_callbacks_in_edit(call, time)
            if time in reserved_hours:
                date, room = get_date_room_from_db_id(call, session)
                buttons.append(btn(text="🟨", callback_data=f"who_{date}_{room}_{time}"))
            elif hours and time == hours[0]:
                buttons.append(btn(text="▶️", callback_data=cb[1]))
            elif hours and len(hours) > 1 and time == hours[-1]:
                buttons.append(btn(text="◀️", callback_data=cb[1]))
            elif time in hours:
                buttons.append(btn(text="✅", callback_data=cb[0]))
            else:
                buttons.append(btn(text=get_txt_in_cb([h, m], call, session), callback_data=cb[0]))
            if len(buttons) == 2:
                markup.row(*buttons)
                buttons = []
    if buttons:
        markup.row(*buttons)
    return markup


def get_hours_and_reserved_in_edit(call, session):
    try:
        db_id = call.data.split("_")[2]
        reserve = session.query(Reservations).filter_by(id=db_id).first()
        hours = [] if reserve.status is None else get_hours_as_db_status_in_edit(call, session)
        reserved_hours = get_reserved_hours_in_edit(call, session)
        return hours, reserved_hours
    except Exception as e:
        add_log(f"Exception in get_hours_and_reserved_in_edit: {e}")


def get_callbacks_in_edit(call, str_time):
    db_id = call.data.split("_")[2]
    select_cb = f"e-t_select_{db_id}_{str_time}"
    remove_cb = f"e-t_remove_{db_id}_{str_time}"
    return [select_cb, remove_cb]


def get_date_room_from_db_id(call, session):
    db_id = call.data.split("_")[2]
    reserve = session.query(Reservations).filter_by(id=db_id).first()
    return reserve.date, reserve.room_id


def get_hours_as_db_status_in_edit(call, session):
    db_id = call.data.split("_")[2]
    reserve = session.query(Reservations).filter_by(id=db_id).first()
    if reserve.status == FIRST:
        hours = [reserve.start_time]
    else:
        reserved_times = [(reserve.start_time, reserve.end_time, reserve.date)]
        hours = get_reserved_hours_as_query(reserved_times)
    return hours


def get_reserved_hours_in_edit(call, session):
    db_id = call.data.split("_")[2]
    reserve = session.query(Reservations).filter_by(id=db_id).first()
    reserved_rows = session.query(Reservations).filter(
        (Reservations.id != db_id) &
        (Reservations.room_id == reserve.room_id) &
        (Reservations.date == reserve.date) &
        (Reservations.status == CONFIRMED)
    ).all()
    reserved_times = [(row.start_time, row.end_time, row.date) for row in reserved_rows]
    reserved_hours = get_reserved_hours_as_query(reserved_times)
    return reserved_hours


def get_past_reserves(chat_id, session):
    user = session.query(Users).filter_by(chat_id=str(chat_id)).first()
    reserves = session.query(Reservations).filter_by(user_id=user.id, status=CONFIRMED).all()
    past_reserves = [reserve for reserve in reserves if not future_date(reserve)]
    sorted_reserves = sorted(past_reserves,
                             key=lambda reserve: dt.strptime(f"{reserve.date} {reserve.start_time}", "%Y-%m-%d %H:%M"))
    sorted_reserves = list(reversed(sorted_reserves))
    return sorted_reserves


def get_start_end_paginate(page, past_reserves):
    items_per_page = 8
    start_idx = page * items_per_page
    end_idx = start_idx + items_per_page
    paginated_reserves = past_reserves[start_idx:end_idx]
    return start_idx, end_idx, paginated_reserves


def get_txt_markup_in_past_reservations(past_reserves, txt_2, user):
    if len(past_reserves) > 0:
        txt = get_text(BotText.PAST_RESERVATIONS_HEADER, user.language) + txt_2
    else:
        txt = get_text(BotText.NO_PAST_RESERVATIONS_TEXT, user.language)
    markup = InlineKeyboardMarkup()
    return txt, markup


def get_future_text(call, session):
    user = get_user(call, session)
    confs = session.query(Reservations).filter_by(user_id=user.id, status=CONFIRMED).all()
    future_reserves = [reserve for reserve in confs if future_date(reserve)]
    sorted_reserves = sorted(future_reserves,
                             key=lambda reserve: dt.strptime(f"{reserve.date} {reserve.start_time}", "%Y-%m-%d %H:%M"))
    txt_2 = ""
    for reserve in sorted_reserves:
        room_name = get_room_name(reserve.room_id, session)
        weekday = dt.strptime(reserve.date, "%Y-%m-%d").strftime("%A")
        date = reserve.date if user.language == "en" else gregorian_to_jalali(reserve.date)
        weekday = weekday if user.language == "en" else day_in_persian[weekday]
        txt_2 += get_text(BotText.ADD_TIME_SECOND_STATUS, user.language).format(
            date=date, weekday=weekday, room_name=room_name, start_time=reserve.start_time,
            end_time=reserve.end_time
        ) + "\n\n"
    return txt_2


def get_date_obj(date, time_str):
    the_time = dt.strptime(time_str, "%H:%M")
    the_time += timedelta(minutes=1)
    the_time = the_time.strftime("%H:%M")
    dt_time = dt.strptime(f"{date} {the_time}", "%Y-%m-%d %H:%M")
    return tehran_tz.localize(dt_time)
