from sqlalchemy.exc import SQLAlchemyError

from functions.run_command import run_user_command
from models.reserve_bot import get_db_session
from models.users import Users
from services.config import get_user, check_text_in_name
from services.language import get_text, BotText
from services.log import add_log


def process_name(message, bot):
    with get_db_session() as session:
        user = get_user(message, session)
        bot.send_message(
            int(user.chat_id),
            get_text(BotText.ENTER_NAME, user.language),
        )
    bot.register_next_step_handler(message, check_name, bot)


def check_name(message, bot):
    retry = False
    try:
        with get_db_session() as session:
            user = get_user(message, session)
            chat_id, language = user.chat_id, user.language
            text = check_text_in_name(message)
            if text is None:
                t = get_text(BotText.OPERATION_CANCELED, language)
                bot.send_message(chat_id, t)
            elif text:
                name_exists = session.query(Users).filter_by(name=message.text).first()
                if not name_exists:
                    add_name_in_db(message, session)
                    t = get_text(BotText.NAME_SUBMITTED, language).format(
                        name=message.text
                    )
                    bot.send_message(chat_id, t)
                    return run_user_command(message, session, bot)
                else:
                    t = get_text(BotText.INVALID_NAME_TAKEN, language)
                    bot.send_message(chat_id, t)
                    retry = True
            else:
                t = get_text(BotText.INVALID_NAME, language)
                bot.send_message(chat_id, t)
                retry = True
    except SQLAlchemyError as e:
        add_log(f"SQLAlchemyError in check_name: {e}")
        return
    except Exception as e:
        add_log(f"Exception in check_name: {e}")
        return
    if retry:
        return process_name(message, bot)


def add_name_in_db(message, session):
    try:
        user = get_user(message, session)
        user.name = message.text
        session.commit()
    except SQLAlchemyError as e:
        add_log(f"SQLAlchemyError in add_name_in_db: {e}")
    except Exception as e:
        add_log(f"Exception in add_name_in_db: {e}")
