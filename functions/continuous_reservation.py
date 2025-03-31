from datetime import datetime, timedelta

from telebot import types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton as Btn

from functions.get_functions import get_txt_in_cb
from models.rooms import Rooms
from services.config import (
    get_user,
    FARSI,
    WEEKDAYS_LIST,
    day_in_persian,
    time_difference,
)
from services.language import get_text, BotText, change_num_as_lang
from services.log import add_log


def process_continuous_reservation(call_message, session, bot):
    try:
        user = get_user(call_message, session)
        t = get_text(BotText.CHOOSE_WEEKDAY_TEXT, user.language)
        k = get_weekday_buttons(user)
        ch_id = user.chat_id
        if isinstance(call_message, types.Message):
            bot.send_message(chat_id=ch_id, text=t, reply_markup=k)
        else:
            msg = call_message.message.id
            bot.edit_message_text(chat_id=ch_id, message_id=msg, text=t, reply_markup=k)
    except Exception as e:
        add_log(f"Exception in process_continuous_reservation: {e}")


def get_weekday_buttons(user):
    markup = InlineKeyboardMarkup(row_width=3)
    text_index = 0 if user.language == FARSI else 1
    for i in range(0, len(WEEKDAYS_LIST), 3):
        buttons = [
            Btn(text=day[text_index], callback_data=f"cr_weekday_{day[1]}")
            for day in WEEKDAYS_LIST[i : i + 3]
        ]
        markup.row(*reversed(buttons) if user.language == FARSI else buttons)
    return markup


def process_cr_weekday(call, session, bot):
    ch_id, msg = call.message.chat.id, call.message.id
    weekday_str = call.data.split("_")[2]
    user = get_user(call, session)
    if user.language == FARSI:
        weekday = day_in_persian[weekday_str]
    else:
        weekday = weekday_str
    t = get_text(BotText.CHOOSE_HOURS_TEXT, user.language).format(weekday=weekday)
    key = get_cr_hour_buttons(call, session)
    key = add_confirm_back(key, user, ["cr_confirm_hour", "cr_back_weekday"])
    bot.edit_message_text(chat_id=ch_id, message_id=msg, text=t, reply_markup=key)


def get_cr_hour_buttons(call, session, start_end=None):
    markup, buttons = InlineKeyboardMarkup(row_width=2), []
    for h in range(8, 21):
        for m in range(0, 46, 15):
            time = f"{h:02}:{m:02}"
            txt, callback = get_txt_in_cb([h, m], call, session), f"cr_hr_select_{time}"
            if start_end:
                start, end = start_end
                start_diff = time_difference(start, time)
                end_diff = time_difference(end, time)
                if start_diff == 0:
                    txt, callback = "▶️", f"cr_hr_first-remove_{time}"
                elif end_diff == -15:
                    txt, callback = "◀️", f"cr_hr_remove_{time}"
                elif start_diff > 0 > end_diff:
                    txt, callback = "✅", f"cr_hr_select_{time}"
            buttons.append(Btn(text=txt, callback_data=callback))
            if len(buttons) == 2:
                markup.row(*buttons)
                buttons = []
    if buttons:
        markup.row(*buttons)
    return markup


def add_confirm_back(markup, user, callback):
    cb_confirm, cb_back = callback
    confirm_text = get_text(BotText.CONFIRM_BUTTON, user.language)
    back_text = get_text(BotText.BACK_BUTTON, user.language)
    markup.add(Btn(text=confirm_text, callback_data=cb_confirm))
    markup.add(Btn(text=back_text, callback_data=cb_back))
    return markup


def process_cr_hour_selection(call, session, bot):
    ch_id, msg = call.message.chat.id, call.message.id
    user = get_user(call, session)
    start, end, txt = "", "", ""
    status = get_status(call)
    # status: start/clear/error-duration/error-past/second/back-first
    if status == "error-past":
        t = get_text(BotText.INVALID_TIME_ALERT, user.language)
        bot.answer_callback_query(call.id, t, show_alert=True)
        return
    elif status == "error-duration":
        t0 = get_text(BotText.INVALID_DURATION, user.language)
        t = change_num_as_lang(t0, user.language)
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


