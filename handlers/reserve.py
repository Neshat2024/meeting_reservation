from telebot import TeleBot
from telebot import types

from functions.reserve import process_reservation
from services.config import commands
from services.wraps import set_command, check_name_in_db


def add_reservation_command():
    commands.append(
        types.BotCommand(command="/reservation", description="🚪 Reserve Meeting Room")
    )


def register_reservation_command(session, bot):
    @bot.message_handler(commands=["reservation"])
    @set_command("reservation", session)
    @check_name_in_db(session, bot)
    def reservation_command(message):
        return process_reservation(message, session, bot)


# def register_handle_ws_selection(session, bot):
#     @bot.callback_query_handler(func=lambda call: call.data.startswith("hw_"))
#     # @check_username(bot, session, User)
#     def handle_workspace_selection(call):
#         return process_workspace_selection(call, session, bot)


def reservation_command_handler(bot: TeleBot, session):
    add_reservation_command()
    register_reservation_command(session, bot)
    # register_handle_ws_selection(session, bot)
