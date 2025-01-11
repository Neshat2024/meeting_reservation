from sqlalchemy import or_
from sqlalchemy.exc import SQLAlchemyError

from functions.name import process_name
from models.users import Users
from services.config import get_user, add_user, set_command_in_wraps
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
    chat_id, uname = str(message.chat.id), message.chat.username
    return (
        session.query(Users)
        .filter(or_(Users.chat_id == chat_id, Users.username == uname))
        .first()
    )


def set_command(command, session):
    def decorator(handler):
        def wrapper(message):
            user = get_user(message, session)
            if not user:
                user = add_user(message, session)
                set_command_in_wraps(user, session, command)
            else:
                set_command_in_wraps(user, session, command)
            return handler(message)

        return wrapper

    return decorator


def check_admin(session, bot):
    def decorator(handler):
        def wrapper(message):
            try:
                chat_id = str(message.chat.id)
                user = session.query(Users).filter_by(chat_id=chat_id).first()
                if user.role == "admin":
                    return handler(message)
                text = "You are not admin, and you can't access this command ⛔️"
                user.command = None
                session.commit()
                bot.send_message(chat_id, text)
            except SQLAlchemyError as e:
                add_log(f"SQLAlchemyError in check_admin: {e}", bot.get_me().username)
            except Exception as e:
                add_log(f"Exception in check_admin: {e}", bot.get_me().username)

        return wrapper

    return decorator
