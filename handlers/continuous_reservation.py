from telebot import types

from functions.continuous_reservation_one import (
    process_continuous_reservation,
    process_cr_weekday,
    process_cr_hour_selection,
    process_confirm_cr_hour,
    process_cr_back_hours,
    process_room_selection,
    process_show_rooms,
    process_cr_week_selection,
    process_confirm_cr_week,
    process_cr_back_weeks,
)
from functions.continuous_reservation_two import (
    process_cr_edit_weeks,
    process_cr_back_final_week,
    process_cr_edit_week_selection, process_cr_confirm_edited_weeks, process_cr_cancel_reserve,
    process_cr_reserve_weeks,
)
from services.config import commands
from services.wraps import set_command, check_name_in_db


def add_continuous_reservation_command():
    commands.append(
        types.BotCommand(
            command="/continuous_reservation",
            description="🔄 Continuous Reserve Meeting Room",
        )
    )


def register_continuous_reservation_command(session, bot):
    @bot.message_handler(commands=["continuous_reservation"])
    @set_command("continuous_reservation", session)
    @check_name_in_db(session, bot)
    def continuous_reservation_command(message):
        return process_continuous_reservation(message, session, bot)


def register_handle_cr_weekday(session, bot):
    @bot.callback_query_handler(func=lambda call: call.data.startswith("cr_weekday_"))
    def handle_cr_weekday(call):
        return process_cr_weekday(call, session, bot)


def register_handle_cr_back_weekday(session, bot):
    @bot.callback_query_handler(
        func=lambda call: call.data.startswith("cr_back_weekday")
    )
    def handle_cr_back_weekday(call):
        return process_continuous_reservation(call, session, bot)


def register_handle_cr_hour_selection(session, bot):
    @bot.callback_query_handler(func=lambda call: call.data.startswith("cr_hr_"))
    def handle_cr_hour_selection(call):
        return process_cr_hour_selection(call, session, bot)


def register_handle_confirm_cr_hour(session, bot):
    @bot.callback_query_handler(
        func=lambda call: call.data.startswith("cr_confirm_hour")
    )
    def handle_confirm_cr_hour(call):
        return process_confirm_cr_hour(call, session, bot)


def register_handle_cr_back_hours(session, bot):
    @bot.callback_query_handler(func=lambda call: call.data.startswith("cr_back_hours"))
    def handle_cr_back_hours(call):
        return process_cr_back_hours(call, session, bot)


def register_handle_room_selection(session, bot):
    @bot.callback_query_handler(func=lambda call: call.data.startswith("cr_room_"))
    def handle_room_selection(call):
        return process_room_selection(call, session, bot)


def register_handle_cr_back_rooms(session, bot):
    @bot.callback_query_handler(func=lambda call: call.data.startswith("cr_back_rooms"))
    def handle_cr_back_rooms(call):
        return process_show_rooms(call, session, bot)


def register_handle_cr_week_selection(session, bot):
    @bot.callback_query_handler(func=lambda call: call.data.startswith("cr_week_"))
    def handle_cr_week_selection(call):
        return process_cr_week_selection(call, session, bot)


def register_handle_confirm_cr_week(session, bot):
    @bot.callback_query_handler(
        func=lambda call: call.data.startswith("cr_confirm_weeks")
    )
    def handle_confirm_cr_week(call):
        return process_confirm_cr_week(call, session, bot)


def register_handle_cr_back_weeks(session, bot):
    @bot.callback_query_handler(func=lambda call: call.data.startswith("cr_back_weeks"))
    def handle_cr_back_weeks(call):
        return process_cr_back_weeks(call, session, bot)


def part_one(bot, session):
    register_continuous_reservation_command(session, bot)
    register_handle_cr_weekday(session, bot)
    register_handle_cr_back_weekday(session, bot)
    register_handle_cr_hour_selection(session, bot)
    register_handle_confirm_cr_hour(session, bot)
    register_handle_cr_back_hours(session, bot)
    register_handle_room_selection(session, bot)
    register_handle_cr_back_rooms(session, bot)
    register_handle_cr_week_selection(session, bot)
    register_handle_confirm_cr_week(session, bot)
    register_handle_cr_back_weeks(session, bot)


def register_handle_cr_edit_weeks(session, bot):
    @bot.callback_query_handler(func=lambda call: call.data.startswith("edit-weeks"))
    def handle_cr_edit_weeks(call):
        return process_cr_edit_weeks(call, session, bot)


def register_handle_cr_back_final_week(session, bot):
    @bot.callback_query_handler(
        func=lambda call: call.data.startswith("cr_back_final_week")
    )
    def handle_cr_back_final_week(call):
        return process_cr_back_final_week(call, session, bot)


def register_handle_cr_edit_week_selection(session, bot):
    @bot.callback_query_handler(func=lambda call: call.data.startswith("cr_ew_"))
    def handle_cr_edit_week_selection(call):
        return process_cr_edit_week_selection(call, session, bot)


def register_handle_cr_confirm_edited_weeks(session, bot):
    @bot.callback_query_handler(func=lambda call: call.data.startswith("cr_confirm_edit_week"))
    def handle_cr_confirm_edited_weeks(call):
        return process_cr_confirm_edited_weeks(call, session, bot)


def register_handle_cr_cancel_reserve(session, bot):
    @bot.callback_query_handler(func=lambda call: call.data.startswith("cancel-reserve"))
    def handle_cr_cancel_reserve(call):
        return process_cr_cancel_reserve(call, session, bot)


def register_handle_cr_reserve_weeks(session, bot):
    @bot.callback_query_handler(func=lambda call: call.data.startswith("reserve-weeks"))
    def handle_cr_reserve_weeks(call):
        return process_cr_reserve_weeks(call, session, bot)


def part_two(bot, session):
    register_handle_cr_edit_weeks(session, bot)
    register_handle_cr_back_final_week(session, bot)
    register_handle_cr_edit_week_selection(session, bot)
    register_handle_cr_confirm_edited_weeks(session, bot)
    register_handle_cr_cancel_reserve(session, bot)
    register_handle_cr_reserve_weeks(session, bot)


def continuous_reservation_command_handler(bot, session):
    add_continuous_reservation_command()
    part_one(bot, session)
    part_two(bot, session)
