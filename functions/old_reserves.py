from datetime import datetime as dt

import pytz
from sqlalchemy.exc import SQLAlchemyError
from telebot.apihelper import ApiTelegramException
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton as btn

from functions.get_functions import get_room_name, get_start_end_week_date, add_free_buttons, \
    get_end_time, admins, calc_duration, get_second_data_in_start, \
    set_end_time_in_process_start, future_date, get_start_in_edit_data_one, get_hour_buttons_in_edit, get_date_buttons, \
    get_past_reserves, get_start_end_paginate, get_txt_markup_in_past_reservations, get_future_text
from models.reservations import Reservations
from models.rooms import Rooms
from models.users import Users
from services.config import change_command_to_none, CONFIRMED, BACK_USER, FIRST, SECOND
from services.log import add_log

tehran_tz = pytz.timezone("Asia/Tehran")


def process_user_reservations(call, session, bot):
    try:
        chat_id, msg_id = str(call.message.chat.id), call.message.id
        user = session.query(Users).filter_by(chat_id=chat_id).first()
        reserves = session.query(Reservations).filter_by(user_id=user.id, status=CONFIRMED).all()
        markup, row = InlineKeyboardMarkup(row_width=2), []
        if len(reserves) > 0:
            txt = "View upcoming reservations with «🗓 Future» or past reservations using «🔍 Past»"
            row.append(btn(text="🗓 Future", callback_data="future"))
            row.append(btn(text="🔍 Past", callback_data="past_reservations_0"))
            markup.row(*row)
        else:
            txt = "You haven’t made any Reservations yet 🙁"
        markup.add(btn(text="⬅️ Back", callback_data="backmain"))
        if user.command == BACK_USER:
            change_command_to_none(user, session)
        bot.edit_message_text(chat_id=chat_id, message_id=msg_id, text=txt, reply_markup=markup)
    except Exception as e:
        add_log(f"Exception in process_user_reservations: {e}")


def process_future_reservations(call, session, bot):
    try:
        chat_id, msg_id = str(call.message.chat.id), call.message.id
        txt_2 = get_future_text(call, session)
        markup = InlineKeyboardMarkup()
        if len(txt_2) > 0:
            txt = "🗓 Your Future Reservations are:\n\n" + txt_2
            markup.add(btn(text="✏️ Edit Reservations", callback_data="editreservation"))
            markup.add(btn(text="🗑 Delete Reservations", callback_data="deletereservation"))
        else:
            txt = "You don't have any Future Reservation 🤲🏻"
        markup.add(btn(text="⬅️ Back", callback_data="backuser"))
        bot.edit_message_text(chat_id=chat_id, message_id=msg_id, text=txt, reply_markup=markup)
    except Exception as e:
        add_log(f"Exception in process_future_reservations: {e}")


def process_edit_reservations(call, session, bot):
    try:
        chat_id, msg_id = str(call.message.chat.id), call.message.id
        uid = session.query(Users).filter_by(chat_id=chat_id).first().id
        confs = session.query(Reservations).filter_by(user_id=uid, status=CONFIRMED).all()
        future_reserves = [reserve for reserve in confs if future_date(reserve)]
        txt = "📝 Choose the Reservation you'd like to edit:"
        markup = InlineKeyboardMarkup()
        for reserve in future_reserves:
            date, str_hour = reserve.date, f"{reserve.start_time}-{reserve.end_time}"
            t = f"📅 {date[5:7]}/{date[7:]}  {str_hour}"
            markup.add(btn(text=t, callback_data=f"e_r_{reserve.id}"))
        markup.add(btn(text="⬅️ Back", callback_data="backfuture"))
        bot.edit_message_text(chat_id=chat_id, message_id=msg_id, text=txt, reply_markup=markup)
    except Exception as e:
        add_log(f"Exception in process_edit_reservations: {e}")


