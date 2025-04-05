from sqlalchemy.exc import SQLAlchemyError

from functions.get_functions_cr import (
    get_week_date_buttons,
    get_final_week_buttons,
    get_room_id_as_name,
    get_start_end_charge,
    get_date_as_txt,
)
from models.reservations import Reservations
from services.config import get_user, CONFIRMED
from services.language import change_num_as_lang, get_text, BotText
from services.log import add_log


def process_cr_edit_weeks(call, session, bot):
    try:
        ch_id, msg = call.message.chat.id, call.message.id
        user = get_user(call, session)
        week_dates = call.message.text.split("\n")[6:]
        key = get_week_date_buttons(week_dates, user)
        bot.edit_message_reply_markup(chat_id=ch_id, message_id=msg, reply_markup=key)
    except Exception as e:
        add_log(f"Exception in process_cr_edit_weeks: {e}")


def process_cr_back_final_week(call, session, bot):
    try:
        ch_id, msg = call.message.chat.id, call.message.id
        user = get_user(call, session)
        t = call.message.text.replace("🗑", "🟢")
        key = get_final_week_buttons(user)
        bot.edit_message_text(chat_id=ch_id, message_id=msg, text=t, reply_markup=key)
    except Exception as e:
        add_log(f"Exception in process_cr_back_final_week: {e}")


def process_cr_edit_week_selection(call, session, bot):
    try:
        ch_id, msg = call.message.chat.id, call.message.id
        user = get_user(call, session)
        txt = call.message.text.split("\n")
        mode, date = call.data.split("_")[2:]
        fa_date = change_num_as_lang(date, "fa")
        for line in txt:
            if (date in line or fa_date in line) and mode == "select":
                idx = txt.index(line)
                txt[idx] = line.replace("🟢", "🗑")
            elif (date in line or fa_date in line) and mode == "remove":
                idx = txt.index(line)
                txt[idx] = line.replace("🗑", "🟢")
        t = "\n".join(txt)
        week_dates = t.split("\n")[6:]
        key = get_week_date_buttons(week_dates, user)
        bot.edit_message_text(chat_id=ch_id, message_id=msg, text=t, reply_markup=key)
    except Exception as e:
        add_log(f"Exception in process_cr_edit_week_selection: {e}")


def process_cr_confirm_edited_weeks(call, session, bot):
    try:
        ch_id, msg = call.message.chat.id, call.message.id
        user = get_user(call, session)
        txt = call.message.text.split("\n")
        weeks = int(change_num_as_lang(txt[5].split(":")[1].strip(), "en"))
        for line in txt:
            if "🗑" in line:
                txt.remove(line)
                weeks -= 1
        weeks = change_num_as_lang(str(weeks), user.language)
        for line in txt:
            if "🗓️" in line:
                idx = txt.index(line)
                txt[idx] = f"{line.split(':')[0]}: {weeks}"
        t = "\n".join(txt)
        key = get_final_week_buttons(user)
        bot.edit_message_text(chat_id=ch_id, message_id=msg, text=t, reply_markup=key)
    except Exception as e:
        add_log(f"Exception in process_cr_confirm_edited_weeks: {e}")


def process_cr_cancel_reserve(call, session, bot):
    try:
        ch_id, msg = call.message.chat.id, call.message.id
        user = get_user(call, session)
        t = get_text(BotText.CANCEL_RESERVATION_TEXT, user.language)
        bot.edit_message_text(chat_id=ch_id, message_id=msg, text=t)
    except Exception as e:
        add_log(f"Exception in process_cr_cancel_reserve: {e}")


def process_cr_reserve_weeks(call, session, bot):
    try:
        ch_id, msg = call.message.chat.id, call.message.id
        user = get_user(call, session)
        txt = change_num_as_lang(call.message.text, "en")
        txt = txt.split("\n")
        last_charge = txt[1].split(":")[1].strip()
        txt.pop(1)
        txt = [line for line in txt if "🔴" not in line]
        if len(txt) < 6:
            t = get_text(BotText.INVALID_NONE_WEEKS, user.language)
            bot.answer_callback_query(call.id, t, show_alert=True)
            return
        update_txt_as_weeks(txt)
        charge = add_cr_to_db(txt, user, session)
        txt = "\n".join(txt)
        billing_charge = int(last_charge) - charge
        t = get_text(BotText.CONFIRMED_COUNTINUOUS_RESERVATION, user.language).format(
            billing_charge=billing_charge, charge=charge, last_data=txt
        )
        t = change_num_as_lang(t, user.language)
        bot.edit_message_text(chat_id=ch_id, message_id=msg, text=t)
    except Exception as e:
        add_log(f"Exception in process_cr_reserve_weeks: {e}")


def update_txt_as_weeks(txt):
    new_weeks = len(txt) - 5
    for line in txt:
        if "🗓️" in line:
            idx = txt.index(line)
            txt[idx] = f"{line.split(':')[0]}: {new_weeks}"


def add_cr_to_db(txt, user, session):
    start, end, charge = get_start_end_charge(txt)
    try:
        new_charge = user.charge - charge
        user.charge = new_charge
        room_name = txt[3].split(": ")[1]
        room_id = get_room_id_as_name(room_name, session)
        for line in txt[5:]:
            date = get_date_as_txt(line)
            new_reserve = Reservations(
                room_id=room_id,
                user_id=user.id,
                date=date,
                start_time=start,
                end_time=end,
                status=CONFIRMED,
            )
            session.add(new_reserve)
        session.commit()
        return new_charge
    except SQLAlchemyError as e:
        add_log(f"SQLAlchemyError in add_cr_to_db: {e}")
    except Exception as e:
        add_log(f"Exception in add_cr_to_db: {e}")
