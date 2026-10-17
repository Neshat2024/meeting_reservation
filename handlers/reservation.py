from telebot import TeleBot

from functions.new_reserves import (
    process_reservation,
    process_hour_selection,
    process_select_room,
    process_add_time,
    process_remove_time,
    process_back_date,
    process_confirm_selection,
    process_new_reservation,
    process_back_main,
    process_who_reserved,
)
from functions.old_reserves import (
    process_user_reservations,
    process_future_reservations,
    process_past_reservations,
    process_delete_reservations,
    process_edit_reservations,
    process_edit_specific_reservation,
    process_edit_specific_date,
    process_edit_specific_room,
    process_edit_specific_hours,
    process_set_edit_date,
    process_set_edit_room,
    process_set_edit_hours,
    process_add_time_in_edit,
    process_remove_time_in_edit,
    process_delete_specific_reservation,
    process_delete_today_reservations,
    process_edit_today_reservations,
)
from models.reserve_bot import get_db_session
from services.wraps import set_command, check_name_in_db


def register_reservation_command(bot):
    @bot.message_handler(
        func=lambda message: message.text.startswith("🚪 Reservation")
        or message.text.startswith("🚪 رزرو اتاق")
    )
    @set_command("reservation")
    @check_name_in_db(bot)
    def reservation_command(message):
        with get_db_session() as session:
            return process_reservation(message, session, bot)


def register_handle_new_reservation(bot):
    @bot.callback_query_handler(
        func=lambda call: call.data.startswith("new_reservation")
    )
    def handle_new_reservation(call):
        with get_db_session() as session:
            return process_new_reservation(call, session, bot)


def register_handle_back_main(bot):
    @bot.callback_query_handler(func=lambda call: call.data.startswith("backmain"))
    def handle_back_main(call):
        with get_db_session() as session:
            return process_back_main(call, session, bot)


def register_handle_select_room(bot):
    @bot.callback_query_handler(func=lambda call: call.data.startswith("room_"))
    def handle_select_room(call):
        with get_db_session() as session:
            return process_select_room(call, session, bot)


def register_handle_back_date(bot):
    @bot.callback_query_handler(func=lambda call: call.data.startswith("backdate"))
    def handle_back_date(call):
        with get_db_session() as session:
            return process_back_date(call, session, bot)


def register_handle_hour_selection(bot):
    @bot.callback_query_handler(func=lambda call: call.data.startswith("dt_"))
    def handle_hour_selection(call):
        with get_db_session() as session:
            return process_hour_selection(call, session, bot)


def register_handle_add_time(bot):
    @bot.callback_query_handler(func=lambda call: call.data.startswith("time_select"))
    def handle_add_time(call):
        with get_db_session() as session:
            return process_add_time(call, session, bot)


def register_handle_remove_time(bot):
    @bot.callback_query_handler(func=lambda call: call.data.startswith("time_remove"))
    def handle_remove_time(call):
        with get_db_session() as session:
            return process_remove_time(call, session, bot)


def register_handle_confirm_selection(bot):
    @bot.callback_query_handler(func=lambda call: call.data.startswith("confirm-hours"))
    def handle_confirm_selection(call):
        with get_db_session() as session:
            return process_confirm_selection(call, session, bot)


def register_handle_who_reserved(bot):
    @bot.callback_query_handler(func=lambda call: call.data.startswith("who_"))
    def handle_who_reserved(call):
        with get_db_session() as session:
            return process_who_reserved(call, session, bot)


def register_new_reservations(bot):
    register_reservation_command(bot)
    register_handle_new_reservation(bot)
    register_handle_back_main(bot)
    register_handle_select_room(bot)
    register_handle_back_date(bot)
    register_handle_hour_selection(bot)
    register_handle_add_time(bot)
    register_handle_remove_time(bot)
    register_handle_confirm_selection(bot)
    register_handle_who_reserved(bot)


def register_handle_user_reservations(bot):
    @bot.callback_query_handler(
        func=lambda call: call.data.startswith("user_reservations")
    )
    def handle_user_reservations(call):
        with get_db_session() as session:
            return process_user_reservations(call, session, bot)


def register_handle_future_reservations(bot):
    @bot.callback_query_handler(func=lambda call: call.data.startswith("future"))
    def handle_future_reservations(call):
        with get_db_session() as session:
            return process_future_reservations(call, session, bot)


def register_handle_edit_today_reservations(bot):
    @bot.callback_query_handler(
        func=lambda call: call.data.startswith("td-editreservation")
    )
    def handle_edit_today_reservations(call):
        with get_db_session() as session:
            return process_edit_today_reservations(call, session, bot)


def register_handle_edit_reservations(bot):
    @bot.callback_query_handler(
        func=lambda call: call.data.startswith("editreservation")
    )
    def handle_edit_reservations(call):
        with get_db_session() as session:
            return process_edit_reservations(call, session, bot)


def register_handle_edit_specific_reservation(bot):
    @bot.callback_query_handler(func=lambda call: call.data.startswith("e_r_"))
    def handle_edit_specific_reservation(call):
        with get_db_session() as session:
            return process_edit_specific_reservation(call, session, bot)


def register_handle_edit_specific_date(bot):
    @bot.callback_query_handler(func=lambda call: call.data.startswith("e_date_"))
    def handle_edit_specific_date(call):
        with get_db_session() as session:
            return process_edit_specific_date(call, session, bot)