def get_status(call):
    txt = call.message.text.split("\n")
    mode, time = call.data.split("_")[2:]
    # mode: select/remove/first-remove
    if len(txt) == 2:
        return "start"
    else:
        txt = change_num_as_lang(call.message.text, "en").split("\n")
        start_time = txt[1].split(": ")[1]
        end_time = txt[2].split(": ")[1]
        diff = time_difference(start_time, end_time)
    if mode == "first-remove":
        return "clear"
    elif time_difference(start_time, time) >= 240:
        return "error-duration"
    elif diff == 15 and mode == "select" and time_difference(time, start_time) > 0:
        return "error-past"
    elif diff == 15 and mode == "select":
        return "second"
    elif mode == "remove":
        return "back-first"
    elif mode == "select":
        return "start"


def select_new_time(call, user):
    time = call.data.split("_")[3]
    weekday = call.message.text.split("\n")[0]
    start, end = get_time_and_15_min_later(time)
    t = get_text(BotText.FIRST_HOURS_TEXT, user.language).format(
        weekday=weekday, start=start, end=end
    )
    txt = change_num_as_lang(t, user.language)
    return txt, start, end


def remove_start_hour(call, user):
    weekday = call.message.text.split("\n")[0]
    txt = get_text(BotText.START_HOURS_TEXT, user.language).format(weekday=weekday)
    return txt, "", ""


def set_new_end_hour(call, user):
    time = call.data.split("_")[3]
    _, end_time = get_time_and_15_min_later(time)
    txt = call.message.text.split("\n")
    weekday = txt[0]
    start_time = txt[1].split(": ")[1]
    start, end = start_time, end_time
    t = get_text(BotText.SECOND_HOURS_TEXT, user.language).format(
        weekday=weekday, start=start, end=end
    )
    txt = change_num_as_lang(t, user.language)
    return txt, start, end


def remove_end_hour(call, user):
    txt = call.message.text.split("\n")
    weekday = txt[0]
    start_time = txt[1].split(": ")[1]
    start, end = get_time_and_15_min_later(start_time)
    t = get_text(BotText.FIRST_HOURS_TEXT, user.language).format(
        weekday=weekday, start=start, end=end
    )
    txt = change_num_as_lang(t, user.language)
    return txt, start, end


def get_time_and_15_min_later(time_str):
    time_str = change_num_as_lang(time_str, "en")
    original_time = datetime.strptime(time_str, "%H:%M")
    later_time = original_time + timedelta(minutes=15)
    later_str = later_time.strftime("%H:%M")
    return time_str, later_str


def process_confirm_cr_hour(call, session, bot):
    txt = call.message.text.split("\n")
    user = get_user(call, session)
    if len(txt) < 3:
        txt = get_text(BotText.INCOMPLETE_HOURS_ALERT, user.language)
        bot.answer_callback_query(call.id, txt, show_alert=True)
    else:
        return process_show_rooms(call, session, bot)


def process_show_rooms(call, session, bot):
    ch_id, msg = call.message.chat.id, call.message.id
    user = get_user(call, session)
    last_data = "\n".join(call.message.text.split("\n")[:3])
    txt = get_text(BotText.CHOOSE_ROOM_TEXT, user.language).format(last_data=last_data)
    txt = change_num_as_lang(txt, user.language)
    key = InlineKeyboardMarkup()
    rooms = session.query(Rooms).all()
    for room in rooms:
        key.add(Btn(text=f"{room.name}", callback_data=f"cr_room_{room.name}"))
    back_txt = get_text(BotText.BACK_BUTTON, user.language)
    key.add(Btn(text=back_txt, callback_data="cr_back_hours"))
    bot.edit_message_text(chat_id=ch_id, message_id=msg, text=txt, reply_markup=key)


