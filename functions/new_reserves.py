from datetime import datetime as dt

import pytz
from sqlalchemy.exc import SQLAlchemyError
from telebot.apihelper import ApiTelegramException
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton as btn

from functions.get_functions import get_room_name, get_room_date_as_call, create_date_buttons, get_date_in_db, \
    get_data_in_process_button, get_reservation_in_confirm, get_hour_buttons, get_date_query_in_add_time, \
    get_reserved_hours, get_reserved_hours_as_query, get_end_time, set_end_time_in_process_start, \
    get_second_data_in_start, get_date_obj
from models.reservations import Reservations
from models.rooms import Rooms
from models.users import Users
from services.config import BACK_DATE, change_command_to_none, CONFIRMED, FIRST, SECOND, BACK_MAIN, gregorian_to_jalali, \
    day_in_persian, get_user
from services.language import BotText, get_text, change_num_as_lang
from services.log import add_log

tehran_tz = pytz.timezone("Asia/Tehran")


def process_reservation(message, session, bot):
    try:
        user = get_user(message, session)
        txt = get_text(BotText.RESERVATION_TEXT, user.language)
        btn1 = get_text(BotText.NEW_RESERVATION_BUTTON, user.language)
        btn2 = get_text(BotText.MY_RESERVATIONS_BUTTON, user.language)
        markup = InlineKeyboardMarkup()
        markup.add(btn(text=btn1, callback_data="new_reservation"))
        markup.add(btn(text=btn2, callback_data="user_reservations"))
        if user.command == BACK_MAIN:
            msg_id = message.id
            bot.edit_message_text(chat_id=int(user.chat_id), message_id=msg_id, text=txt, reply_markup=markup)
            change_command_to_none(user, session)
        else:
            bot.send_message(chat_id=int(user.chat_id), text=txt, reply_markup=markup)
    except Exception as e:
        add_log(f"Exception in process_reservation: {e}")


def process_new_reservation(call, session, bot):
    try:
        msg_id = call.message.id
        user = get_user(call, session)
        txt = get_text(BotText.CHOOSE_DATE_TEXT, user.language)
        key = create_date_buttons('room', user)
        key.add(btn(text=get_text(BotText.BACK_BUTTON, user.language), callback_data="backmain"))
        if user.command == BACK_DATE:
            change_command_to_none(user, session)
        bot.edit_message_text(chat_id=int(user.chat_id), message_id=msg_id, text=txt, reply_markup=key)
    except Exception as e:
        add_log(f"Exception in process_new_reservation: {e}")


def process_back_main(call, session, bot):
    try:
        user = get_user(call, session)
        user.command = BACK_MAIN
        session.commit()
        return process_reservation(call.message, session, bot)
    except SQLAlchemyError as e:
        add_log(f"SQLAlchemyError in process_back_main: {e}")
    except Exception as e:
        add_log(f"Exception in process_back_main: {e}")


def process_select_room(call, session, bot):
    try:
        msg_id = call.message.id
        date = call.data.split("_")[1]
        weekday = dt.strptime(date, "%Y-%m-%d").strftime("%A")
        user = get_user(call, session)
        date = date if user.language == "en" else gregorian_to_jalali(date)
        weekday = weekday if user.language == "en" else day_in_persian[weekday]
        txt = get_text(BotText.ROOM_SELECTION_TEXT, user.language).format(date=date, weekday=weekday)
        txt = change_num_as_lang(txt, user.language)
        markup = add_room_buttons(call, session)
        bot.edit_message_text(chat_id=int(user.chat_id), message_id=msg_id, text=txt, reply_markup=markup)
    except Exception as e:
        add_log(f"Exception in process_select_room: {e}")


def add_room_buttons(call, session):
    date = call.data.split("_")[1]
    rooms = session.query(Rooms).all()
    markup = InlineKeyboardMarkup()
    for room in rooms:
        markup.add(btn(text=f"{room.name}", callback_data=f"dt_{room.id}_{date}"))
    user = session.query(Users).filter_by(chat_id=str(call.message.chat.id)).first()
    markup.add(btn(text=get_text(BotText.BACK_BUTTON, user.language), callback_data="backdate"))
    return markup


