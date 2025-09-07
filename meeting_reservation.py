import sys


def main():
    if len(sys.argv) < 2:
        print("Usage: python meeting_reservation.py <instance_name>")
        sys.exit(1)

    # Initialize settings FIRST
    from settings import settings

    settings.initialize(f".env.{sys.argv[1]}")

    # Now import other modules
    import telebot
    from handlers.admin_commands import admin_commands_handler
    from handlers.continuous_reservation import continuous_reservation_command_handler
    from handlers.main import start_help_handler
    from handlers.reservation import reservation_command_handler
    from handlers.set_color import set_color_for_all_users
    from handlers.setting_command import settings_command_handler
    from handlers.view_weekly_schedule import view_weekly_schedule_command_handler
    from models.reserve_bot import init_db
    from services.bot_runner import runner, MyBot
    from settings import commands

    # Initialize bot
    bot = MyBot(settings.TOKEN_RESERVE)

    # Initialize Database
    init_db(bot)

    # Register handlers
    set_color_for_all_users()
    reservation_command_handler(bot)
    admin_commands_handler(bot)
    view_weekly_schedule_command_handler(bot)
    settings_command_handler(bot)
    start_help_handler(bot)

    if settings.IS_CONTINUOUS_RESERVE_AVAILABLE.lower() == "true":
        continuous_reservation_command_handler(bot)

    # Configure proxy
    if settings.PROXY_HOST and settings.PROXY_PORT:
        proxy_url = f"socks5h://{settings.PROXY_HOST}:{settings.PROXY_PORT}"
        telebot.apihelper.proxy = {"http": proxy_url, "https": proxy_url}

    # Set Bot Menu Command
    bot.set_my_commands(commands)

    # Run Bot
    runner(bot)


if __name__ == "__main__":
    main()
