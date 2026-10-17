from telebot import TeleBot
from telebot import types

from functions.settings_func import (
    process_settings,
    process_set_language_to_persian,
    process_set_language_to_english,
)
from models.reserve_bot import get_db_session
from services.wraps import set_command
from settings import commands


def add_settings_command():
    commands.append(
        types.BotCommand(command="/settings", description="⚙️ Bot Settings (Language)")
    )


def register_settings_command(bot):
    with get_db_session() as session:

        @bot.message_handler(commands=["settings"])
        @set_command("settings", session)
        def settings_command(message):
            return process_settings(message, session, bot)


def register_set_language_to_persian(bot):
    with get_db_session() as session:

        @bot.callback_query_handler(func=lambda call: call.data.startswith("fa-lang"))
        def set_language_to_persian(call):
            return process_set_language_to_persian(call, session, bot)


def register_set_language_to_english(bot):
    with get_db_session() as session:

        @bot.callback_query_handler(func=lambda call: call.data.startswith("en-lang"))
        def set_language_to_english(call):
            return process_set_language_to_english(call, session, bot)


def settings_command_handler(bot: TeleBot):
    add_settings_command()
    register_settings_command(bot)
    register_set_language_to_persian(bot)
    register_set_language_to_english(bot)
