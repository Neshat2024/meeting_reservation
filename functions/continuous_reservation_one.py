import pytz
from telebot import types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton as Btn

from functions.get_functions_cr import (
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
from services.config import (
    get_user,
    FARSI,
    day_in_persian,
)
from services.language import get_text, BotText, change_num_as_lang
from services.log import add_log

tehran_tz = pytz.timezone("Asia/Tehran")
user_states = {}


def process_continuous_reservation(call_message, session, bot):
    try:
        user = get_user(call_message, session)
        ch_id = user.chat_id
        if user.charge not in ["", None, 0]:
            t = get_text(BotText.CHOOSE_WEEKDAY_TEXT, user.language)
            k = get_weekday_buttons(user)
            if isinstance(call_message, types.Message):
                msg = bot.send_message(chat_id=ch_id, text=t, reply_markup=k)
                user_states[ch_id] = {"last_msg_id": msg.message_id}
            else:
                msg = call_message.message.id
                bot.edit_message_text(
                    chat_id=ch_id, message_id=msg, text=t, reply_markup=k
                )
        else:
            t = get_text(BotText.INVALID_CHARGE, user.language)
            bot.send_message(chat_id=ch_id, text=t)
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
        t = get_text(BotText.CHOOSE_HOURS_TEXT, user.language).format(
            weekday=weekday, charge=user.charge
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
    t = get_text(BotText.FIRST_HOURS_TEXT, user.language).format(
        weekday=weekday, charge=user.charge, start=start, end=end
    )
    txt = change_num_as_lang(t, user.language)
    return txt, start, end


def remove_start_hour(call, user):
    weekday = call.message.text.split("\n")[0]
    txt = get_text(BotText.START_HOURS_TEXT, user.language).format(
        weekday=weekday, charge=user.charge
    )
    return txt, "", ""


def set_new_end_hour(call, user):
    time = call.data.split("_")[3]
    _, end_time = get_time_and_15_min_later(time)
    txt = call.message.text.split("\n")
    weekday = txt[0]
    start_time = txt[2].split(": ")[1]
    start, end = start_time, end_time
    t = get_text(BotText.SECOND_HOURS_TEXT, user.language).format(
        weekday=weekday, charge=user.charge, start=start, end=end
    )
    txt = change_num_as_lang(t, user.language)
    return txt, start, end


def remove_end_hour(call, user):
    txt = call.message.text.split("\n")
    weekday = txt[0]
    start_time = txt[2].split(": ")[1]
    start, end = get_time_and_15_min_later(start_time)
    t = get_text(BotText.FIRST_HOURS_TEXT, user.language).format(
        weekday=weekday, charge=user.charge, start=start, end=end
    )
    txt = change_num_as_lang(t, user.language)
    return txt, start, end


def process_confirm_cr_hour(call, session, bot):
    txt = call.message.text.split("\n")
    user = get_user(call, session)
    if len(txt) < 4:
        txt = get_text(BotText.INCOMPLETE_HOURS_ALERT, user.language)
        bot.answer_callback_query(call.id, txt, show_alert=True)
    else:
        return process_show_rooms(call, session, bot)


def process_show_rooms(call, session, bot):
    try:
        ch_id, msg = call.message.chat.id, call.message.id
        user = get_user(call, session)
        last_data = "\n".join(call.message.text.split("\n")[:4])
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
        start = txt[2].split(": ")[1]
        end = txt[3].split(": ")[1]
        t = "\n".join(txt[:4])
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
        last_data = "\n".join(txt[:4])
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
        if status == "select":
            if user.language == "en":
                txt[5] = f"❓ Weeks: {week}"
            else:
                txt[5] = f"❓ هفته‌ها: {change_num_as_lang(week, user.language)}"
        else:
            if user.language == "en":
                txt[5] = "❓ Weeks:"
            else:
                txt[5] = "❓ هفته‌ها:"
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
        weeks = txt[5].split(":")[1].strip()
        if not weeks:
            t = get_text(BotText.INVALID_WEEK_SELECTION, user.language)
            bot.answer_callback_query(call.id, t, show_alert=True)
            return
        week_as_date = get_week_as_dates(txt, session, user)
        last_data = "\n".join(call.message.text.split("\n")[:5])
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
        last_data = "\n".join(txt[:5])
        weeks = txt[5].split(":")[1].strip()
        t = get_text(BotText.SECOND_CHARGE_TEXT, user.language).format(
            last_data=last_data, weeks=weeks
        )
        t = change_num_as_lang(t, user.language)
        key = get_weeks_buttons(user, t)
        key = add_confirm_back(key, user, ["cr_confirm_weeks", "cr_back_rooms"])
        bot.edit_message_text(chat_id=ch_id, message_id=msg, text=t, reply_markup=key)
    except Exception as e:
        add_log(f"Exception in process_cr_back_weeks: {e}")
