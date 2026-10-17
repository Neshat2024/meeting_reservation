from sqlalchemy import or_
from sqlalchemy.exc import SQLAlchemyError

from functions.get_functions_reserves import generate_random_hex_color
from functions.name import process_name
from models.reserve_bot import get_db_session
from models.users import Users
from services.config import get_user, add_user, set_command_in_wraps, check_role
from services.language import BotText, get_text
from services.log import add_log


def check_name_in_db(bot):
    def decorator(handler):
        def wrapper(message):
            needs_name = False
            with get_db_session() as session:
                username = message.chat.username
                user_exists = get_user_in_wraps(message, session)
                if not user_exists:
                    user_exists = add_user(message, session)
                elif user_exists and user_exists.username != username:
                    user_exists.username = username
                    session.commit()
                needs_name = bool(user_exists and not user_exists.name)
            if needs_name:
                return process_name(message, bot)
            return handler(message)

        return wrapper

    return decorator


def get_user_in_wraps(message, session):
    chat_id = str(message.chat.id)
    return session.query(Users).filter_by(chat_id=chat_id).first()


def set_command(command):
    def decorator(handler):
        def wrapper(message):
            with get_db_session() as session:
                user = get_user(message, session)
                if not user:
                    user = add_user(message, session)
                    if user:
                        set_command_in_wraps(user, session, command)
                else:
                    check_role(user, session)
                    set_command_in_wraps(user, session, command)
            return handler(message)

        return wrapper

    return decorator


def check_admin(bot):
    def decorator(handler):
        def wrapper(message):
            try:
                allowed = False
                chat_id = language = None
                with get_db_session() as session:
                    user = get_user(message, session)
                    if user.role in ["admin", "manager"]:
                        allowed = True
                    else:
                        user.command = None
                    chat_id, language = user.chat_id, user.language
                if allowed:
                    return handler(message)
                bot.send_message(chat_id, get_text(BotText.INVALID_ADMIN, language))
            except SQLAlchemyError as e:
                add_log(f"SQLAlchemyError in check_admin: {e}")
            except Exception as e:
                add_log(f"Exception in check_admin: {e}")

        return wrapper

    return decorator


def check_color():
    def decorator(handler):
        def wrapper(message):
            try:
                has_color = False
                with get_db_session() as session:
                    user = get_user(message, session)
                    if user.color:
                        has_color = True
                    else:
                        user.color = generate_random_hex_color()
                if has_color:
                    return handler(message)
            except SQLAlchemyError as e:
                add_log(f"SQLAlchemyError in check_color: {e}")
            except Exception as e:
                add_log(f"Exception in check_color: {e}")

        return wrapper

    return decorator
