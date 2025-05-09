import pytz
from telebot import types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton as Btn

from functions.get_functions_cr import (
    is_billable,
    get_week_as_dates,
    get_final_week_buttons,
    get_weekday_buttons,
    get_cr_hour_buttons,
    get_time_and_15_min_later,
    get_status,
    get_weeks_buttons,
    add_confirm_back,
)
from models.rooms import Rooms
from services.config import get_user
from services.language import get_text, BotText, change_num_as_lang
from services.log import add_log
from settings import FARSI, day_in_persian

tehran_tz = pytz.timezone("Asia/Tehran")


def process_continuous_reservation(call_message, session, bot):
    try:
        user = get_user(call_message, session)
        c = user.chat_id
        if not is_billable() or user.charge not in ["", None, 0]:
            t = get_text(BotText.CHOOSE_WEEKDAY_TEXT, user.language)
            k = get_weekday_buttons(user)
            if isinstance(call_message, types.Message):
                bot.send_message(c, t, reply_markup=k)
            else:
                msg = call_message.message.id
                bot.edit_message_text(chat_id=c, message_id=msg, text=t, reply_markup=k)
        else:
            t = get_text(BotText.INVALID_CHARGE, user.language)
            bot.send_message(c, t)
    except Exception as e:
        add_log(f"Exception in process_continuous_reservation: {e}")


def process_cr_weekday(call, session, bot):
    try:
        ch_id, msg = call.message.chat.id, call.message.id
        weekday_str = call.data.split("_")[2]
        user = get_user(call, session)
        if user.language == FARSI:
            weekday = day_in_persian[weekday_str]
        else:
            weekday = weekday_str
        if is_billable():
            t = get_text(BotText.CHOOSE_HOURS_TEXT_CHARGE, user.language).format(
                weekday=weekday, charge=user.charge
            )
        else:
            t = get_text(BotText.CHOOSE_HOURS_TEXT, user.language).format(
                weekday=weekday
            )
        key = get_cr_hour_buttons(call, session)
        key = add_confirm_back(key, user, ["cr_confirm_hour", "cr_back_weekday"])
        bot.edit_message_text(chat_id=ch_id, message_id=msg, text=t, reply_markup=key)
    except Exception as e:
        add_log(f"Exception in process_cr_weekday: {e}")


def process_cr_hour_selection(call, session, bot):
    try:
        ch_id, msg = call.message.chat.id, call.message.id
        user = get_user(call, session)
        start, end, txt = "", "", ""
        status = get_status(call, user)
        # status: start/clear/error-duration/error-past/error-charge/second/back-first
        if status == "error-past":
            t = get_text(BotText.INVALID_TIME_ALERT, user.language)
            bot.answer_callback_query(call.id, t, show_alert=True)
            return
        elif status == "error-duration":
            t0 = get_text(BotText.INVALID_DURATION, user.language)
            t = change_num_as_lang(t0, user.language)
            bot.answer_callback_query(call.id, t, show_alert=True)
            return
        elif status.startswith("error-charge"):
            charge = status.split("_")[1]
            t = get_text(BotText.INSUFFICIENT_CHARGE, user.language).format(
                charge=charge
            )
            bot.answer_callback_query(call.id, t, show_alert=True)
            return
        elif status == "start":
            txt, start, end = select_new_time(call, user)
        elif status == "clear":
            txt, start, end = remove_start_hour(call, user)
        elif status == "second":
            txt, start, end = set_new_end_hour(call, user)
        elif status == "back-first":
            txt, start, end = remove_end_hour(call, user)
        if start and end:
            start = change_num_as_lang(start, "en")
            end = change_num_as_lang(end, "en")
            key = get_cr_hour_buttons(call, session, [start, end])
        else:
            key = get_cr_hour_buttons(call, session)
        key = add_confirm_back(key, user, ["cr_confirm_hour", "cr_back_weekday"])
        bot.edit_message_text(chat_id=ch_id, message_id=msg, text=txt, reply_markup=key)
    except Exception as e:
        add_log(f"Exception in process_cr_hour_selection: {e}")


def select_new_time(call, user):
    time = call.data.split("_")[3]
    weekday = call.message.text.split("\n")[0]
    start, end = get_time_and_15_min_later(time)
    if is_billable():
        t = get_text(BotText.FIRST_HOURS_TEXT_CHARGE, user.language).format(
            weekday=weekday, charge=user.charge, start=start, end=end
        )
    else:
        t = get_text(BotText.FIRST_HOURS_TEXT, user.language).format(
            weekday=weekday, start=start, end=end
        )
    txt = change_num_as_lang(t, user.language)
    return txt, start, end


