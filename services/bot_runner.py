import os
import subprocess
import threading
import time
from datetime import datetime as dt

import pytz
import schedule
import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

from models.users import Users, SessionLocal
from services.log import add_log
from settings import settings

session = SessionLocal()
tehran_tz = pytz.timezone("Asia/Tehran")


def backup_command(backup_file):
    db_name = "reservebot"
    return [
        "pg_dump",
        "-h",
        "localhost",
        "-p",
        "5432",
        "-U",
        settings.POSTGRES_USER,
        db_name,
        "-f",
        backup_file,
    ]


def backup_database(bot):
    os.environ["PGPASSWORD"] = settings.POSTGRES_PASSWORD
    backup_dir = "backups"
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    timestamp = dt.now(tehran_tz).strftime("%Y%m%d_%H%M%S")
    bot_username = bot.get_me().username
    backup_file = os.path.join(backup_dir, f"{bot_username}_{timestamp}.sql")
    command = backup_command(backup_file)
    flag = True
    try:
        subprocess.run(command, check=True)
        txt = f"Backup created at: {backup_file}"
        add_log(txt, file_path=backup_file)
    except subprocess.CalledProcessError as e:
        add_log(f"Error during backup: {e}")
        flag = False
    except Exception as e:
        add_log(f"Exception during backup: {e}")
        flag = False
    finally:
        if "PGPASSWORD" in os.environ:
            del os.environ["PGPASSWORD"]
        if flag:
            os.remove(backup_file)


def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)


def runner(bot):
    add_log(f"Bot Started at {dt.now(tehran_tz).strftime('%Y-%m-%d %H:%M:%S')}")
    print("Bot is polling...")
    threading.Thread(target=run_scheduler, daemon=True).start()
    schedule.every(6).hours.do(job_func=backup_database, bot=bot)
    bot.infinity_polling()
    add_log(f"Bot Stopped at {dt.now(tehran_tz).strftime('%Y-%m-%d %H:%M:%S')}")


class MyBot(telebot.TeleBot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Create your fixed keyboard
        # self.fixed_keyboard_en = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        # self.fixed_keyboard_en.add(
        #     KeyboardButton("🚪 Reservation"),
        #     KeyboardButton("🗓 View Schedule"),
        # )
        #
        # self.fixed_keyboard_fa = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        # self.fixed_keyboard_fa.add(
        #     KeyboardButton("🚪 رزرو اتاق"),
        #     KeyboardButton("🗓 مشاهده جدول رزرو ها"),
        # )
        #
        # if settings.IS_CONTINUOUS_RESERVE_AVAILABLE.lower() == "true":
        #     self.fixed_keyboard_en.add(KeyboardButton("🔄 Continuous Reservation"))
        #     self.fixed_keyboard_fa.add(KeyboardButton("🔄 رزرو دوره ای"))

        self.fixed_keyboard_en = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        self.fixed_keyboard_fa = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)

        # English buttons
        en_buttons = [
            KeyboardButton("🚪 Reservation"),
            KeyboardButton("🗓 View Schedule"),
        ]

        # Farsi buttons
        fa_buttons = [
            KeyboardButton("🚪 رزرو اتاق"),
            KeyboardButton("🗓 مشاهده جدول رزرو ها"),
        ]

        if settings.IS_CONTINUOUS_RESERVE_AVAILABLE.lower() == "true":
            # Insert the continuous reservation button in the middle (index 1)
            en_buttons.insert(1, KeyboardButton("🔄 Continuous Reservation"))
            fa_buttons.insert(1, KeyboardButton("🔄 رزرو دوره ای"))

        # Add all buttons at once
        self.fixed_keyboard_en.add(*en_buttons)
        self.fixed_keyboard_fa.add(*fa_buttons)

    def _add_keyboard_if_needed(self, chat_id, kwargs):
        """Helper method to add keyboard to kwargs if not specified"""
        if "reply_markup" not in kwargs or kwargs["reply_markup"] is None:
            user = session.query(Users).filter_by(chat_id=str(chat_id)).first()
            if user:
                kwargs["reply_markup"] = (
                    self.fixed_keyboard_en
                    if user.language == "en"
                    else self.fixed_keyboard_fa
                )
            else:
                kwargs["reply_markup"] = self.fixed_keyboard_fa
        return kwargs

    # Text messages
    def send_message(self, chat_id, text, *args, **kwargs):
        kwargs = self._add_keyboard_if_needed(chat_id, kwargs)
        return super().send_message(chat_id, text, *args, **kwargs)

    def reply_to(self, message, text, *args, **kwargs):
        kwargs = self._add_keyboard_if_needed(message.chat.id, kwargs)
        return super().reply_to(message, text, **kwargs)

    # Media messages
    def send_photo(self, chat_id, photo, *args, **kwargs):
        kwargs = self._add_keyboard_if_needed(chat_id, kwargs)
        return super().send_photo(chat_id, photo, *args, **kwargs)

    # Message editing
    def edit_message_text(
        self, chat_id=None, message_id=None, text=None, reply_markup=None, **kwargs
    ):
        return super().edit_message_text(
            text=text,
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=reply_markup,
            **kwargs,
        )

    def edit_message_reply_markup(
        self, chat_id=None, message_id=None, reply_markup=None, **kwargs
    ):
        return super().edit_message_reply_markup(
            chat_id=chat_id, message_id=message_id, reply_markup=reply_markup, **kwargs
        )

    # Message deletion (no keyboard needed)
    def delete_message(self, chat_id, message_id, *args, **kwargs):
        return super().delete_message(chat_id, message_id, *args, **kwargs)

    # Callback queries
    def answer_callback_query(
        self, callback_query_id, text=None, show_alert=None, **kwargs
    ):
        return super().answer_callback_query(
            callback_query_id=callback_query_id,
            text=text,
            show_alert=show_alert,
        )
