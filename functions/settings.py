from sqlalchemy.exc import SQLAlchemyError
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton as btn

from models.users import Users
from services.language import get_text, BotText
from services.log import add_log


def process_settings(message, session, bot):
    try:
        chat_id = str(message.chat.id)
        user = session.query(Users).filter_by(chat_id=chat_id).first()
        txt = get_text(BotText.LANGUAGE_TEXT, user.language)
        key = InlineKeyboardMarkup()
        if user.language == "fa":
            key.add(btn(text="English", callback_data="en-lang"))
        else:
            key.add(btn(text="فارسی", callback_data="fa-lang"))
        bot.send_message(chat_id=chat_id, text=txt, reply_markup=key)
    except Exception as e:
        add_log(f"Exception in process_settings: {e}")


def process_set_language_to_persian(call, session, bot):
    try:
        chat_id, msg_id = str(call.message.chat.id), call.message.id
        user = session.query(Users).filter_by(chat_id=chat_id).first()
        user.language = 'fa'
        session.commit()
        txt = get_text(BotText.PERSIAN_CALLBACK, user.language)
        bot.edit_message_text(chat_id=chat_id, message_id=msg_id, text=txt)
    except SQLAlchemyError as e:
        add_log(f"SQLAlchemyError in process_set_language_to_persian: {e}")
    except Exception as e:
        add_log(f"Exception in process_set_language_to_persian: {e}")


def process_set_language_to_english(call, session, bot):
    try:
        chat_id, msg_id = str(call.message.chat.id), call.message.id
        user = session.query(Users).filter_by(chat_id=chat_id).first()
        user.language = 'en'
        session.commit()
        txt = get_text(BotText.PERSIAN_CALLBACK, user.language)
        bot.edit_message_text(chat_id=chat_id, message_id=msg_id, text=txt)
    except SQLAlchemyError as e:
        add_log(f"SQLAlchemyError in process_set_language_to_english: {e}")
    except Exception as e:
        add_log(f"Exception in process_set_language_to_english: {e}")
