import os

from dotenv import load_dotenv
from telebot import TeleBot

from handlers.manage_room import manage_room_command_handler
from handlers.main import start_help_handler
from handlers.reservation import reservation_command_handler
from handlers.view_weekly_schedule import view_weekly_schedule_command_handler
from models.reserve_bot import init_db, SessionLocal
from services.bot_runner import runnner
from services.config import commands

load_dotenv()

bot = TeleBot(os.getenv("TOKEN_RESERVE"))
session = SessionLocal()

# Initialize Database
init_db(bot)

# Register handlers
reservation_command_handler(bot, session)
manage_room_command_handler(bot, session)
view_weekly_schedule_command_handler(bot, session)
start_help_handler(bot, session)

# Set Bot Menu Command
bot.set_my_commands(commands)

# Run Bot
runnner(bot)
