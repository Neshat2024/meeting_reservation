from telebot import TeleBot

from functions.view_weekly_schedule import (
    process_view_weekly_schedule,
    process_view_schedule,
    process_view_today_schedule,
    process_view_custom_schedule,
    process_select_date_custom_schedule,
)
from models.reserve_bot import get_db_session
from services.wraps import set_command, check_name_in_db, check_color


def register_view_schedule_command(bot):
    with get_db_session() as session:

        @bot.message_handler(
            func=lambda message: message.text.startswith("🗓 View Schedule")
            or message.text.startswith("🗓 مشاهده جدول رزرو ها")
        )
        @set_command("view", session)
        @check_color(session)
        @check_name_in_db(session, bot)
        def view_schedule_command(message):
            return process_view_schedule(message, session, bot)


def register_view_today_schedule(bot):
    with get_db_session() as session:

        @bot.callback_query_handler(
            func=lambda call: call.data.startswith("today-view")
        )
        def view_today_schedule(call):
            return process_view_today_schedule(call, session, bot)


def register_select_date_custom_schedule(bot):
    with get_db_session() as session:

        @bot.callback_query_handler(
            func=lambda call: call.data.startswith("select-date")
        )
        def select_date_custom_schedule(call):
            return process_select_date_custom_schedule(call, session, bot)


def register_view_custom_schedule(bot):
    with get_db_session() as session:

        @bot.callback_query_handler(func=lambda call: call.data.startswith("cu-view"))
        def view_custom_schedule(call):
            return process_view_custom_schedule(call, session, bot)


def register_back_view(bot):
    with get_db_session() as session:

        @bot.callback_query_handler(
            func=lambda call: call.data.startswith("backtoview")
        )
        def back_view(call):
            return process_view_schedule(call, session, bot)


def register_view_weekly_schedule(bot):
    with get_db_session() as session:

        @bot.callback_query_handler(
            func=lambda call: call.data.startswith("weekly-view")
        )
        def view_weekly_schedule(call):
            return process_view_weekly_schedule(call, session, bot)


def view_weekly_schedule_command_handler(bot: TeleBot):
    register_view_schedule_command(bot)
    register_view_today_schedule(bot)
    register_select_date_custom_schedule(bot)
    register_view_custom_schedule(bot)
    register_back_view(bot)
    register_view_weekly_schedule(bot)
