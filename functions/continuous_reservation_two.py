from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton as Btn

from functions.get_functions_cr import add_confirm_back, get_weeks_buttons
from services.config import get_user
from services.language import change_num_as_lang


def process_cr_edit_weeks(call, session, bot):
    ch_id, msg = call.message.chat.id, call.message.id
    user = get_user(call, session)
    week_dates = call.message.text.split("\n")[6:]
    key = InlineKeyboardMarkup()
    for week_date in week_dates:
        if "🔴" not in week_date:
            date = week_date.split()[1]
            en_date = change_num_as_lang(date, "en")
            key.add(Btn(text=date, callback_data=f"cr_ew_select_{en_date}"))
    key = add_confirm_back(key, user, ["cr_confirm_edit_week", "cr_back_final_week"])
    bot.edit_message_reply_markup(chat_id=ch_id, message_id=msg, reply_markup=key)


def process_cr_back_final_week(call, session, bot):
    ch_id, msg = call.message.chat.id, call.message.id
    user = get_user(call, session)
    t = call.message.text.replace("🗑", "🟢")
    key = get_weeks_buttons(user, t)
    key = add_confirm_back(key, user, ["cr_confirm_weeks", "cr_back_rooms"])
    bot.edit_message_text(chat_id=ch_id, message_id=msg, text=t, reply_markup=key)


def process_cr_edit_week_selection(call, session, bot):
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