def process_back_date(call, session, bot):
    try:
        user = get_user(call, session)
        user.command = BACK_DATE
        session.commit()
        return process_new_reservation(call, session, bot)
    except SQLAlchemyError as e:
        add_log(f"SQLAlchemyError in process_back_date: {e}")
    except Exception as e:
        add_log(f"Exception in process_back_date: {e}")


def process_hour_selection(call, session, bot):
    try:
        msg_id = call.message.id
        call_list = call.data.split("_")
        room, date = int(call_list[1]), call_list[2]
        weekday = dt.strptime(date, "%Y-%m-%d").strftime("%A")
        delete_status_select_end(call, session)
        room_name = get_room_name(room, session)
        user = get_user(call, session)
        date = date if user.language == "en" else gregorian_to_jalali(date)
        weekday = weekday if user.language == "en" else day_in_persian[weekday]
        txt = get_text(BotText.HOUR_SELECTION_TEXT, user.language).format(date=date, weekday=weekday,
                                                                          room_name=room_name)
        txt = change_num_as_lang(txt, user.language)
        key = create_hour_buttons(call, session)
        bot.edit_message_text(chat_id=int(user.chat_id), message_id=msg_id, text=txt, reply_markup=key)
    except Exception as e:
        add_log(f"Exception in process_hour_selection: {e}")


def delete_status_select_end(call, session):
    try:
        call_list = call.data.split("_")
        if len(call_list) > 3:
            room, date = call_list[3], call_list[2]
        else:
            room, date = call_list[1], call_list[2]
        user = get_user(call, session)
        all_reserves = session.query(Reservations).filter_by(user_id=user.id, date=date, room_id=room).all()
        for reserve in all_reserves:
            if reserve.status != CONFIRMED:
                session.delete(reserve)
        session.commit()
    except SQLAlchemyError as e:
        add_log(f"SQLAlchemyError in delete_status_select_end: {e}")
    except Exception as e:
        add_log(f"Exception in delete_status_select_end: {e}")


def create_hour_buttons(call, session):
    room, date = get_room_date_as_call(call)
    markup = get_hour_buttons(call, session)
    user = session.query(Users).filter_by(chat_id=str(call.message.chat.id)).first()
    markup.add(btn(text=get_text(BotText.CONFIRM_BUTTON, user.language), callback_data=f"confirm-hours_{room}_{date}"))
    markup.add(btn(text=get_text(BotText.BACK_BUTTON, user.language), callback_data=f"room_{date}"))
    return markup


def process_add_time(call, session, bot):
    msg_id = call.message.id
    user = get_user(call, session)
    try:
        call_list = call.data.split("_")
        date, room, str_time = call_list[2], int(call_list[3]), call_list[4]
        room_name = get_room_name(room, session)
        weekday = dt.strptime(date, "%Y-%m-%d").strftime("%A")
        process_hour_as_status(call, session, bot)
        date_in_db = get_date_in_db(call, session)
        date = date if user.language == "en" else gregorian_to_jalali(date)
        weekday = weekday if user.language == "en" else day_in_persian[weekday]
        if date_in_db and date_in_db.status == FIRST:
            txt = get_text(BotText.ADD_TIME_FIRST_STATUS, user.language).format(
                date=date, weekday=weekday, room_name=room_name, start_time=date_in_db.start_time,
                end_time=date_in_db.end_time
            )
        elif date_in_db and date_in_db.status == SECOND:
            txt = get_text(BotText.ADD_TIME_SECOND_STATUS, user.language).format(
                date=date, weekday=weekday, room_name=room_name, start_time=date_in_db.start_time,
                end_time=date_in_db.end_time
            )
        else:
            txt = get_text(BotText.ADD_TIME_DEFAULT, user.language).format(date=date, weekday=weekday,
                                                                           room_name=room_name)
        txt = change_num_as_lang(txt, user.language)
        key = create_hour_buttons(call, session)
        bot.edit_message_text(chat_id=int(user.chat_id), message_id=msg_id, text=txt, reply_markup=key)
    except ApiTelegramException:
        bot.answer_callback_query(call.id, get_text(BotText.INVALID_TIME_ALERT, user.language), show_alert=True)
    except Exception as e:
        add_log(f"Exception in process_add_time: {e}")


