from telebot import TeleBot
from telebot import types

from functions.new_reserves import process_reservation, process_hour_selection, process_select_room, process_add_time, \
    process_remove_time, process_back_date, process_confirm_selection, process_new_reservation, process_back_main, \
    process_who_reserved
from functions.old_reserves import process_user_reservations, process_future_reservations, process_past_reservations, \
    process_delete_reservations, process_edit_reservations, process_edit_specific_reservation, \
    process_edit_specific_date, process_edit_specific_room, \
    process_edit_specific_hours, process_set_edit_date, process_set_edit_room, process_set_edit_hours, \
    process_add_time_in_edit, process_remove_time_in_edit, process_delete_specific_reservation
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


def register_handle_new_reservation(session, bot):
    @bot.callback_query_handler(func=lambda call: call.data.startswith("new_reservation"))
    def handle_new_reservation(call):
        return process_new_reservation(call, session, bot)


def register_handle_back_main(session, bot):
    @bot.callback_query_handler(func=lambda call: call.data.startswith("backmain"))
    def handle_back_main(call):
        return process_back_main(call, session, bot)


def register_handle_select_room(session, bot):
    @bot.callback_query_handler(func=lambda call: call.data.startswith("room_"))
    def handle_select_room(call):
        return process_select_room(call, session, bot)


def register_handle_back_date(session, bot):
    @bot.callback_query_handler(func=lambda call: call.data.startswith("backdate"))
    def handle_back_date(call):
        return process_back_date(call, session, bot)


def register_handle_hour_selection(session, bot):
    @bot.callback_query_handler(func=lambda call: call.data.startswith("dt_"))
    def handle_hour_selection(call):
        return process_hour_selection(call, session, bot)


def register_handle_add_time(session, bot):
    @bot.callback_query_handler(func=lambda call: call.data.startswith("time_select"))
    def handle_add_time(call):
        return process_add_time(call, session, bot)


def register_handle_remove_time(session, bot):
    @bot.callback_query_handler(func=lambda call: call.data.startswith("time_remove"))
    def handle_remove_time(call):
        return process_remove_time(call, session, bot)


def register_handle_confirm_selection(session, bot):
    @bot.callback_query_handler(func=lambda call: call.data.startswith("confirm-hours"))
    def handle_confirm_selection(call):
        return process_confirm_selection(call, session, bot)


def register_handle_user_reservations(session, bot):
    @bot.callback_query_handler(func=lambda call: call.data.startswith("user_reservations"))
    def handle_user_reservations(call):
        return process_user_reservations(call, session, bot)


def register_handle_future_reservations(session, bot):
    @bot.callback_query_handler(func=lambda call: call.data.startswith("future"))
    def handle_future_reservations(call):
        return process_future_reservations(call, session, bot)


def register_handle_edit_reservations(session, bot):
    @bot.callback_query_handler(func=lambda call: call.data.startswith("editreservation"))
    def handle_edit_reservations(call):
        return process_edit_reservations(call, session, bot)


def register_handle_edit_specific_reservation(session, bot):
    @bot.callback_query_handler(func=lambda call: call.data.startswith("e_r_"))
    def handle_edit_specific_reservation(call):
        return process_edit_specific_reservation(call, session, bot)


def register_handle_edit_specific_date(session, bot):
    @bot.callback_query_handler(func=lambda call: call.data.startswith("e_date_"))
    def handle_edit_specific_date(call):
        return process_edit_specific_date(call, session, bot)


def register_handle_set_edit_date(session, bot):
    @bot.callback_query_handler(func=lambda call: call.data.startswith("set_e_"))
    def handle_set_edit_date(call):
        return process_set_edit_date(call, session, bot)


def register_handle_back_specific(session, bot):
    @bot.callback_query_handler(func=lambda call: call.data.startswith("backspecific"))
    def handle_back_specific(call):
        return process_edit_specific_reservation(call, session, bot)


def register_handle_edit_specific_room(session, bot):
    @bot.callback_query_handler(func=lambda call: call.data.startswith("e_room_"))
    def handle_edit_specific_room(call):
        return process_edit_specific_room(call, session, bot)


