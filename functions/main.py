from datetime import datetime as dt

import pytz
from dotenv import load_dotenv
from sqlalchemy.exc import SQLAlchemyError

from functions.name import process_name
from models.reservations import Reservations
from services.config import add_user, get_user, ENGLISH, FARSI
from services.language import get_text, BotText, change_num_as_lang
from services.log import add_log
from services.wraps import get_user_in_wraps

tehran_tz = pytz.timezone("Asia/Tehran")
load_dotenv()


def process_start(message, session, bot):
    try:
        uname = message.chat.username
        user = get_user(message, session)
        if user:
            bot.reply_to(message, get_text(BotText.START, user.language))
        else:
            bot.reply_to(message, get_text(BotText.START, FARSI))
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


def process_help(message, session, bot):
    user = get_user(message, session)
    if user:
        text = get_text(BotText.HELP, user.language)
    else:
        text = get_text(BotText.HELP, ENGLISH)
    bot.reply_to(message, text)


def process_ok_reservation(call, session, bot):
    try:
        msg_id = call.message.id
        user = get_user(call, session)
        now = dt.now(tehran_tz)
        book = session.query(Reservations).filter_by(id=call.data.split("_")[1]).first()
        if book:
            end_time = get_time_as_tehran_tz(book, book.end_time)
            start_time = get_time_as_tehran_tz(book, book.start_time)
            txt = ""
            if now > end_time:
                bot.answer_callback_query(
                    call.id,
                    get_text(BotText.INVALID_END_RESERVATION, user.language),
                    show_alert=True,
                )
                return
            if now < start_time:
                txt = get_text(BotText.FUTURE_MEETING_START, user.language).format(
                    start_time=book.start_time
                )
                txt = change_num_as_lang(txt, user.language)
            elif now < end_time:
                txt = get_text(BotText.FUTURE_MEETING_END, user.language).format(
                    start_time=book.end_time
                )
                txt = change_num_as_lang(txt, user.language)
            bot.edit_message_text(
                chat_id=int(user.chat_id), message_id=msg_id, text=txt
            )
        else:
            bot.answer_callback_query(
                call.id,
                get_text(BotText.RESERVE_NOT_EXISTS, user.language),
                show_alert=True,
            )
    except Exception as e:
        add_log(f"Exception in process_ok_reservation: {e}")


def process_cancel_reservation(call, session, bot):
    try:
        msg_id = call.message.id
        user = get_user(call, session)
        now = dt.now(tehran_tz)
        book = session.query(Reservations).filter_by(id=call.data.split("_")[1]).first()
        if book:
            end_time = get_time_as_tehran_tz(book, book.end_time)
            start_time = get_time_as_tehran_tz(book, book.start_time)
            if now > end_time:
                bot.answer_callback_query(
                    call.id,
                    get_text(BotText.INVALID_CANCEL_RESERVATION, user.language),
                    show_alert=True,
                )
                return
            txt = ""
            if now < start_time:
                txt = cancel_before_start_time(session, book, user)
            elif now < end_time:
                txt = cancel_after_start_time(session, [book, user], now)
                txt = change_num_as_lang(txt, user.language)
            bot.edit_message_text(
                chat_id=int(user.chat_id), message_id=msg_id, text=txt
            )
        else:
            bot.answer_callback_query(
                call.id,
                get_text(BotText.RESERVE_NOT_EXISTS, user.language),
                show_alert=True,
            )
    except Exception as e:
        add_log(f"Exception in process_cancel_reservation: {e}")


def get_time_as_tehran_tz(reserve, time):
    str_time = f"{reserve.date} {time}"
    dt_time = dt.strptime(str_time, "%Y-%m-%d %H:%M")
    return tehran_tz.localize(dt_time)


def cancel_before_start_time(session, book, user):
    try:
        session.delete(book)
        session.commit()
        return get_text(BotText.CANCEL_FIXED, user.language)
    except SQLAlchemyError as e:
        add_log(f"SQLAlchemyError in cancel_before_start_time: {e}")
    except Exception as e:
        add_log(f"Exception in cancel_before_start_time: {e}")


def cancel_after_start_time(session, book_user, now):
    try:
        book, user = book_user
        str_time = f"{str(now.hour).zfill(2)}:{str(now.minute).zfill(2)}"
        book.end_time = str_time
        session.commit()
        return get_text(BotText.CANCEL_FIXED_TIME, user.language).format(
            str_time=str_time
        )
    except SQLAlchemyError as e:
        add_log(f"SQLAlchemyError in cancel_after_start_time: {e}")
    except Exception as e:
        add_log(f"Exception in cancel_after_start_time: {e}")


def process_checkout_reservation(call, session, bot):
    try:
        msg_id = call.message.id
        user = get_user(call, session)
        now = dt.now(tehran_tz)
        db_id = call.data.split("_")[1]
        reserve = session.query(Reservations).filter_by(id=db_id).first()
        if reserve:
            end_time = get_time_as_tehran_tz(reserve, reserve.end_time)
            if now < end_time:
                str_time = f"{str(now.hour).zfill(2)}:{str(now.minute).zfill(2)}"
                reserve.end_time = str_time
                session.commit()
                txt = get_text(BotText.CHECKOUT_FIXED, user.language).format(
                    str_time=str_time
                )
                txt = change_num_as_lang(txt, user.language)
                bot.edit_message_text(
                    chat_id=int(user.chat_id), message_id=msg_id, text=txt
                )
            else:
                bot.answer_callback_query(
                    call.id,
                    get_text(BotText.INVALID_CHECKOUT_RESERVATION, user.language),
                    show_alert=True,
                )
        else:
            bot.answer_callback_query(
                call.id,
                get_text(BotText.RESERVE_NOT_EXISTS, user.language),
                show_alert=True,
            )
    except Exception as e:
        add_log(f"Exception in process_checkout_reservation: {e}")
