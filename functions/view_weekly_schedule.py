import os
from datetime import datetime as dt, timedelta

import arabic_reshaper
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
from bidi.algorithm import get_display
from matplotlib.font_manager import FontProperties
from sqlalchemy.exc import SQLAlchemyError

from functions.get_functions import get_data_in_create_image
from models.reservations import Reservations
from models.rooms import Rooms
from services.config import CONFIRMED, day_in_persian
from services.log import add_log


def process_view_weekly_schedule(message, session, bot):
    try:
        rooms = session.query(Rooms).all()
        for room in rooms:
            image_path = create_image(session, room)
            if image_path is not None:
                with open(image_path, 'rb') as photo:
                    bot.send_photo(
                        chat_id=message.chat.id,
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
        day_positions = {value: i for i, (key, value) in enumerate(day_in_persian.items())}
        # ایجاد شکل و محور
        fig, ax = plt.subplots(figsize=(12, 6))
        process_plot_for_employees([schedule, employees], day_positions, ax)
        process_ax(ax, room, employees)
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
    today = dt.now()
    today = dt(year=today.year, month=today.month, day=today.day)
    next_week = today + timedelta(days=7)
    next_week = dt(year=next_week.year, month=next_week.month, day=next_week.day, hour=23)
    return today, next_week


def get_schedule_employees(session, room, today_next_week):
    try:
        today, next_week = today_next_week
        employees, schedule = {}, {}
        reserves = session.query(Reservations).filter_by(status=CONFIRMED).all()
        for reserve in reserves:
            if reserve.room_id == room.id:
                name, date, start, end, color = get_data_in_create_image(reserve, session)
                weekday = dt.strptime(date, "%Y-%m-%d").strftime("%A")
                if name not in employees:
                    employees[name] = color
                date = dt.strptime(f"{date} {start}", "%Y-%m-%d %H:%M")
                if today <= date <= next_week and name not in schedule:
                    schedule[name] = [(day_in_persian[weekday], start, end)]
                elif today <= date <= next_week:
                    schedule[name].append((day_in_persian[weekday], start, end))
        return schedule, employees
    except SQLAlchemyError as e:
        add_log(f"SQLAlchemyError in get_schedule_employees: {e}")
    except Exception as e:
        add_log(f"Exception in get_schedule_employees: {e}")


def get_display_text(text):
    reshaped_text = arabic_reshaper.reshape(text)  # شکل‌دهی حروف
    bidi_text = get_display(reshaped_text)  # راست‌چین کردن متن
    return bidi_text


def process_plot_for_employees(schedule_employees, day_positions, ax):
    schedule, employees = schedule_employees
    for employee, blocks in schedule.items():
        for block in blocks:
            day, start, end = block
            y = day_positions[day]

            # Convert start and end times to datetime objects
            start_time = dt.strptime(start, "%H:%M")
            end_time = dt.strptime(end, "%H:%M")

            # Calculate the duration in hours
            reference_time = dt.strptime("08:00", "%H:%M")  # Reference time is 8:00 AM
            start_hours = (start_time - reference_time).seconds / 3600
            end_hours = (end_time - reference_time).seconds / 3600

            # Calculate the duration
            duration = end_hours - start_hours

            # Plot the bar
            ax.broken_barh([(start_hours, duration)], (y - 0.4, 0.8), facecolors=employees[employee])


def process_ax(ax, room, employees):
    font_path = './Fonts/Vazir.ttf'
    font_prop = FontProperties(fname=font_path)
    # تنظیم محور y با نام روزها به فارسی
    ax.set_yticks(range(len(day_in_persian)))
    y_labels = [get_display_text(value) for key, value in day_in_persian.items()]
    ax.set_yticklabels(y_labels, fontproperties=font_prop, fontsize=12)
    # تنظیم محور x با ساعت‌های روز (از ۸ تا ۲۱)
    ax.set_xlim(0, 13)  # 8 AM to 9 PM is 13 hours
    # Create x-axis ticks and labels for every 15 minutes
    x_ticks, x_labels = get_x_ticks_and_x_labels()
    ax.set_xticks(x_ticks)
    ax.set_xticklabels(x_labels, rotation=45, ha='right', fontsize=10)
    ax.set_xlabel(get_display_text('ساعت‌های روز (۸ تا ۲۱)'), fontproperties=font_prop, fontsize=14)
    # تنظیم محدوده محور y
    ax.set_ylim(-0.5, len(day_in_persian) - 0.5)
    # تنظیم عنوان نمودار به فارسی
    ax.set_title(get_display_text(f'{room.name} نمودار اتاق'), fontproperties=font_prop, fontsize=16)
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
    for hour in range(8, 21):  # From 8 AM to 9 PM
        for minute in [0, 15, 30, 45]:  # Every 15 minutes
            x_ticks.append((hour - 8) + (minute / 60))  # Convert to hours since 8 AM
            x_labels.append(f"{hour}:{minute:02d}")  # Format as "HH:MM"
    return x_ticks, x_labels
