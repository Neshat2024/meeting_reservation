import os
import subprocess
import threading
import time
from datetime import datetime as dt

import pytz
import schedule

from services.log import add_log

tehran_tz = pytz.timezone("Asia/Tehran")


def backup_command(backup_file):
    db_name = "reservebot"
    return [
        "pg_dump",
        "-h",
        "localhost",
        "-p",
        "5432",
        "-U",
        os.getenv("POSTGRES_USER"),
        db_name,
        "-f",
        backup_file,
    ]


def backup_database(bot):
    os.environ["PGPASSWORD"] = os.getenv("POSTGRES_PASSWORD")
    backup_dir = "backups"
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    timestamp = dt.now(tehran_tz).strftime("%Y%m%d_%H%M%S")
    bot_username = bot.get_me().username
    backup_file = os.path.join(backup_dir, f"{bot_username}_{timestamp}.sql")
    command = backup_command(backup_file)
    try:
        subprocess.run(command, check=True)
        txt = f"Backup created at: {backup_file}"
        add_log(txt, backup_file)
        flag = True
    except subprocess.CalledProcessError as e:
        add_log(f"Error during backup: {e}")
        flag = False
    finally:
        if "PGPASSWORD" in os.environ:
            del os.environ["PGPASSWORD"]
        if flag:
            os.remove(backup_file)


def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)


def runnner(bot):
    add_log(f"Bot Started at {dt.now(tehran_tz).strftime('%Y-%m-%d %H:%M:%S')}")
    print("Bot is polling...")
    threading.Thread(target=run_scheduler, daemon=True).start()
    schedule.every(6).hours.do(job_func=backup_database, bot=bot)
    bot.infinity_polling()
    add_log(f"Bot Stopped at {dt.now(tehran_tz).strftime('%Y-%m-%d %H:%M:%S')}")
