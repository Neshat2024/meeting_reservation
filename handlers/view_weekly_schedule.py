from telebot import TeleBot
from telebot import types

from functions.view_weekly_schedule import process_view_weekly_schedule
from services.config import commands
from services.wraps import set_command, check_name_in_db


def add_view_weekly_schedule_command():
    commands.append(
        types.BotCommand(command="/view_weekly_schedule", description="🗓 Weekly Schedule for Meeting Rooms")
    )


def register_view_weekly_schedule_command(session, bot):
    @bot.message_handler(commands=["view_weekly_schedule"])
    @set_command("view", session)
    @check_name_in_db(session, bot)
    def view_weekly_schedule_command(message):
        return process_view_weekly_schedule(message, session, bot)


# def register_handle_ws_selection(session, bot):
#     @bot.callback_query_handler(func=lambda call: call.data.startswith("hw_"))
#     # @check_username(bot, session, User)
#     def handle_workspace_selection(call):
#         return process_workspace_selection(call, session, bot)


def view_weekly_schedule_command_handler(bot: TeleBot, session):
    add_view_weekly_schedule_command()
    register_view_weekly_schedule_command(session, bot)
    # register_handle_ws_selection(session, bot)
