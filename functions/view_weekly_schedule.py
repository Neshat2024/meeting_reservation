import os
from datetime import datetime as dt, timedelta

import arabic_reshaper
import jdatetime
import matplotlib
import matplotlib.patches as mpatches
from bidi.algorithm import get_display
from matplotlib.font_manager import FontProperties
from sqlalchemy.exc import SQLAlchemyError
from telebot import types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton as btn

from models.users import Users

matplotlib.use('Agg')  # Set the backend to 'Agg' (non-interactive)
import matplotlib.pyplot as plt
from functions.get_functions import get_data_in_create_image, create_date_buttons
from models.reservations import Reservations
from models.rooms import Rooms
from services.config import CONFIRMED, day_in_persian, change_command_to_none
from services.log import add_log
import pytz

tehran_tz = pytz.timezone("Asia/Tehran")


def process_view_schedule(call_message, session, bot):
    txt = "🗓 Choose Your Schedule:"
    key = InlineKeyboardMarkup()
    key.add(btn(text="📅 Today", callback_data="today-view"))
    key.add(btn(text="📆 Custom Day", callback_data="select-date"))
    key.add(btn(text="🗓 Weekly", callback_data="weekly-view"))
    if isinstance(call_message, types.Message):
        message = call_message
        chat_id = str(message.chat.id)
        bot.send_message(chat_id, txt, reply_markup=key)
    elif isinstance(call_message, types.CallbackQuery):
        chat_id = str(call_message.message.chat.id)
        msg_id = call_message.message.id
        bot.edit_message_text(chat_id=chat_id, message_id=msg_id, text=txt, reply_markup=key)
    user = session.query(Users).filter_by(chat_id=chat_id).first()
    change_command_to_none(user, session)


def process_view_today_schedule(call, session, bot):
    try:
        rooms = session.query(Rooms).all()
        bot.delete_message(call.message.chat.id, call.message.id)
        for room in rooms:
            image_path = create_image_for_today(session, room)
            if image_path is not None:
                with open(image_path, 'rb') as photo:
                    bot.send_photo(
                        chat_id=call.message.chat.id,
                        photo=photo,
                        caption=f"📊 Today's Schedule for {room.name}"  # Caption for the photo
                    )
                os.remove(image_path)
    except SQLAlchemyError as e:
        add_log(f"SQLAlchemyError in process_view_today_schedule: {e}")
    except Exception as e:
        add_log(f"Exception in process_view_today_schedule: {e}")


def create_image_for_today(session, room):
    try:
        today = dt.now(tehran_tz)
        today = dt(year=today.year, month=today.month, day=today.day)
        tomorrow = today + timedelta(days=1)
        schedule, employees = get_schedule_employees(session, room, [today, tomorrow])
        day_positions, y_labels = get_day_positions_and_labels_for_today(today)
        fig, ax = plt.subplots(figsize=(18, 4))
        process_plot_for_employees([schedule, employees, day_positions], ax, True)
        process_ax(ax, room, employees, y_labels)
        plt.tight_layout()
        plt.savefig('today_schedule_timeline_fa.png', dpi=300, bbox_inches='tight')
        plt.close()
        return "today_schedule_timeline_fa.png"
    except SQLAlchemyError as e:
        add_log(f"SQLAlchemyError in create_image_for_today: {e}")
    except Exception as e:
        add_log(f"Exception in create_image_for_today: {e}")


def get_day_positions_and_labels_for_today(today):
    dates = [today]
    day_positions = {}
    y_labels = []
    for i, date in enumerate(dates):
        weekday = date.strftime("%A")
        persian_day = day_in_persian[weekday]
        formatted_date = date.strftime("%Y-%m-%d")
        day_positions[formatted_date] = i
        y_labels.append(f"{get_display_text(persian_day)} {gregorian_to_jalali(formatted_date)}")
    return day_positions, y_labels


def process_select_date_custom_schedule(call, session, bot):
    chat_id = call.message.chat.id
    msg_id = call.message.id
    txt = '📅 Choose a Date for View Meetings (Available up to Next Week):'
    key = create_date_buttons('cu-view')
    key.add(btn(text="⬅️ Back", callback_data="backtoview"))
    bot.edit_message_text(chat_id=chat_id, message_id=msg_id, text=txt, reply_markup=key)


def process_view_custom_schedule(call, session, bot):
    try:
        custom_date = call.data.split("_")[1]
        bot.delete_message(call.message.chat.id, call.message.id)
        rooms = session.query(Rooms).all()
        for room in rooms:
            image_path = create_image_for_custom_day(session, room, custom_date)
            if image_path is not None:
                with open(image_path, 'rb') as photo:
                    bot.send_photo(
                        chat_id=call.message.chat.id,
                        photo=photo,
                        caption=f"📊 Schedule for {custom_date} in {room.name}"  # Caption for the photo
                    )
                os.remove(image_path)
    except SQLAlchemyError as e:
        add_log(f"SQLAlchemyError in process_view_custom_day_schedule: {e}")
    except Exception as e:
        add_log(f"Exception in process_view_custom_day_schedule: {e}")


