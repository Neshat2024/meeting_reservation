from telebot import TeleBot
from telebot import types

from functions.admin_commands import process_admin_commands, process_add_room, process_update_room, \
    process_update_specific_room, \
    process_delete_room, process_delete_specific_room, process_back_room
from services.config import commands
from services.wraps import set_command, check_name_in_db, check_admin


def add_admin_commands():
    commands.append(
        types.BotCommand(command="/admin_commands", description="🔧 Admins can manage Meeting Rooms")
    )


def register_admin_commands(session, bot):
    @bot.message_handler(commands=["admin_commands"])
    @set_command("admin_commands", session)
    @check_admin(session, bot)
    @check_name_in_db(session, bot)
    def admin_commands(message):
        return process_admin_commands(message, session, bot)


def register_handle_add_room(session, bot):
    @bot.callback_query_handler(func=lambda call: call.data.startswith("add_room"))
    def handle_add_room(call):
        return process_add_room(call, session, bot)


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


def admin_commands_handler(bot: TeleBot, session):
    add_admin_commands()
    register_admin_commands(session, bot)
    register_handle_add_room(session, bot)
    register_handle_edit_room(session, bot)
    register_handle_edit_specific_room(session, bot)
    register_handle_delete_room(session, bot)
    register_handle_delete_specific_room(session, bot)
    register_handle_back_room(session, bot)