def register_handle_set_edit_date(bot):
    @bot.callback_query_handler(func=lambda call: call.data.startswith("set_e_"))
    def handle_set_edit_date(call):
        with get_db_session() as session:
            return process_set_edit_date(call, session, bot)


def register_handle_back_specific(bot):
    @bot.callback_query_handler(func=lambda call: call.data.startswith("backspecific"))
    def handle_back_specific(call):
        with get_db_session() as session:
            return process_edit_specific_reservation(call, session, bot)


def register_handle_edit_specific_room(bot):
    @bot.callback_query_handler(func=lambda call: call.data.startswith("e_room_"))
    def handle_edit_specific_room(call):
        with get_db_session() as session:
            return process_edit_specific_room(call, session, bot)


def register_handle_set_edit_room(bot):
    @bot.callback_query_handler(func=lambda call: call.data.startswith("set_r_"))
    def handle_set_edit_room(call):
        with get_db_session() as session:
            return process_set_edit_room(call, session, bot)


def register_handle_edit_specific_hours(bot):
    @bot.callback_query_handler(func=lambda call: call.data.startswith("e_hours_"))
    def handle_edit_specific_hours(call):
        with get_db_session() as session:
            return process_edit_specific_hours(call, session, bot)


def register_handle_add_time_in_edit(bot):
    @bot.callback_query_handler(func=lambda call: call.data.startswith("e-t_select_"))
    def handle_add_time_in_edit(call):
        with get_db_session() as session:
            return process_add_time_in_edit(call, session, bot)


def register_handle_remove_time_in_edit(bot):
    @bot.callback_query_handler(func=lambda call: call.data.startswith("e-t_remove_"))
    def handle_remove_time_in_edit(call):
        with get_db_session() as session:
            return process_remove_time_in_edit(call, session, bot)


def register_handle_set_edit_hours(bot):
    @bot.callback_query_handler(func=lambda call: call.data.startswith("set_h_"))
    def handle_set_edit_hours(call):
        with get_db_session() as session:
            return process_set_edit_hours(call, session, bot)


def register_handle_back_edit(bot):
    @bot.callback_query_handler(func=lambda call: call.data.startswith("backedit"))
    def handle_back_edit(call):
        with get_db_session() as session:
            if call.data.endswith("_td"):
                return process_edit_today_reservations(call, session, bot)
            else:
                return process_edit_reservations(call, session, bot)


def register_handle_delete_today_reservations(bot):
    @bot.callback_query_handler(
        func=lambda call: call.data.startswith("td-deletereservation")
    )
    def handle_delete_today_reservations(call):
        with get_db_session() as session:
            return process_delete_today_reservations(call, session, bot)


def register_handle_delete_reservations(bot):
    @bot.callback_query_handler(
        func=lambda call: call.data.startswith("deletereservation")
    )
    def handle_delete_reservations(call):
        with get_db_session() as session:
            return process_delete_reservations(call, session, bot)


def register_handle_delete_specific_reservation(bot):
    @bot.callback_query_handler(func=lambda call: call.data.startswith("d_r_"))
    def handle_delete_specific_reservation(call):
        with get_db_session() as session:
            return process_delete_specific_reservation(call, session, bot)


def register_handle_back_future(bot):
    @bot.callback_query_handler(func=lambda call: call.data.startswith("backfuture"))
    def handle_back_future(call):
        with get_db_session() as session:
            return process_future_reservations(call, session, bot)


def register_handle_back_my_reservations(bot):
    @bot.callback_query_handler(
        func=lambda call: call.data.startswith("backmyreserves")
    )
    def handle_back_my_reservations(call):
        with get_db_session() as session:
            return process_user_reservations(call, session, bot)


def register_handle_past_reservations(bot):
    @bot.callback_query_handler(
        func=lambda call: call.data.startswith("past_reservations_")
    )
    def handle_past_reservations(call):
        with get_db_session() as session:
            page = int(call.data.split("_")[-1])
            return process_past_reservations([call, page], session, bot)


def register_handle_back_user(bot):
    @bot.callback_query_handler(func=lambda call: call.data.startswith("backuser"))
    def handle_back_user(call):
        with get_db_session() as session:
            return process_user_reservations(call, session, bot)


def register_old_reservations(bot):
    register_handle_user_reservations(bot)
    register_handle_future_reservations(bot)
    register_handle_edit_today_reservations(bot)
    register_handle_edit_reservations(bot)
    register_handle_edit_specific_reservation(bot)
    register_handle_edit_specific_date(bot)
    register_handle_set_edit_date(bot)
    register_handle_back_specific(bot)
    register_handle_edit_specific_room(bot)
    register_handle_set_edit_room(bot)
    register_handle_edit_specific_hours(bot)
    register_handle_add_time_in_edit(bot)
    register_handle_remove_time_in_edit(bot)
    register_handle_set_edit_hours(bot)
    register_handle_back_edit(bot)
    register_handle_delete_today_reservations(bot)
    register_handle_delete_reservations(bot)
    register_handle_delete_specific_reservation(bot)
    register_handle_back_future(bot)
    register_handle_back_my_reservations(bot)
    register_handle_past_reservations(bot)
    register_handle_back_user(bot)


def reservation_command_handler(bot: TeleBot):
    register_new_reservations(bot)
    register_old_reservations(bot)
