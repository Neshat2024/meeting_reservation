from functions.get_functions_cr import get_week_date_buttons, \
    get_final_week_buttons
from services.config import get_user
from services.language import change_num_as_lang, get_text, BotText


def process_cr_edit_weeks(call, session, bot):
    ch_id, msg = call.message.chat.id, call.message.id
    user = get_user(call, session)
    week_dates = call.message.text.split("\n")[6:]
    key = get_week_date_buttons(week_dates, user)
    bot.edit_message_reply_markup(chat_id=ch_id, message_id=msg, reply_markup=key)


def process_cr_back_final_week(call, session, bot):
    ch_id, msg = call.message.chat.id, call.message.id
    user = get_user(call, session)
    t = call.message.text.replace("🗑", "🟢")
    key = get_final_week_buttons(user)
    bot.edit_message_text(chat_id=ch_id, message_id=msg, text=t, reply_markup=key)


def process_cr_edit_week_selection(call, session, bot):
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


def process_cr_confirm_edited_weeks(call, session, bot):
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


def process_cr_cancel_reserve(call, session, bot):
    ch_id, msg = call.message.chat.id, call.message.id
    user = get_user(call, session)
    t = get_text(BotText.CANCEL_RESERVATION_TEXT, user.language)
    bot.edit_message_text(chat_id=ch_id, message_id=msg, text=t)


def process_cr_reserve_weeks(call, session, bot):
    ch_id, msg = call.message.chat.id, call.message.id
    user = get_user(call, session)
    txt = call.message.text.split("\n")
    last_charge = change_num_as_lang(txt[1].split(":")[1].strip(), user.language)
    txt.pop(1)
    for line in txt:
        if "🔴" in line:
            idx = txt.index(line)
            txt.remove(idx)
    charge = add_cr_to_db(txt, user, session)
    t = get_text(BotText.CONFIRMED_COUNTINUOUS_RESERVATION, user.language).format(last_charge=last_charge, charge=charge, last_data="\n".join(txt))
    bot.edit_message_text(chat_id=ch_id, message_id=msg, text=t)


def add_cr_to_db(txt, user, session):
    pass