def register_handle_set_edit_room(session, bot):
    @bot.callback_query_handler(func=lambda call: call.data.startswith("set_r_"))
    def handle_set_edit_room(call):
        return process_set_edit_room(call, session, bot)


def register_handle_edit_specific_hours(session, bot):
    @bot.callback_query_handler(func=lambda call: call.data.startswith("e_hours_"))
    def handle_edit_specific_hours(call):
        return process_edit_specific_hours(call, session, bot)


def register_handle_add_time_in_edit(session, bot):
    @bot.callback_query_handler(func=lambda call: call.data.startswith("e-t_select_"))
    def handle_add_time_in_edit(call):
        return process_add_time_in_edit(call, session, bot)


def register_handle_remove_time_in_edit(session, bot):
    @bot.callback_query_handler(func=lambda call: call.data.startswith("e-t_remove_"))
    def handle_remove_time_in_edit(call):
        return process_remove_time_in_edit(call, session, bot)


def register_handle_set_edit_hours(session, bot):
    @bot.callback_query_handler(func=lambda call: call.data.startswith("set_h_"))
    def handle_set_edit_hours(call):
        return process_set_edit_hours(call, session, bot)


def register_handle_back_edit(session, bot):
    @bot.callback_query_handler(func=lambda call: call.data.startswith("backedit"))
    def handle_back_edit(call):
        return process_edit_reservations(call, session, bot)


def register_handle_delete_reservations(session, bot):
    @bot.callback_query_handler(func=lambda call: call.data.startswith("deletereservation"))
    def handle_delete_reservations(call):
        return process_delete_reservations(call, session, bot)


def register_handle_delete_specific_reservation(session, bot):
    @bot.callback_query_handler(func=lambda call: call.data.startswith("d_r_"))
    def handle_delete_specific_reservation(call):
        return process_delete_specific_reservation(call, session, bot)


def register_handle_back_future(session, bot):
    @bot.callback_query_handler(func=lambda call: call.data.startswith("backfuture"))
    def handle_back_future(call):
        return process_future_reservations(call, session, bot)


def register_handle_past_reservations(session, bot):
    @bot.callback_query_handler(func=lambda call: call.data.startswith("past_reservations_"))
    def handle_past_reservations(call):
        page = int(call.data.split("_")[-1])
        return process_past_reservations([call, page], session, bot)


def register_handle_back_user(session, bot):
    @bot.callback_query_handler(func=lambda call: call.data.startswith("backuser"))
    def handle_back_user(call):
        return process_user_reservations(call, session, bot)


def register_handle_who_reserved(session, bot):
    @bot.callback_query_handler(func=lambda call: call.data.startswith("who_"))
    def handle_who_reserved(call):
        return process_who_reserved(call, session, bot)


def reservation_command_handler(bot: TeleBot, session):
    add_reservation_command()
    register_reservation_command(session, bot)
    register_handle_new_reservation(session, bot)
    register_handle_back_main(session, bot)
    register_handle_select_room(session, bot)
    register_handle_back_date(session, bot)
    register_handle_hour_selection(session, bot)
    register_handle_add_time(session, bot)
    register_handle_remove_time(session, bot)
    register_handle_confirm_selection(session, bot)
    register_handle_user_reservations(session, bot)
    register_handle_future_reservations(session, bot)
    register_handle_edit_reservations(session, bot)
    register_handle_edit_specific_reservation(session, bot)
    register_handle_edit_specific_date(session, bot)
    register_handle_set_edit_date(session, bot)
    register_handle_back_specific(session, bot)
    register_handle_edit_specific_room(session, bot)
    register_handle_set_edit_room(session, bot)
    register_handle_edit_specific_hours(session, bot)
    register_handle_add_time_in_edit(session, bot)
    register_handle_remove_time_in_edit(session, bot)
    register_handle_set_edit_hours(session, bot)
    register_handle_back_edit(session, bot)
    register_handle_delete_reservations(session, bot)
    register_handle_delete_specific_reservation(session, bot)
    register_handle_back_future(session, bot)
    register_handle_past_reservations(session, bot)
    register_handle_back_user(session, bot)
    register_handle_who_reserved(session, bot)
