from datetime import datetime, timedelta

import pytz
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton as Btn

from functions.get_functions_reserves import get_txt_in_cb
from models.reservations import Reservations
from models.rooms import Rooms
from models.users import Users
from services.config import (
    CONFIRMED,
    gregorian_to_jalali,
    day_in_persian,
    FARSI,
    weekday_map,
    WEEKDAYS_LIST,
    time_difference,
)
from services.language import (
    get_text,
    BotText,
    change_num_as_lang,
)

tehran_tz = pytz.timezone("Asia/Tehran")


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


def get_status(call, user):
    txt = call.message.text.split("\n")
    mode, time = call.data.split("_")[2:]
    # mode: select/remove/first-remove
    if len(txt) == 3:
        return "start"
    else:
        txt = change_num_as_lang(call.message.text, "en").split("\n")
        start_time = txt[2].split(": ")[1]
        end_time = txt[3].split(": ")[1]
        diff = time_difference(start_time, end_time)
    time_start, time_end = get_time_and_15_min_later(time)
    start_to_end = time_difference(start_time, time_end)
    if mode == "first-remove":
        return "clear"
    elif time_difference(start_time, time) >= 240:
        return "error-duration"
    elif diff == 15 and mode == "select" and time_difference(time, start_time) > 0:
        return "error-past"
    elif diff == 15 and mode == "select" and start_to_end > user.charge * 60:
        charge = (
            (start_to_end // 60) + 1
            if start_to_end not in [120, 180, 240]
            else start_to_end // 60
        )
        return f"error-charge_{charge}"
    elif diff == 15 and mode == "select":
        return "second"
    elif mode == "remove":
        return "back-first"
    elif mode == "select":
        return "start"


def get_time_and_15_min_later(time_str):
    time_str = change_num_as_lang(time_str, "en")
    original_time = datetime.strptime(time_str, "%H:%M")
    later_time = original_time + timedelta(minutes=15)
    later_str = later_time.strftime("%H:%M")
    return time_str, later_str


def get_weeks_buttons(user, txt):
    txt = change_num_as_lang(txt, "en")
    txt = txt.split("\n")
    week = txt[5].split(":")[1].strip()
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


def get_final_week_buttons(user):
    markup, buttons = InlineKeyboardMarkup(row_width=2), []
    txt_cb = [
        (get_text(BotText.EDIT_WEEKS_BUTTON, user.language), "edit-weeks"),
        (get_text(BotText.CHAT_WITH_BOOKER_BUTTON, user.language), "chat-booker"),
        (get_text(BotText.RESERVE_POSSIBLES_BUTTON, user.language), "reserve-weeks"),
        (get_text(BotText.CANCEL_RESERVATION_BUTTON, user.language), "cancel-reserve"),
    ]
    for idx, (txt, cb) in enumerate(txt_cb):
        buttons.append(Btn(text=txt, callback_data=cb))
        if idx % 2 == 1:
            markup.row(*reversed(buttons) if user.language == FARSI else buttons)
            buttons = []
    back_text = get_text(BotText.BACK_BUTTON, user.language)
    markup.add(Btn(text=back_text, callback_data="cr_back_weeks"))
    return markup


def get_week_as_dates(txt, session, user):
    weeks = int(txt[5].split(":")[1].strip())
    weekday = get_weekday_as_language(txt[0].split(": ")[1])
    target_weekday = weekday_map[weekday]
    today = datetime.now(tehran_tz).date()
    current_weekday = today.weekday()
    days_ahead = (target_weekday - current_weekday) % 7
    if days_ahead == 0:
        next_date = today
    else:
        next_date = today + timedelta(days=days_ahead)
    dates = []
    for week in range(weeks):
        date = next_date + timedelta(weeks=week)
        str_date = date.strftime("%Y-%m-%d")
        booker = get_booker_as_start_end(txt, str_date, session)
        str_date = str_date if user.language == "en" else gregorian_to_jalali(str_date)
        if user.language == "en":
            dates.append(
                f"🟢 {str_date}"
                if not booker
                else f"🔴 {str_date} (Reserved by {booker})"
            )
        else:
            dates.append(
                f"🟢 {str_date}"
                if not booker
                else f"🔴 {str_date} (رزرو شده توسط {booker})"
            )
    return "\n".join(dates)


def get_weekday_as_language(weekday):
    for ewd, pwd in day_in_persian.items():
        if pwd == weekday:
            weekday = ewd.lower()
            break
    else:
        weekday = weekday.lower()
    return weekday


def get_booker_as_start_end(txt, date, session):
    start, end = txt[2].split(": ")[1], txt[3].split(": ")[1]
    room_name = txt[4].split(": ")[1]
    room_id = get_room_id_as_name(room_name, session)
    if room_id:
        reserves = (
            session.query(Reservations)
            .filter_by(room_id=room_id, date=date, status=CONFIRMED)
            .all()
        )
        for reserve in reserves:
            if time_has_overlap([start, end], [reserve.start_time, reserve.end_time]):
                return get_user_name(reserve.user_id, session)
        return


def get_room_id_as_name(room_name, session):
    room = session.query(Rooms).filter_by(name=room_name).first()
    return str(room.id)


def get_user_name(user_id, session):
    user = session.query(Users).filter_by(id=user_id).first()
    return user.name


def time_has_overlap(time1, time2):
    start1, end1 = time1
    start2, end2 = time2
    s1 = time_to_minutes(start1)
    e1 = time_to_minutes(end1)
    s2 = time_to_minutes(start2)
    e2 = time_to_minutes(end2)
    return max(s1, s2) < min(e1, e2)


def time_to_minutes(time_str):
    hh, mm = map(int, time_str.split(":"))
    return (hh * 60) + mm