def process_cr_back_hours(call, session, bot):
    ch_id, msg = call.message.chat.id, call.message.id
    user = get_user(call, session)
    txt = call.message.text.split("\n")
    start = txt[1].split(": ")[1]
    end = txt[2].split(": ")[1]
    t = "\n".join(txt[:3])
    start = change_num_as_lang(start, "en")
    end = change_num_as_lang(end, "en")
    key = get_cr_hour_buttons(call, session, [start, end])
    key = add_confirm_back(key, user, ["cr_confirm_hour", "cr_back_weekday"])
    bot.edit_message_text(chat_id=ch_id, message_id=msg, text=t, reply_markup=key)


def process_room_selection(call, session, bot):
    ch_id, msg = call.message.chat.id, call.message.id
    user = get_user(call, session)
    txt = call.message.text.split("\n")
    last_data = "\n".join(txt[:3])
    t = get_text(BotText.CHOOSE_CHARGE_TEXT, user.language).format(
        last_data=last_data, room=call.data.split("_")[2], charge=user.charge
    )
    t = change_num_as_lang(t, user.language)
    key = get_weeks_buttons(user, t)
    key = add_confirm_back(key, user, ["cr_confirm_weeks", "cr_back_rooms"])
    bot.edit_message_text(chat_id=ch_id, message_id=msg, text=t, reply_markup=key)


def get_weeks_buttons(user, txt):
    txt = change_num_as_lang(txt, "en")
    txt = txt.split("\n")
    week = txt[10].split(":")[1].strip()
    markup, buttons = InlineKeyboardMarkup(row_width=5), []
    for i in range(1, 26):
        if week and str(i) == week:
            t = f" {change_num_as_lang(str(i), user.language)} ✅"
            buttons.append(Btn(text=f"{t}", callback_data=f"cr_week_remove_{i}"))
        else:
            t = f"  {change_num_as_lang(str(i), user.language)}  "
            buttons.append(Btn(text=f"{t}", callback_data=f"cr_week_select_{i}"))
        if len(buttons) == 5:
            markup.row(*reversed(buttons) if user.language == FARSI else buttons)
            buttons = []
    if buttons:
        markup.row(*reversed(buttons) if user.language == FARSI else buttons)
    return markup


def process_cr_week_selection(call, session, bot):
    ch_id, msg = call.message.chat.id, call.message.id
    status, week = call.data.split("_")[2:]
    txt = call.message.text.split("\n")
    user = get_user(call, session)
    if status == "select":
        if user.language == "en":
            txt[10] = f"❓ Weeks: {week}"
        else:
            txt[10] = f"❓ هفته‌ها: {change_num_as_lang(week, user.language)}"
    else:
        if user.language == "en":
            txt[10] = "❓ Weeks:"
        else:
            txt[10] = "❓ هفته‌ها:"
    t = "\n".join(txt)
    key = get_weeks_buttons(user, t)
    key = add_confirm_back(key, user, ["cr_confirm_weeks", "cr_back_rooms"])
    bot.edit_message_text(chat_id=ch_id, message_id=msg, text=t, reply_markup=key)


def process_confirm_cr_week(call, session, bot):
    txt = change_num_as_lang(call.message.text, "en").split("\n")
    start = txt[1].split(": ")[1]
    end = txt[2].split(": ")[1]
    user = get_user(call, session)
    user_has_charge = check_user_charge(time_difference(start, end), user)
    if not user_has_charge:
        t = get_text(BotText.INVALID_TIME_ALERT, user.language)
        bot.answer_callback_query(call.id, t, show_alert=True)
    # if user.charge !=


def check_user_charge(diff, user):
    if user.charge == 0:
        return False
    elif diff <= 60 and user.charge >= 1:
        return True
    elif 60 < diff <= 120 and user.charge >= 2:
        return True
    elif 120 < diff <= 180 and user.charge >= 3:
        return True
    elif 180 < diff <= 240 and user.charge >= 4:
        return True
    elif user.charge >= 4:
        return True
    else:
        return False
