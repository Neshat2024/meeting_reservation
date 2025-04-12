from telebot import TeleBot
from telebot import types

from functions.admin_commands_one import (
    process_admin_commands,
    process_add_room,
    process_update_room,
    process_update_specific_room,
    process_delete_room,
    process_delete_specific_room,
    process_back_room,
    process_view_users,
    process_delete_users,
)
from functions.admin_commands_two import (
    process_edit_users_name,
    process_edit_specific_name,
    process_charge_user,
    process_get_charge_for_user,
    process_delete_specific_user,
)
from services.config import commands
from services.wraps import set_command, check_name_in_db, check_admin


def add_admin_commands():
    commands.append(
        types.BotCommand(
            command="/admin_commands", description="🔧 Admins can manage Meeting Rooms"
        )
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


def register_handle_view_users(session, bot):
    @bot.callback_query_handler(func=lambda call: call.data.startswith("view_users"))
    def handle_view_users(call):
        return process_view_users(call, session, bot)


def register_handle_delete_users(session, bot):
    @bot.callback_query_handler(func=lambda call: call.data.startswith("del_users"))
    def handle_delete_users(call):
        return process_delete_users(call, session, bot)


def register_handle_back_room(session, bot):
    @bot.callback_query_handler(func=lambda call: call.data.startswith("backroom"))
    def handle_back_room(call):
        return process_back_room(call.message, session, bot)


def part_one_admin_cmd(bot, session):
    register_admin_commands(session, bot)
    register_handle_add_room(session, bot)
    register_handle_edit_room(session, bot)
    register_handle_edit_specific_room(session, bot)
    register_handle_delete_room(session, bot)
    register_handle_delete_specific_room(session, bot)
    register_handle_view_users(session, bot)
    register_handle_delete_users(session, bot)
    register_handle_back_room(session, bot)


def register_handle_edit_users_name(session, bot):
    @bot.callback_query_handler(func=lambda call: call.data.startswith("editname"))
    def handle_edit_users_name(call):
        return process_edit_users_name(call, session, bot)


def register_handle_edit_specific_name(session, bot):
    @bot.callback_query_handler(func=lambda call: call.data.startswith("e_name_"))
    def handle_edit_specific_name(call):
        return process_edit_specific_name(call, session, bot)


def register_handle_back_view(session, bot):
    @bot.callback_query_handler(func=lambda call: call.data.startswith("back-view"))
    def handle_back_view(call):
        return process_view_users(call, session, bot)


def register_handle_back_users_view(session, bot):
    @bot.callback_query_handler(
        func=lambda call: call.data.startswith("back-users-view")
    )
    def handle_back_users_view(call):
        return process_edit_users_name(call, session, bot)


def register_handle_delete_specific_user(session, bot):
    @bot.callback_query_handler(func=lambda call: call.data.startswith("d-user_"))
    def handle_delete_specific_user(call):
        return process_delete_specific_user(call, session, bot)


def register_handle_charge_user(session, bot):
    @bot.callback_query_handler(func=lambda call: call.data.startswith("charge_user"))
    def handle_charge_user(call):
        return process_charge_user(call, session, bot)


def register_get_charge_for_user(session, bot):
    @bot.callback_query_handler(func=lambda call: call.data.startswith("ch-user_"))
    def handle_get_charge_for_user(call):
        return process_get_charge_for_user(call, session, bot)


def register_handle_back_charge(session, bot):
    @bot.callback_query_handler(
        func=lambda call: call.data.startswith("back-charge-user")
    )
    def handle_back_charge(call):
        return process_charge_user(call, session, bot)


def part_two_admin_cmd(bot, session):
    register_handle_edit_users_name(session, bot)
    register_handle_edit_specific_name(session, bot)
    register_handle_back_view(session, bot)
    register_handle_back_users_view(session, bot)
    register_handle_delete_specific_user(session, bot)
    register_handle_charge_user(session, bot)
    register_get_charge_for_user(session, bot)
    register_handle_back_charge(session, bot)


def admin_commands_handler(bot: TeleBot, session):
    add_admin_commands()
    part_one_admin_cmd(bot, session)
    part_two_admin_cmd(bot, session)
