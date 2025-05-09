import logging
import os
import sys

import telebot

from settings import settings


def add_log(the_error, file_path=None, checkout=False):
    log_channel_id = settings.LOG_CHANNEL_ID
    current_dir = os.path.dirname(settings.CLOCKIFY_LOG_DIR)
    logging_bot = telebot.TeleBot(settings.TOKEN_LOGGING)
    if checkout:
        if settings.PROXY_HOST and settings.PROXY_PORT:
            proxy_url = f"socks5h://{settings.PROXY_HOST}:{settings.PROXY_PORT}"
            telebot.apihelper.proxy = {"http": proxy_url, "https": proxy_url}
        log_filename = os.path.join(current_dir, f"{sys.argv[1]}_logs.log")
        logging.basicConfig(
            filename=log_filename,
            level=logging.ERROR,
            format="%(asctime)s - %(levelname)s - %(message)s",
        )
        logging.error(the_error)
        logging_bot.send_message(log_channel_id, f"{sys.argv[1]} - {the_error}")
    else:
        reserve_username = telebot.TeleBot(settings.TOKEN_RESERVE).get_me().username
        log_filename = os.path.join(current_dir, f"{reserve_username}_logs.log")
        logging.basicConfig(
            filename=log_filename,
            level=logging.ERROR,
            format="%(asctime)s - %(levelname)s - %(message)s",
        )
        logging.error(the_error)
        logging_bot.send_message(log_channel_id, f"{reserve_username} - {the_error}")
        try:
            if file_path:
                with open(file_path, "rb") as file:
                    backup_channel_id = settings.BACKUP_CHANNEL_ID
                    logging_bot.send_document(backup_channel_id, file)
        except Exception as e:
            logging_bot.send_message(log_channel_id, f"Error in sending Backup - {e}")