def remove_start_hour(call, user):
    weekday = call.message.text.split("\n")[0]
    if is_billable():
        txt = get_text(BotText.START_HOURS_TEXT_CHARGE, user.language).format(
            weekday=weekday, charge=user.charge
        )
    else:
        txt = get_text(BotText.START_HOURS_TEXT, user.language).format(weekday=weekday)
    return txt, "", ""


def set_new_end_hour(call, user):
    time = call.data.split("_")[3]
    _, end_time = get_time_and_15_min_later(time)
    txt = call.message.text.split("\n")
    weekday = txt[0]
    if is_billable():
        start_time = txt[2].split(": ")[1]
        t = get_text(BotText.SECOND_HOURS_TEXT_CHARGE, user.language).format(
            weekday=weekday, charge=user.charge, start=start_time, end=end_time
        )
    else:
        start_time = txt[1].split(": ")[1]
        t = get_text(BotText.SECOND_HOURS_TEXT, user.language).format(
            weekday=weekday, start=start_time, end=end_time
        )
    txt = change_num_as_lang(t, user.language)
    return txt, start_time, end_time


def remove_end_hour(call, user):
    txt = call.message.text.split("\n")
    weekday = txt[0]
    billable = is_billable()
    if billable:
        start_time = txt[2].split(": ")[1]
    else:
        start_time = txt[1].split(": ")[1]
    start, end = get_time_and_15_min_later(start_time)
    if billable:
        t = get_text(BotText.FIRST_HOURS_TEXT_CHARGE, user.language).format(
            weekday=weekday, charge=user.charge, start=start, end=end
        )
    else:
        t = get_text(BotText.FIRST_HOURS_TEXT, user.language).format(
            weekday=weekday, start=start, end=end
        )
    txt = change_num_as_lang(t, user.language)
    return txt, start, end


def process_confirm_cr_hour(call, session, bot):
    txt = call.message.text.split("\n")
    user = get_user(call, session)
    billable = is_billable()
    if (billable and len(txt) < 4) or (not billable and len(txt) < 3):
        txt = get_text(BotText.INCOMPLETE_HOURS_ALERT, user.language)
        bot.answer_callback_query(call.id, txt, show_alert=True)
    else:
        return process_show_rooms(call, session, bot)


def process_show_rooms(call, session, bot):
    try:
        ch_id, msg = call.message.chat.id, call.message.id
        user = get_user(call, session)
        if is_billable():
            last_data = "\n".join(call.message.text.split("\n")[:4])
        else:
            last_data = "\n".join(call.message.text.split("\n")[:3])
        txt = get_text(BotText.CHOOSE_ROOM_TEXT, user.language).format(
            last_data=last_data
        )
        txt = change_num_as_lang(txt, user.language)
        key = InlineKeyboardMarkup()
        rooms = session.query(Rooms).all()
        for room in rooms:
            key.add(Btn(text=f"{room.name}", callback_data=f"cr_room_{room.name}"))
        back_txt = get_text(BotText.BACK_BUTTON, user.language)
        key.add(Btn(text=back_txt, callback_data="cr_back_hours"))
        bot.edit_message_text(chat_id=ch_id, message_id=msg, text=txt, reply_markup=key)
    except Exception as e:
        add_log(f"Exception in process_show_rooms: {e}")


def process_cr_back_hours(call, session, bot):
    try:
        ch_id, msg = call.message.chat.id, call.message.id
        user = get_user(call, session)
        txt = call.message.text.split("\n")
        if is_billable():
            start = txt[2].split(": ")[1]
            end = txt[3].split(": ")[1]
            t = "\n".join(txt[:4])
        else:
            start = txt[1].split(": ")[1]
            end = txt[2].split(": ")[1]
            t = "\n".join(txt[:3])
        start = change_num_as_lang(start, "en")
        end = change_num_as_lang(end, "en")
        key = get_cr_hour_buttons(call, session, [start, end])
        key = add_confirm_back(key, user, ["cr_confirm_hour", "cr_back_weekday"])
        bot.edit_message_text(chat_id=ch_id, message_id=msg, text=t, reply_markup=key)
    except Exception as e:
        add_log(f"Exception in process_cr_back_hours: {e}")