def process_edit_specific_reservation(call, session, bot):
    try:
        chat_id, msg_id = str(call.message.chat.id), call.message.id
        db_id = call.data.split("_")[2]
        reserve = session.query(Reservations).filter_by(id=db_id).first()
        room_name = get_room_name(reserve.room_id, session)
        weekday = dt.strptime(reserve.date, "%Y-%m-%d").strftime("%A")
        txt = f'📅 Date: {reserve.date} ({weekday})\n🚪 Room: {room_name}\n▶️ From: {reserve.start_time}\n◀️ To: {reserve.end_time}'
        markup = InlineKeyboardMarkup()
        markup.add(btn(text="📅 Edit Date", callback_data=f"e_date_{reserve.id}"))
        markup.add(btn(text="🚪 Edit Room", callback_data=f"e_room_{reserve.id}"))
        markup.add(btn(text="🕰 Edit Hours", callback_data=f"e_hours_{reserve.id}"))
        markup.add(btn(text="⬅️ Back", callback_data="backedit"))
        bot.edit_message_text(chat_id=chat_id, message_id=msg_id, text=txt, reply_markup=markup)
    except Exception as e:
        add_log(f"Exception in process_edit_specific_reservation: {e}")


def process_edit_specific_date(call, session, bot):
    try:
        chat_id, msg_id = str(call.message.chat.id), call.message.id
        db_id = call.data.split("_")[2]
        reserve = session.query(Reservations).filter_by(id=db_id).first()
        room_name = get_room_name(reserve.room_id, session)
        txt = f'🚪 Room: {room_name}\n▶️ From: {reserve.start_time}\n◀️ To: {reserve.end_time}\n❓ Date:'
        markup = create_date_buttons_in_edit(db_id)
        bot.edit_message_text(chat_id=chat_id, message_id=msg_id, text=txt, reply_markup=markup)
    except Exception as e:
        add_log(f"Exception in process_edit_specific_date: {e}")


def create_date_buttons_in_edit(db_id):
    start_date, end_date, days_of_week = get_start_end_week_date()
    markup = add_row_buttons_in_edit([start_date, end_date, days_of_week], db_id)
    return markup


def add_row_buttons_in_edit(start_end_days, db_id):
    row, markup = get_date_buttons(start_end_days, db_id)
    markup = add_free_buttons(row, markup)
    markup.add(btn(text="⬅️ Back", callback_data=f"backspecific__{db_id}"))
    return markup


def process_set_edit_date(call, session, bot):
    try:
        date, db_id = call.data.split("_")[3], int(call.data.split("_")[2])
        reserve = session.query(Reservations).filter_by(id=db_id).first()
        reserve.date = date
        session.commit()
        return process_edit_specific_reservation(call, session, bot)
    except Exception as e:
        add_log(f"Exception in process_set_edit_date: {e}")


def process_edit_specific_room(call, session, bot):
    try:
        chat_id, msg_id = str(call.message.chat.id), call.message.id
        db_id = int(call.data.split("_")[2])
        reserve = session.query(Reservations).filter_by(id=db_id).first()
        weekday = dt.strptime(reserve.date, "%Y-%m-%d").strftime("%A")
        txt = f'📅 Date: {reserve.date} ({weekday})\n▶️ From: {reserve.start_time}\n◀️ To: {reserve.end_time}\n❓ Room:'
        markup = add_room_buttons_in_edit(call, session)
        bot.edit_message_text(chat_id=chat_id, message_id=msg_id, text=txt, reply_markup=markup)
    except Exception as e:
        add_log(f"Exception in process_edit_specific_room: {e}")


def add_room_buttons_in_edit(call, session):
    db_id = int(call.data.split("_")[2])
    rooms = session.query(Rooms).all()
    markup = InlineKeyboardMarkup()
    for room in rooms:
        markup.add(btn(text=f"{room.name}", callback_data=f"set_r_{db_id}_{room.id}"))
    markup.add(btn(text="⬅️ Back", callback_data=f"backspecific__{db_id}"))
    return markup


def process_set_edit_room(call, session, bot):
    try:
        room, db_id = int(call.data.split("_")[3]), int(call.data.split("_")[2])
        reserve = session.query(Reservations).filter_by(id=db_id).first()
        reserve.room_id = room
        session.commit()
        return process_edit_specific_reservation(call, session, bot)
    except SQLAlchemyError as e:
        add_log(f"SQLAlchemyError in process_set_edit_room: {e}")
    except Exception as e:
        add_log(f"Exception in process_set_edit_room: {e}")


