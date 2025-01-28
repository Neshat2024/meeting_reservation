from sqlalchemy.exc import SQLAlchemyError
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton as btn

from services.config import get_user
from services.language import get_text, BotText
from services.log import add_log


def process_settings(message, session, bot):
    try:
        user = get_user(message, session)
        txt = get_text(BotText.LANGUAGE_TEXT, user.language)
        key = InlineKeyboardMarkup()
        if user.language == "fa":
            key.add(btn(text="English", callback_data="en-lang"))
        else:
            key.add(btn(text="فارسی", callback_data="fa-lang"))
        bot.send_message(chat_id=int(user.chat_id), text=txt, reply_markup=key)
    except Exception as e:
        add_log(f"Exception in process_settings: {e}")


def process_set_language_to_persian(call, session, bot):
    try:
        msg_id = call.message.id
        user = get_user(call, session)
        user.language = 'fa'
        session.commit()
        txt = get_text(BotText.PERSIAN_CALLBACK, user.language)
        bot.edit_message_text(chat_id=int(user.chat_id), message_id=msg_id, text=txt)
    except SQLAlchemyError as e:
        add_log(f"SQLAlchemyError in process_set_language_to_persian: {e}")
    except Exception as e:
        add_log(f"Exception in process_set_language_to_persian: {e}")


def process_set_language_to_english(call, session, bot):
    try:
        msg_id = call.message.id
        user = get_user(call, session)
        user.language = 'en'
        session.commit()
        txt = get_text(BotText.PERSIAN_CALLBACK, user.language)
        bot.edit_message_text(chat_id=int(user.chat_id), message_id=msg_id, text=txt)
    except SQLAlchemyError as e:
        add_log(f"SQLAlchemyError in process_set_language_to_english: {e}")
    except Exception as e:
        add_log(f"Exception in process_set_language_to_english: {e}")