def process_hour_as_status(call, session, bot):
    reserves = get_date_query_in_add_time(call, session)
    for reserve in reserves:
        if reserve.status == FIRST:
            return process_start_hour(call, session, [reserve, bot])
        elif reserve.status == SECOND:
            return process_end_hour(call, session, [reserve, bot])
    else:
        return add_new_date_to_db(call, session, bot)


def process_start_hour(call, session, reserve_bot):
    try:
        reserve, bot = reserve_bot
        hours, reserved_hours = get_start_hour_data_one(call, session, reserve)
        user = get_user(call, session)
        for hour in hours:
            if hour in reserved_hours:
                bot.answer_callback_query(call.id, get_text(BotText.INVALID_RESERVED_TIMES, user.language),
                                          show_alert=True)
                break
        else:
            s_in_min, e_in_min, e_min, e_hour, ok_duration, is_admin = get_second_data_in_start(
                [call.data.split("_")[4], call], session, reserve)
            if s_in_min < e_in_min and (ok_duration or is_admin):
                set_end_time_in_process_start(e_min, e_hour, reserve)
                reserve.status = SECOND
                session.commit()
            elif s_in_min < e_in_min:
                bot.answer_callback_query(call.id, change_num_as_lang(get_text(BotText.INVALID_DURATION, user.language),
                                                                      user.language), show_alert=True)
    except SQLAlchemyError as e:
        add_log(f"SQLAlchemyError in process_start_hour: {e}")
    except Exception as e:
        add_log(f"Exception in process_start_hour: {e}")


def process_end_hour(call, session, reserve_bot):
    try:
        reserve, bot = reserve_bot
        user = get_user(call, session)
        room, user_id, date, selected_time, e_time = get_data_in_process_button(call, session)
        now_time = dt.now(tehran_tz)
        dt_time = dt.strptime(f"{date} {get_end_time(selected_time)}", "%Y-%m-%d %H:%M")
        dt_time = tehran_tz.localize(dt_time)
        if dt_time > now_time:
            session.delete(reserve)
            add_new_date_to_db(call, session, bot)
        else:
            bot.answer_callback_query(call.id, get_text(BotText.INVALID_PAST_TIMES, user.language), show_alert=True)
    except SQLAlchemyError as e:
        add_log(f"SQLAlchemyError in process_end_hour: {e}")
    except Exception as e:
        add_log(f"Exception in process_end_hour: {e}")


def add_new_date_to_db(call, session, bot):
    try:
        room, user_id, date, selected_time, e_time = get_data_in_process_button(call, session)
        user = get_user(call, session)
        now_time = dt.now(tehran_tz)
        dt_time = dt.strptime(f"{date} {get_end_time(selected_time)}", "%Y-%m-%d %H:%M")
        dt_time = tehran_tz.localize(dt_time)
        if dt_time > now_time:
            new_date = Reservations(room_id=room, user_id=user_id, date=date, start_time=selected_time, end_time=e_time,
                                    status=FIRST)
            session.add(new_date)
            session.commit()
        else:
            bot.answer_callback_query(call.id, get_text(BotText.INVALID_PAST_TIMES, user.language), show_alert=True)
    except SQLAlchemyError as e:
        add_log(f"SQLAlchemyError in add_new_date_to_db: {e}")
    except Exception as e:
        add_log(f"Exception in add_new_date_to_db: {e}")


def get_start_hour_data_one(call, session, reserve):
    e_time = call.data.split("_")[4]
    s_time = reserve.start_time
    reserved_times = [(s_time, e_time, reserve.date)]
    hours = get_reserved_hours_as_query(reserved_times)
    reserved_hours = get_reserved_hours(call, session)
    return hours, reserved_hours