def process_edit_specific_hours(call, session, bot):
    try:
        chat_id, msg_id = str(call.message.chat.id), call.message.id
        db_id = call.data.split("_")[2]
        reserve = session.query(Reservations).filter_by(id=db_id).first()
        room_name = get_room_name(reserve.room_id, session)
        weekday = dt.strptime(reserve.date, "%Y-%m-%d").strftime("%A")
        txt = f'📅 Date: {reserve.date} ({weekday})\n🚪 Room: {room_name}\n❓ From:'
        key = create_hour_buttons_in_edit(call, session)
        bot.edit_message_text(chat_id=chat_id, message_id=msg_id, text=txt, reply_markup=key)
    except Exception as e:
        add_log(f"Exception in process_edit_specific_hours: {e}")


def create_hour_buttons_in_edit(call, session):
    db_id = int(call.data.split("_")[2])
    markup = get_hour_buttons_in_edit(call, session)
    markup.add(btn(text="🟢 Confirm 🟢", callback_data=f"set_h_{db_id}"))
    return markup


def process_add_time_in_edit(call, session, bot):
    chat_id, msg_id = str(call.message.chat.id), call.message.id
    db_id, str_time = int(call.data.split("_")[2]), call.data.split("_")[3]
    change_status_as_selection(call, session, bot)
    reserve = session.query(Reservations).filter_by(id=db_id).first()
    room_name = get_room_name(reserve.room_id, session)
    weekday = dt.strptime(reserve.date, "%Y-%m-%d").strftime("%A")
    if reserve.status == FIRST:
        txt = f'📅 Date: {reserve.date} ({weekday})\n🚪 Room: {room_name}\n▶️ From: {reserve.start_time}\n◀️ To: {reserve.end_time}\n(You can change the end time)'
    elif reserve.status == SECOND:
        txt = f'📅 Date: {reserve.date} ({weekday})\n🚪 Room: {room_name}\n▶️ From: {reserve.start_time}\n◀️ To: {reserve.end_time}'
    else:
        txt = f'📅 Date: {reserve.date} ({weekday})\n🚪 Room: {room_name}\n❓ From:'
    key = create_hour_buttons_in_edit(call, session)
    try:
        bot.edit_message_text(chat_id=chat_id, message_id=msg_id, text=txt, reply_markup=key)
    except ApiTelegramException:
        bot.answer_callback_query(call.id, "The end time can't be before the start time 🗿", show_alert=True)
    except Exception as e:
        add_log(f"Exception in process_add_time_in_edit: {e}")


def change_status_as_selection(call, session, bot):
    try:
        db_id, str_time = int(call.data.split("_")[2]), call.data.split("_")[3]
        reserve = session.query(Reservations).filter_by(id=db_id).first()
        s_time, e_time = reserve.start_time, reserve.end_time
        now = dt.now(tehran_tz)
        dt_time = dt.strptime(f"{reserve.date} {get_end_time(str_time)}", "%Y-%m-%d %H:%M")
        dt_time = tehran_tz.localize(dt_time)
        db_status = reserve.status
        if db_status == CONFIRMED and str_time == s_time:
            reserve.start_time, reserve.end_time = None, None
            reserve.status = None
            session.commit()
        elif db_status == CONFIRMED and get_end_time(str_time) == e_time:
            reserve.end_time = get_end_time(s_time)
            reserve.status = FIRST
            session.commit()
        elif db_status == CONFIRMED and get_end_time(s_time) == e_time and dt_time > now:
            s_in_min = int(s_time.split(":")[0]) * 60 + int(s_time.split(":")[1])
            e_in_min = int(e_time.split(":")[0]) * 60 + int(e_time.split(":")[1])
            s_dt = dt.strptime(f"{reserve.date} {s_time}", "%Y-%m-%d %H:%M")
            s_dt = tehran_tz.localize(s_dt)
            chat_id = str(call.message.chat.id)
            user = session.query(Users).filter_by(chat_id=chat_id).first()
            is_admin = True if user.username in admins else False
            ok_duration = calc_duration(s_in_min, e_in_min)
            if dt_time > s_dt and (ok_duration or is_admin):
                reserve.end_time = get_end_time(str_time)
                reserve.status = SECOND
                session.commit()
            elif dt_time < s_dt:
                reserve.start_time, reserve.end_time = str_time, get_end_time(str_time)
                reserve.status = FIRST
                session.commit()
            else:
                bot.answer_callback_query(call.id, "The duration must be less than 4 hours ⛔️", show_alert=True)
        elif db_status == CONFIRMED and get_end_time(s_time) == e_time:
            bot.answer_callback_query(call.id, "Only future times can be reserved ⛔️", show_alert=True)
        elif db_status == FIRST:
            process_start_hour_in_edit(call, session, [reserve, bot])
        elif dt_time > now:
            reserve.start_time, reserve.end_time = str_time, get_end_time(str_time)
            reserve.status = FIRST
            session.commit()
        else:
            bot.answer_callback_query(call.id, "Only future times can be reserved ⛔️", show_alert=True)
    except SQLAlchemyError as e:
        add_log(f"SQLAlchemyError in change_status_as_selection: {e}")
    except Exception as e:
        add_log(f"Exception in change_status_as_selection: {e}")