def create_image_for_custom_day(session, room, custom_date):
    try:
        custom_date = dt.strptime(custom_date, "%Y-%m-%d")
        custom_date = tehran_tz.localize(custom_date)
        next_day = custom_date + timedelta(days=1)
        schedule, employees = get_schedule_employees(session, room, [custom_date, next_day])
        day_positions, y_labels = get_day_positions_and_labels_for_custom_day(custom_date)
        fig, ax = plt.subplots(figsize=(18, 4))
        process_plot_for_employees([schedule, employees, day_positions], ax, True)
        process_ax(ax, room, employees, y_labels)
        plt.tight_layout()
        plt.savefig('custom_day_schedule_timeline_fa.png', dpi=300, bbox_inches='tight')
        plt.close()
        return "custom_day_schedule_timeline_fa.png"
    except SQLAlchemyError as e:
        add_log(f"SQLAlchemyError in create_image_for_custom_day: {e}")
    except Exception as e:
        add_log(f"Exception in create_image_for_custom_day: {e}")


def get_day_positions_and_labels_for_custom_day(custom_date):
    dates = [custom_date]
    day_positions = {}
    y_labels = []
    for i, date in enumerate(dates):
        weekday = date.strftime("%A")
        persian_day = day_in_persian[weekday]
        formatted_date = date.strftime("%Y-%m-%d")
        day_positions[formatted_date] = i
        y_labels.append(f"{get_display_text(persian_day)} {gregorian_to_jalali(formatted_date)}")
    return day_positions, y_labels


def process_view_weekly_schedule(call, session, bot):
    try:
        rooms = session.query(Rooms).all()
        bot.delete_message(call.message.chat.id, call.message.id)
        for room in rooms:
            image_path = create_image(session, room)
            if image_path is not None:
                with open(image_path, 'rb') as photo:
                    bot.send_photo(
                        chat_id=call.message.chat.id,
                        photo=photo,
                        caption=f"📊 Chart {room.name}"  # Caption for the photo
                    )
                os.remove(image_path)
    except SQLAlchemyError as e:
        add_log(f"SQLAlchemyError in process_view_weekly_schedule: {e}")
    except Exception as e:
        add_log(f"Exception in process_view_weekly_schedule: {e}")


def create_image(session, room):
    try:
        today, next_week = main_data_in_create_image()
        schedule, employees = get_schedule_employees(session, room, [today, next_week])
        # تخصیص هر روز به یک موقعیت در محور y
        day_positions, y_labels = get_day_positions_and_labels(today)
        # ایجاد شکل و محور با اندازه بزرگ‌تر
        fig, ax = plt.subplots(figsize=(18, 10))  # Increase the figure size (width, height)
        process_plot_for_employees([schedule, employees, day_positions], ax)
        process_ax(ax, room, employees, y_labels)
        # بهبود چیدمان نمودار
        plt.tight_layout()
        # ذخیره نمودار به صورت تصویر
        plt.savefig('weekly_schedule_timeline_fa.png', dpi=300, bbox_inches='tight')
        plt.close()
        return "weekly_schedule_timeline_fa.png"
    except SQLAlchemyError as e:
        add_log(f"SQLAlchemyError in create_image: {e}")
    except Exception as e:
        add_log(f"Exception in create_image: {e}")


def main_data_in_create_image():
    today = dt.now(tehran_tz)
    today = dt(year=today.year, month=today.month, day=today.day)
    next_week = today + timedelta(days=7)
    next_week = dt(year=next_week.year, month=next_week.month, day=next_week.day, hour=23)
    return today, next_week


def get_day_positions_and_labels(today):
    dates = [today + timedelta(days=i) for i in range(8)]
    dates.reverse()
    day_positions = {}
    y_labels = []
    for i, date in enumerate(dates):
        weekday = date.strftime("%A")
        persian_day = day_in_persian[weekday]
        formatted_date = date.strftime("%Y-%m-%d")
        day_positions[formatted_date] = i
        y_labels.append(f"{get_display_text(persian_day)} {gregorian_to_jalali(formatted_date)}")
    return day_positions, y_labels