def process_room_selection(call, session, bot):
    try:
        ch_id, msg = call.message.chat.id, call.message.id
        user = get_user(call, session)
        txt = call.message.text.split("\n")
        if is_billable():
            last_data = "\n".join(txt[:4])
        else:
            last_data = "\n".join(txt[:3])
        t = get_text(BotText.CHOOSE_CHARGE_TEXT, user.language).format(
            last_data=last_data, room=call.data.split("_")[2]
        )
        t = change_num_as_lang(t, user.language)
        key = get_weeks_buttons(user, t)
        key = add_confirm_back(key, user, ["cr_confirm_weeks", "cr_back_rooms"])
        bot.edit_message_text(chat_id=ch_id, message_id=msg, text=t, reply_markup=key)
    except Exception as e:
        add_log(f"Exception in process_room_selection: {e}")


def process_cr_week_selection(call, session, bot):
    try:
        ch_id, msg = call.message.chat.id, call.message.id
        status, week = call.data.split("_")[2:]
        txt = call.message.text.split("\n")
        user = get_user(call, session)
        billable = is_billable()
        if billable and status == "select" and user.language == "en":
            txt[5] = f"❓ Weeks: {week}"
        elif billable and status == "select":
            txt[5] = f"❓ هفته‌ها: {change_num_as_lang(week, user.language)}"
        elif status == "select" and user.language == "en":
            txt[4] = f"❓ Weeks: {week}"
        elif status == "select":
            txt[4] = f"❓ هفته‌ها: {change_num_as_lang(week, user.language)}"
        elif billable and user.language == "en":
            txt[5] = "❓ Weeks:"
        elif billable:
            txt[5] = "❓ هفته‌ها:"
        elif user.language == "en":
            txt[4] = "❓ Weeks:"
        else:
            txt[4] = "❓ هفته‌ها:"
        t = "\n".join(txt)
        key = get_weeks_buttons(user, t)
        key = add_confirm_back(key, user, ["cr_confirm_weeks", "cr_back_rooms"])
        bot.edit_message_text(chat_id=ch_id, message_id=msg, text=t, reply_markup=key)
    except Exception as e:
        add_log(f"Exception in process_cr_week_selection: {e}")


def process_confirm_cr_week(call, session, bot):
    try:
        ch_id, msg = call.message.chat.id, call.message.id
        user = get_user(call, session)
        txt = change_num_as_lang(call.message.text, "en").split("\n")
        billable = is_billable()
        if billable:
            weeks = txt[5].split(":")[1].strip()
        else:
            weeks = txt[4].split(":")[1].strip()
        if not weeks:
            t = get_text(BotText.INVALID_WEEK_SELECTION, user.language)
            bot.answer_callback_query(call.id, t, show_alert=True)
            return
        week_as_date = get_week_as_dates(txt, session, user)
        if billable:
            last_data = "\n".join(call.message.text.split("\n")[:5])
        else:
            last_data = "\n".join(call.message.text.split("\n")[:4])
        t = get_text(BotText.WEEKS_TEXT, user.language).format(
            last_data=last_data, weeks=weeks, week_as_date=week_as_date
        )
        t = change_num_as_lang(t, user.language)
        key = get_final_week_buttons(user)
        bot.edit_message_text(chat_id=ch_id, message_id=msg, text=t, reply_markup=key)
    except Exception as e:
        add_log(f"Exception in process_confirm_cr_week: {e}")


def process_cr_back_weeks(call, session, bot):
    try:
        ch_id, msg = call.message.chat.id, call.message.id
        user = get_user(call, session)
        txt = call.message.text.split("\n")
        if is_billable():
            last_data = "\n".join(txt[:5])
            weeks = txt[5].split(":")[1].strip()
        else:
            last_data = "\n".join(txt[:4])
            weeks = txt[4].split(":")[1].strip()
        t = get_text(BotText.SECOND_CHARGE_TEXT, user.language).format(
            last_data=last_data, weeks=weeks
        )
        t = change_num_as_lang(t, user.language)
        key = get_weeks_buttons(user, t)
        key = add_confirm_back(key, user, ["cr_confirm_weeks", "cr_back_rooms"])
        bot.edit_message_text(chat_id=ch_id, message_id=msg, text=t, reply_markup=key)
    except Exception as e:
        add_log(f"Exception in process_cr_back_weeks: {e}")
