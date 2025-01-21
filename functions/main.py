from dotenv import load_dotenv
from sqlalchemy.exc import SQLAlchemyError

from functions.name import process_name
from services.config import add_user
from services.log import add_log
from services.wraps import get_user_in_wraps

load_dotenv()


def process_start(message, session, bot):
    try:
        chat_id, uname = str(message.chat.id), message.chat.username
        bot.send_message(chat_id, "Hello! I can help you to Reserve a Meeting Room 🚪")
        user_exists = get_user_in_wraps(message, session)
        if not user_exists:
            user_exists = add_user(message, session)
        elif user_exists and user_exists.username != uname:
            user_exists.username = uname
            session.commit()
        if user_exists and not user_exists.name:
            return process_name(message, session, bot)
    except SQLAlchemyError as e:
        add_log(f"SQLAlchemyError in process_start: {e}")
    except Exception as e:
        add_log(f"Exception in process_start: {e}")


def process_help(message, bot):
    text = (
        "🚪 Meeting Reservation Bot 🚪\n\nAvailable Commands:\n"
        "/start - Start the bot to select from menu\n"
        "/reservation - 🚪 Submit-View-Edit Meeting Reservations\n"
        "/admin_commands - 🔧 Admins can manage Meeting Rooms (view-add-edit)\n"
        "/view_schedule - 🗓 View Schedule for Meeting Rooms (Daily-Custom Day-Weekly)\n"
        "/help - ℹ️ Get help information\n"
    )
    bot.reply_to(message, text)