def process_start_hour_in_edit(call, session, reserve_bot):
    try:
        reserve, bot = reserve_bot
        hours, reserved_hours = get_start_in_edit_data_one(call, session, reserve)
        for hour in hours:
            if hour in reserved_hours:
                bot.answer_callback_query(call.id, "Reserved times can't be selected ⛔️", show_alert=True)
                break
        else:
            s_in_min, e_in_min, e_min, e_hour, ok_duration, is_admin = get_second_data_in_start(
                [call.data.split("_")[3], call], session, reserve)
            if s_in_min < e_in_min and (ok_duration or is_admin):
                set_end_time_in_process_start(e_min, e_hour, reserve)
                reserve.status = SECOND
                session.commit()
            elif s_in_min < e_in_min:
                bot.answer_callback_query(call.id, "The duration must be less than 4 hours ⛔️", show_alert=True)
    except SQLAlchemyError as e:
        add_log(f"SQLAlchemyError in process_start_hour_in_edit: {e}")
    except Exception as e:
        add_log(f"Exception in process_start_hour_in_edit: {e}")


def process_remove_time_in_edit(call, session, bot):
    try:
        chat_id, msg_id = str(call.message.chat.id), call.message.id
        db_id, selected_time = int(call.data.split("_")[2]), call.data.split("_")[3]
        reserve = session.query(Reservations).filter_by(id=db_id).first()
        room_name = get_room_name(reserve.room_id, session)
        weekday = dt.strptime(reserve.date, "%Y-%m-%d").strftime("%A")
        txt = None
        if selected_time == reserve.start_time:
            reserve.start_time, reserve.end_time = None, None
            reserve.status = None
            session.commit()
            txt = f'📅 Date: {reserve.date} ({weekday})\n🚪 Room: {room_name}\n❓ From:'
        elif get_end_time(selected_time) == reserve.end_time:
            reserve.end_time = get_end_time(reserve.start_time)
            reserve.status = FIRST
            session.commit()
            txt = f'📅 Date: {reserve.date} ({weekday})\n🚪 Room: {room_name}\n▶️ From: {reserve.start_time}\n◀️ To: {reserve.end_time}\n(You can change the end time)'
        key = create_hour_buttons_in_edit(call, session)
        bot.edit_message_text(chat_id=chat_id, message_id=msg_id, text=txt, reply_markup=key)
    except Exception as e:
        add_log(f"Exception in process_remove_time_in_edit: {e}")


def process_set_edit_hours(call, session, bot):
    try:
        chat_id, msg_id = str(call.message.chat.id), call.message.id
        db_id = int(call.data.split("_")[2])
        reserve = session.query(Reservations).filter_by(id=db_id).first()
        if reserve.status == FIRST or reserve.status == SECOND:
            reserve.status = CONFIRMED
            session.commit()
            room_name = get_room_name(reserve.room_id, session)
            weekday = dt.strptime(reserve.date, "%Y-%m-%d").strftime("%A")
            txt = f'Your meeting hours submitted ✅\n\n📅 Date: {reserve.date} ({weekday})\n🚪 Room: {room_name}\n▶️ From: {reserve.start_time}\n◀️ To: {reserve.end_time}'
            markup = InlineKeyboardMarkup()
            markup.add(btn(text="📅 Edit Date", callback_data=f"e_date_{reserve.id}"))
            markup.add(btn(text="🚪 Edit Room", callback_data=f"e_room_{reserve.id}"))
            markup.add(btn(text="🕰 Edit Hours", callback_data=f"e_hours_{reserve.id}"))
            markup.add(btn(text="⬅️ Back", callback_data="backedit"))
            bot.edit_message_text(chat_id=chat_id, message_id=msg_id, text=txt, reply_markup=markup)
        else:
            bot.answer_callback_query(call.id, "You can't confirm before completing the hours ⛔️", show_alert=True)
    except SQLAlchemyError as e:
        add_log(f"SQLAlchemyError in process_set_edit_hours: {e}")
    except Exception as e:
        add_log(f"Exception in process_set_edit_hours: {e}")


