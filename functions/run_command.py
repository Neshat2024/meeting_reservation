from functions.commands_func import commands_dict
from services.config import get_user
from services.log import add_log


def run_user_command(message, session, bot):
    try:
        user = get_user(message, session)
        if user.command:
            return commands_dict[user.command](message, session, bot)
    except Exception as e:
        add_log(f"Exception in run_user_command: {e}")