def process_remove_time(call, session, bot):
    try:
        msg_id = call.message.id
        user = get_user(call, session)
        room, user_id, date, selected_time, e_time = get_data_in_process_button(call, session)
        room_name = get_room_name(room, session)
        weekday = dt.strptime(date, "%Y-%m-%d").strftime("%A")
        date = date if user.language == "en" else gregorian_to_jalali(date)
        weekday = weekday if user.language == "en" else day_in_persian[weekday]
        date_in_db = get_date_in_db(call, session)
        if selected_time == date_in_db.start_time:
            delete_status_select_end(call, session)
            txt = get_text(BotText.HOUR_SELECTION_TEXT, user.language).format(date=date, weekday=weekday,
                                                                              room_name=room_name)
        elif get_end_time(selected_time) == date_in_db.end_time:
            date_in_db.end_time = get_end_time(date_in_db.start_time)
            date_in_db.status = FIRST
            session.commit()
            txt = get_text(BotText.ADD_TIME_FIRST_STATUS, user.language).format(
                date=date, weekday=weekday, room_name=room_name, start_time=date_in_db.start_time,
                end_time=date_in_db.end_time
            )
        else:
            delete_status_select_end(call, session)
            txt = get_text(BotText.HOUR_SELECTION_TEXT, user.language).format(date=date, weekday=weekday,
                                                                              room_name=room_name)
        txt = change_num_as_lang(txt, user.language)
        key = create_hour_buttons(call, session)
        bot.edit_message_text(chat_id=int(user.chat_id), message_id=msg_id, text=txt, reply_markup=key)
    except Exception as e:
        add_log(f"Exception in process_remove_time: {e}")


def process_confirm_selection(call, session, bot):
    try:
        msg_id = call.message.id
        reserve = get_reservation_in_confirm(call, session)
        user = get_user(call, session)
        if reserve and reserve.status:
            reserve.status = CONFIRMED
            session.commit()
            room_name = get_room_name(reserve.room_id, session)
            weekday = dt.strptime(reserve.date, "%Y-%m-%d").strftime("%A")
            date = reserve.date if user.language == "en" else gregorian_to_jalali(reserve.date)
            weekday = weekday if user.language == "en" else day_in_persian[weekday]
            txt = get_text(BotText.CONFIRM_RESERVATION_TEXT, user.language).format(
                date=date, weekday=weekday, room_name=room_name, start_time=reserve.start_time,
                end_time=reserve.end_time
            )
            txt = change_num_as_lang(txt, user.language)
            bot.edit_message_text(chat_id=int(user.chat_id), message_id=msg_id, text=txt)
        else:
            bot.answer_callback_query(call.id, get_text(BotText.INCOMPLETE_HOURS_ALERT, user.language), show_alert=True)
    except SQLAlchemyError as e:
        add_log(f"SQLAlchemyError in process_confirm_selection: {e}")
    except Exception as e:
        add_log(f"Exception in process_confirm_selection: {e}")


def process_who_reserved(call, session, bot):
    try:
        call_list = call.data.split("_")
        user = get_user(call, session)
        date, room, hour = call_list[1], call_list[2], call_list[3]
        reserves = session.query(Reservations).filter_by(date=date, room_id=room, status=CONFIRMED).all()
        reserved_times = [(row.start_time, row.end_time, row.user_id) for row in reserves]
        reserved_hours = get_reserved_hours_in_who_reserved(reserved_times)
        name = None
        for reserve in reserved_hours:
            if hour in reserve[0]:
                name = session.query(Users).filter_by(id=int(reserve[1])).first().name
                break
        bot.answer_callback_query(call.id, get_text(BotText.WHO_RESERVED, user.language).format(name=name),
                                  show_alert=True)
    except Exception as e:
        add_log(f"Exception in process_who_reserved: {e}")


def get_reserved_hours_in_who_reserved(reserved_times):
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
                    reserved_hours.append((str_hour, s_e[2]))
                else:
                    pass
    return reserved_hours