def process_delete_reservations(call, session, bot):
    try:
        chat_id, msg_id = str(call.message.chat.id), call.message.id
        uid = session.query(Users).filter_by(chat_id=chat_id).first().id
        confs = session.query(Reservations).filter_by(user_id=uid, status=CONFIRMED).all()
        future_reserves = [reserve for reserve in confs if future_date(reserve)]
        txt = "🗑 Choose the Reservation you'd like to delete:"
        markup = InlineKeyboardMarkup()
        for reserve in future_reserves:
            date, str_hour = reserve.date, f"{reserve.start_time}-{reserve.end_time}"
            t = f"📅 {date[5:7]}/{date[7:]}  {str_hour}"
            markup.add(btn(text=t, callback_data=f"d_r_{reserve.id}"))
        markup.add(btn(text="⬅️ Back", callback_data="backfuture"))
        bot.edit_message_text(chat_id=chat_id, message_id=msg_id, text=txt, reply_markup=markup)
    except Exception as e:
        add_log(f"Exception in process_delete_reservations: {e}")


def process_delete_specific_reservation(call, session, bot):
    try:
        chat_id, msg_id = str(call.message.chat.id), call.message.id
        db_id = int(call.data.split("_")[2])
        reserve = session.query(Reservations).filter_by(id=db_id).first()
        uid = reserve.user_id
        room_name = get_room_name(reserve.room_id, session)
        weekday = dt.strptime(reserve.date, "%Y-%m-%d").strftime("%A")
        txt = f'Your meeting deleted successfully ✅\n\n📅 Date: {reserve.date} ({weekday})\n🚪 Room: {room_name}\n▶️ From: {reserve.start_time}\n◀️ To: {reserve.end_time}'
        session.delete(reserve)
        session.commit()
        users_reservations = session.query(Reservations).filter_by(user_id=uid, status=CONFIRMED).all()
        markup = InlineKeyboardMarkup()
        if len(users_reservations) > 0:
            markup.add(btn(text="⬅️ Back", callback_data="backfuture"))
        else:
            markup.add(btn(text="⬅️ Back", callback_data="backmain"))
        bot.edit_message_text(chat_id=chat_id, message_id=msg_id, text=txt, reply_markup=markup)
    except Exception as e:
        add_log(f"Exception in process_delete_specific_reservation: {e}")


def process_past_reservations(call_page, session, bot):
    try:
        call, page = call_page
        chat_id, msg_id = str(call.message.chat.id), call.message.id
        past_reserves = get_past_reserves(chat_id, session)
        start_idx, end_idx, paginated_reserves = get_start_end_paginate(page, past_reserves)
        txt_2 = ""
        for reserve in paginated_reserves:
            room_name = get_room_name(reserve.room_id, session)
            weekday = dt.strptime(reserve.date, "%Y-%m-%d").strftime("%A")
            txt_2 += f'📅 Date: {reserve.date} ({weekday})\n🚪 Room: {room_name}\n▶️ From: {reserve.start_time}\n◀️ To: {reserve.end_time}\n\n'
        txt, markup = get_txt_markup_in_past_reservations(past_reserves, txt_2)
        if page > 0:
            markup.add(btn(text="⬅️ Previous", callback_data=f"past_reservations_{page - 1}"))
        if end_idx < len(past_reserves):
            markup.add(btn(text="Next ➡️", callback_data=f"past_reservations_{page + 1}"))
        markup.add(btn(text="⬅️ Back", callback_data="backuser"))
        bot.edit_message_text(chat_id=chat_id, message_id=msg_id, text=txt, reply_markup=markup)
    except Exception as e:
        add_log(f"Exception in process_past_reservations: {e}")
