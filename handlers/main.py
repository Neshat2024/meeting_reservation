from telebot import TeleBot, types

from functions.main import (
    process_start,
    process_help,
    process_checkout_reservation,
    process_cancel_reservation,
    process_ok_reservation,
)
from settings import commands


def add_main_commands_report():
    commands.extend(
        [types.BotCommand(command="/help", description="ℹ️ Help information")]
    )


def register_start_command(session, bot):
    @bot.message_handler(commands=["start"])
    def start_command(message):
        return process_start(message, session, bot)


def register_help_command(session, bot):
    @bot.message_handler(commands=["help"])
    def help_command(message):
        return process_help(message, session, bot)


def register_handle_ok_reservation(session, bot):
    @bot.callback_query_handler(
        func=lambda call: call.data.startswith("ok-before-meeting")
    )
    def handle_ok_reservation(call):
        return process_ok_reservation(call, session, bot)


def register_handle_cancel_reservation(session, bot):
    @bot.callback_query_handler(func=lambda call: call.data.startswith("cancel_"))
    def handle_cancel_reservation(call):
        return process_cancel_reservation(call, session, bot)


def register_handle_checkout_reservation(session, bot):
    @bot.callback_query_handler(func=lambda call: call.data.startswith("checkout_"))
    def handle_checkout_reservation(call):
        return process_checkout_reservation(call, session, bot)


def start_help_handler(bot: TeleBot, session):
    add_main_commands_report()
    register_start_command(session, bot)
    register_help_command(session, bot)
    register_handle_ok_reservation(session, bot)
    register_handle_cancel_reservation(session, bot)
    register_handle_checkout_reservation(session, bot)
