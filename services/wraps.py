from sqlalchemy import or_
from sqlalchemy.exc import SQLAlchemyError

from functions.get_functions_reserves import generate_random_hex_color
from functions.name import process_name
from models.users import Users
from services.config import get_user, add_user, set_command_in_wraps, check_role
from services.language import BotText, get_text
from services.log import add_log


def check_name_in_db(session, bot):
    def decorator(handler):
        def wrapper(message):
            username = message.chat.username
            user_exists = get_user_in_wraps(message, session)
            if not user_exists:
                user_exists = add_user(message, session)
            elif user_exists and user_exists.username != username:
                user_exists.username = username
                session.commit()
            if user_exists and not user_exists.name:
                return process_name(message, session, bot)
            return handler(message)

        return wrapper

    return decorator


def get_user_in_wraps(message, session):
    chat_id = str(message.chat.id)
    return session.query(Users).filter_by(chat_id=chat_id).first()


def set_command(command, session):
    def decorator(handler):
        def wrapper(message):
            user = get_user(message, session)
            if not user:
                user = add_user(message, session)
                set_command_in_wraps(user, session, command)
            else:
                check_role(user, session)
                set_command_in_wraps(user, session, command)
            return handler(message)

        return wrapper

    return decorator


def check_admin(session, bot):
    def decorator(handler):
        def wrapper(message):
            try:
                user = get_user(message, session)
                if user.role in ["admin", "manager"]:
                    return handler(message)
                text = get_text(BotText.INVALID_ADMIN, user.language)
                user.command = None
                session.commit()
                bot.send_message(user.chat_id, text)
            except SQLAlchemyError as e:
                add_log(f"SQLAlchemyError in check_admin: {e}")
            except Exception as e:
                add_log(f"Exception in check_admin: {e}")

        return wrapper

    return decorator


def check_color(session):
    def decorator(handler):
        def wrapper(message):
            try:
                user = get_user(message, session)
                if user.color:
                    return handler(message)
                else:
                    user.color = generate_random_hex_color()
                    session.commit()
            except SQLAlchemyError as e:
                add_log(f"SQLAlchemyError in check_color: {e}")
            except Exception as e:
                add_log(f"Exception in check_color: {e}")

        return wrapper

    return decorator
