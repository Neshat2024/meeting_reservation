from telebot import TeleBot, types

from functions.main import process_start, process_help
from services.config import commands


def add_main_commands_report():
    commands.extend(
        [
            types.BotCommand(command="/help", description="ℹ️ Help information")
        ]
    )


def register_start_command(session, bot):
    @bot.message_handler(commands=["start"])
    def start_command(message):
        return process_start(message, session, bot)


def register_help_command(bot):
    @bot.message_handler(commands=["help"])
    def help_command(message):
        return process_help(message, bot)


def start_help_handler(bot: TeleBot, session):
    add_main_commands_report()
    register_start_command(session, bot)
    register_help_command(bot)
