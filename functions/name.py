from sqlalchemy.exc import SQLAlchemyError

from functions.run_command import run_user_command
from models.users import Users
from services.config import get_user, check_text_in_name
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
        text = check_text_in_name(message)
        if text is None:
            bot.send_message(chat_id, "Operation cancelled!")
            return
        elif text:
            name_exists = session.query(Users).filter_by(name=message.text).first()
            if not name_exists:
                add_name_in_db(message, session)
                bot.send_message(chat_id, "Your name submitted successfully 👍🏻")
                return run_user_command(message, session, bot)
            else:
                bot.send_message(chat_id, "This name has already been used. Please choose a different one ⛔️")
                return process_name(message, session, bot)
        else:
            bot.send_message(chat_id, "Your name must be a string and should not contain any digits or symbols ⛔️")
            return process_name(message, session, bot)
    except SQLAlchemyError as e:
        add_log(f"SQLAlchemyError in check_name: {e}")
    except Exception as e:
        add_log(f"Exception in check_name: {e}")


def add_name_in_db(message, session):
    try:
        user = get_user(message, session)
        user.name = message.text
        session.commit()
    except SQLAlchemyError as e:
        add_log(f"SQLAlchemyError in add_name_in_db: {e}")
    except Exception as e:
        add_log(f"Exception in add_name_in_db: {e}")
