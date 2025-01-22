from datetime import datetime as dt

import pytz
from dotenv import load_dotenv
from sqlalchemy.exc import SQLAlchemyError

from functions.name import process_name
from models.reservations import Reservations
from services.config import add_user
from services.log import add_log
from services.wraps import get_user_in_wraps

tehran_tz = pytz.timezone("Asia/Tehran")
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
        "/settings - ⚙️ Bot Settings (You can set Language of the bot)"
        "/help - ℹ️ Get help information\n"
    )
    bot.reply_to(message, text)


def process_ok_reservation(call, session, bot):
    try:
        chat_id, msg_id = call.message.chat.id, call.message.id
        now = dt.now(tehran_tz)
        book = session.query(Reservations).filter_by(id=call.data.split("_")[1]).first()
        if book:
            end_time = get_time_as_tehran_tz(book, book.end_time)
            start_time = get_time_as_tehran_tz(book, book.start_time)
            if now > end_time:
                bot.answer_callback_query(call.id, "This reservation has finished and buttons doesn't work ⛔️")
                return
            if now < start_time:
                txt = f"Your meeting will start at {book.start_time} ✅"
            elif now < end_time:
                txt = f"Your meeting will end at {book.end_time} ✅"
            bot.edit_message_text(chat_id=chat_id, message_id=msg_id, text=txt)
        else:
            bot.answer_callback_query(call.id, "This reservation doesn't exist ⛔️")
    except Exception as e:
        add_log(f"Exception in process_ok_reservation: {e}")


def process_cancel_reservation(call, session, bot):
    try:
        chat_id, msg_id = call.message.chat.id, call.message.id
        now = dt.now(tehran_tz)
        book = session.query(Reservations).filter_by(id=call.data.split("_")[1]).first()
        if book:
            end_time = get_time_as_tehran_tz(book, book.end_time)
            start_time = get_time_as_tehran_tz(book, book.start_time)
            if now > end_time:
                bot.answer_callback_query(call.id, "This reservation has finished and you can't cancel it ⛔️")
                return
            if now < start_time:
                txt = cancel_before_start_time(session, book)
            elif now < end_time:
                txt = cancel_after_start_time(session, book, now)
            bot.edit_message_text(chat_id=chat_id, message_id=msg_id, text=txt)
        else:
            bot.answer_callback_query(call.id, "This reservation doesn't exist ⛔️")
    except Exception as e:
        add_log(f"Exception in process_cancel_reservation: {e}")


def get_time_as_tehran_tz(reserve, time):
    str_time = f"{reserve.date} {time}"
    dt_time = dt.strptime(str_time, "%Y-%m-%d %H:%M")
    return tehran_tz.localize(dt_time)


def cancel_before_start_time(session, book):
    try:
        session.delete(book)
        session.commit()
        return "Your meeting canceled successfully ✅"
    except SQLAlchemyError as e:
        add_log(f"SQLAlchemyError in cancel_before_start_time: {e}")
    except Exception as e:
        add_log(f"Exception in cancel_before_start_time: {e}")


def cancel_after_start_time(session, book, now):
    try:
        str_time = f"{str(now.hour).zfill(2)}:{str(now.minute).zfill(2)}"
        book.end_time = str_time
        session.commit()
        return f"You canceled your meeting at «{str_time}» successfully ✅"
    except SQLAlchemyError as e:
        add_log(f"SQLAlchemyError in cancel_after_start_time: {e}")
    except Exception as e:
        add_log(f"Exception in cancel_after_start_time: {e}")


def process_checkout_reservation(call, session, bot):
    try:
        chat_id, msg_id = call.message.chat.id, call.message.id
        now = dt.now(tehran_tz)
        db_id = call.data.split("_")[1]
        reserve = session.query(Reservations).filter_by(id=db_id).first()
        if reserve:
            end_time = get_time_as_tehran_tz(reserve, reserve.end_time)
            if now < end_time:
                str_time = f"{str(now.hour).zfill(2)}:{str(now.minute).zfill(2)}"
                reserve.end_time = str_time
                session.commit()
                txt = f"Thanks for your attention 🙏🏻\nYou checked out your meeting at {str_time}"
                bot.edit_message_text(chat_id=chat_id, message_id=msg_id, text=txt)
            else:
                bot.answer_callback_query(call.id, "This reservation has finished and you can't checkout it ⛔️")
        else:
            bot.answer_callback_query(call.id, "This reservation doesn't exist ⛔️")
    except Exception as e:
        add_log(f"Exception in process_checkout_reservation: {e}")
