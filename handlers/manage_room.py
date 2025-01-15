from telebot import TeleBot
from telebot import types

from functions.manage_room import process_manage_room, process_add_room, process_update_room, \
    process_update_specific_room, \
    process_delete_room, process_delete_specific_room, process_back_room
from services.config import commands
from services.wraps import set_command, check_name_in_db, check_admin


def add_manage_room_command():
    commands.append(
        types.BotCommand(command="/manage_rooms", description="🛠 Manage Meeting Rooms")
    )


def register_manage_room_command(session, bot):
    @bot.message_handler(commands=["manage_rooms"])
    @set_command("manage_rooms", session)
    @check_admin(session, bot)
    @check_name_in_db(session, bot)
    def manage_room_command(message):
        return process_manage_room(message, session, bot)


def register_handle_add_room(session, bot):
    @bot.callback_query_handler(func=lambda call: call.data.startswith("add_room"))
    def handle_add_room(call):
        return process_add_room(call.message, session, bot)


def register_handle_edit_room(session, bot):
    @bot.callback_query_handler(func=lambda call: call.data.startswith("editroom"))
    def handle_edit_room(call):
        return process_update_room(call, session, bot)


def register_handle_edit_specific_room(session, bot):
    @bot.callback_query_handler(func=lambda call: call.data.startswith("edit_"))
    def handle_edit_specific_room(call):
        return process_update_specific_room(call, session, bot)


def register_handle_delete_room(session, bot):
    @bot.callback_query_handler(func=lambda call: call.data.startswith("deleteroom"))
    def handle_delete_room(call):
        return process_delete_room(call, session, bot)


def register_handle_delete_specific_room(session, bot):
    @bot.callback_query_handler(func=lambda call: call.data.startswith("delete_"))
    def handle_delete_specific_room(call):
        return process_delete_specific_room(call, session, bot)


def register_handle_back_room(session, bot):
    @bot.callback_query_handler(func=lambda call: call.data.startswith("backroom"))
    def handle_back_room(call):
        return process_back_room(call.message, session, bot)


def manage_room_command_handler(bot: TeleBot, session):
    add_manage_room_command()
    register_manage_room_command(session, bot)
    register_handle_add_room(session, bot)
    register_handle_edit_room(session, bot)
    register_handle_edit_specific_room(session, bot)
    register_handle_delete_room(session, bot)
    register_handle_delete_specific_room(session, bot)
    register_handle_back_room(session, bot)
