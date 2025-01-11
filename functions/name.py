import re

from sqlalchemy.exc import SQLAlchemyError

from functions.run_command import run_user_command
from services.config import get_user, send_cancel_message
from services.log import add_log


def process_name(message, session, bot):
    chat_id = str(message.chat.id)
    bot.send_message(
        chat_id,
        "Enter your Name Please:\n\nIf you want to cancel the operation tap on /cancel",
    )
    bot.register_next_step_handler(message, check_name, session, bot)


def check_name(message, session, bot):
    try:
        chat_id = message.chat.id
        text = check_text_in_name(message, session)
        if text is None:
            bot.send_message(chat_id, "Operation cancelled!")
            return
        elif text:
            add_name_in_db(message, session)
            bot.send_message(chat_id, "Your name submitted successfully 👍🏻")
            return run_user_command(message, session, bot)
        else:
            bot.send_message(chat_id, "Your name must be a string and should not contain any digits or symbols ⛔️")
            return process_name(message, session, bot)
    except SQLAlchemyError as e:
        add_log(f"SQLAlchemyError in check_name: {e}")
    except Exception as e:
        add_log(f"Exception in check_name: {e}")


def check_text_in_name(message, session):
    if send_cancel_message(message, session):
        return
    elif contains_only_letters(message.text):
        return True
    else:
        return False


def add_name_in_db(message, session):
    try:
        user = get_user(message, session)
        user.name = message.text
        session.commit()
    except SQLAlchemyError as e:
        add_log(f"SQLAlchemyError in add_name_in_db: {e}")
    except Exception as e:
        add_log(f"Exception in add_name_in_db: {e}")


def contains_only_letters(text):
    pattern = r'^[a-zA-Z\u0600-\u06FF\s]+$'
    if re.match(pattern, text):
        return True
    return False