def get_schedule_employees(session, room, today_next_week):
    try:
        today, end_date = today_next_week
        employees, schedule = {}, {}
        reserves = session.query(Reservations).filter_by(status=CONFIRMED).all()
        for reserve in reserves:
            if str(reserve.room_id) == str(room.id):
                name, date, start, end, color = get_data_in_create_image(reserve, session)
                weekday = dt.strptime(date, "%Y-%m-%d").strftime("%A")
                if name not in employees:
                    employees[name] = color
                date_obj = dt.strptime(f"{date} {start}", "%Y-%m-%d %H:%M")
                date_obj = tehran_tz.localize(date_obj)
                if today <= date_obj <= end_date:
                    persian_day = day_in_persian[weekday]
                    if name not in schedule:
                        schedule[name] = [(persian_day, start, end, date)]
                    else:
                        schedule[name].append((persian_day, start, end, date))
        return schedule, employees
    except SQLAlchemyError as e:
        add_log(f"SQLAlchemyError in get_schedule_employees: {e}")
    except Exception as e:
        add_log(f"Exception in get_schedule_employees: {e}")


def get_display_text(text):
    reshaped_text = arabic_reshaper.reshape(text)  # شکل‌دهی حروف
    bidi_text = get_display(reshaped_text)  # راست‌چین کردن متن
    return bidi_text


def process_plot_for_employees(schedule_employees_day, ax, is_single_day=False):
    schedule, employees, day_positions = schedule_employees_day
    bar_height = 0.4 if is_single_day else 0.8  # Reduce height for single-day schedules
    for employee, blocks in schedule.items():
        for block in blocks:
            day, start, end, date = block
            y = day_positions[date]  # Use the date as the key to get the correct y-position
            # Convert start and end times to datetime objects
            start_time = dt.strptime(start, "%H:%M")
            start_time = tehran_tz.localize(start_time)
            end_time = dt.strptime(end, "%H:%M")
            end_time = tehran_tz.localize(end_time)
            # Calculate the duration in hours
            reference_time = dt.strptime("08:00", "%H:%M")  # Reference time is 8:00 AM
            reference_time = tehran_tz.localize(reference_time)
            start_hours = (start_time - reference_time).seconds / 3600
            end_hours = (end_time - reference_time).seconds / 3600
            # Calculate the duration
            duration = end_hours - start_hours
            # Plot the bar with adjusted height
            ax.broken_barh([(start_hours, duration)], (y - bar_height / 2, bar_height), facecolors=employees[employee])


def process_ax(ax, room, employees, y_labels):
    font_path = './Fonts/Vazir.ttf'
    font_prop = FontProperties(fname=font_path)
    # تنظیم محور y با نام روزها و تاریخ به فارسی
    ax.set_yticks(range(len(y_labels)))
    ax.set_yticklabels(y_labels, fontproperties=font_prop, fontsize=12)
    # تنظیم محور x با ساعت‌های روز (از ۸ تا ۲۱)
    ax.set_xlim(0, 13)  # 8 AM to 9 PM is 13 hours
    # Create x-axis ticks and labels for every 15 minutes
    x_ticks, x_labels = get_x_ticks_and_x_labels()
    ax.set_xticks(x_ticks)
    ax.set_xticklabels(x_labels, rotation=45, ha='right', fontsize=10)
    ax.set_xlabel(get_display_text('ساعت‌های روز (۸ تا ۲۱)'), fontproperties=font_prop, fontsize=14)
    # تنظیم محدوده محور y
    ax.set_ylim(-0.5, len(y_labels) - 0.5)
    # تنظیم عنوان نمودار به فارسی
    ax.set_title(get_display_text(room.name), fontproperties=font_prop, fontsize=16)
    # افزودن راهنما (Legend) برای رنگ‌های کارمندان
    legend_patches = [mpatches.Patch(color=color, label=get_display_text(employee)) for employee, color in
                      employees.items()]
    ax.legend(handles=legend_patches, title=get_display_text('کارمندان'), bbox_to_anchor=(1.05, 1), loc='upper left',
              prop=font_prop)
    # افزودن خطوط شبکه برای محور x
    ax.grid(True, axis='x', linestyle='--', alpha=0.5)
    # حذف خطوط اطراف نمودار
    for spine in ['top', 'right', 'left', 'bottom']:
        ax.spines[spine].set_visible(False)


def get_x_ticks_and_x_labels():
    x_ticks = []
    x_labels = []
    for hour in range(8, 22):  # From 8 AM to 9 PM
        for minute in [0, 15, 30, 45]:  # Every 15 minutes
            x_ticks.append((hour - 8) + (minute / 60))  # Convert to hours since 8 AM
            x_labels.append(f"{hour}:{minute:02d}")  # Format as "HH:MM"
            if x_labels[-1] == '21:00':
                break
    return x_ticks, x_labels


def gregorian_to_jalali(date_str):
    gregorian_date = dt.strptime(date_str, '%Y-%m-%d')
    jalali_date = jdatetime.date.fromgregorian(date=gregorian_date)
    jalali_date_str = jalali_date.strftime('%Y/%m/%d')
    return jalali_date_str
