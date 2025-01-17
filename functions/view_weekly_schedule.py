import os
from datetime import datetime as dt, timedelta
import matplotlib
matplotlib.use('Agg')  # Set the backend to 'Agg'
import matplotlib.pyplot as plt
from matplotlib import font_manager
from functions.get_functions import get_room_name
from models.reservations import Reservations
from models.users import Users
from services.config import CONFIRMED

def process_view_weekly_schedule(message, session, bot):
    image_path = create_image(session)
    with open(image_path, 'rb') as photo:
        bot.send_photo(
            chat_id=message.chat.id,
            photo=photo,
            caption="Here are the reservations up to next week!"  # Caption for the photo
        )
    os.remove(image_path)

def create_image(session):
    try:
        # Replace this path with the path to a Persian font on your system
        font_path = "./Fonts/Pinar-FD-SemiBold.ttf"  # Example: "B Nazanin.ttf"
        persian_font = font_manager.FontProperties(fname=font_path)
    except Exception as e:
        print(f"Error loading font: {e}")
        persian_font = None  # Fallback to default font if the specified font is not found

    # Fetch reservations from the database
    reserves = session.query(Reservations).filter_by(status=CONFIRMED).all()
    reserves_list = []
    today = dt.now()
    today = dt(year=today.year, month=today.month, day=today.day)
    next_week = today + timedelta(days=7)
    next_week = dt(year=next_week.year, month=next_week.month, day=next_week.day, hour=23)
    for reserve in reserves:
        time = f"{reserve.date} {reserve.start_time}"
        date = dt.strptime(time, "%Y-%m-%d %H:%M")
        if today <= date <= next_week:
            reserves_list.append(date)
    # Prepare data for the table
    reserves_list = sorted(reserves_list)
    data = []
    columns = ["Name", "Date", "Start Time", "End Time", "Room"]

    # Parse and sort reservations by date and start_time
    parsed_reserves = []
    for reserve in reserves:
        room = get_room_name(reserve.room_id, session)
        uname = session.query(Users).filter_by(id=reserve.user_id).first().name

        # Parse date and time strings into datetime objects for sorting
        date_obj = dt.strptime(reserve.date, "%Y-%m-%d")  # Parse date (e.g., "2025-17-01")
        start_time_obj = dt.strptime(reserve.start_time, "%H:%M")  # Parse start time (e.g., "11:45")
        end_time = reserve.end_time if reserve.end_time else ""  # Handle None values

        parsed_reserves.append({
            "name": uname,
            "date_obj": date_obj,
            "date_str": date_obj.strftime("%Y-%m-%d"),  # Format date for display
            "start_time_obj": start_time_obj,
            "start_time_str": start_time_obj.strftime("%H:%M"),  # Format start time for display
            "end_time": end_time,
            "room": room
        })

    # Sort reservations by date and start time
    parsed_reserves.sort(key=lambda x: (x["date_obj"], x["start_time_obj"]))

    # Prepare table data
    for reserve in parsed_reserves:
        data.append([
            reserve["name"],
            reserve["date_str"],  # Formatted date
            reserve["start_time_str"],  # Formatted start time
            reserve["end_time"],  # End time (already handled for None values)
            reserve["room"]
        ])

    # Create a figure and axis
    fig, ax = plt.subplots(figsize=(19.20, 10.80))  # 1920x1080 resolution (in inches at 100 DPI)
    fig.patch.set_facecolor('white')
    ax.set_facecolor('white')
    ax.axis('off')  # Hide axes

    # Create the table
    table = ax.table(
        cellText=data,
        colLabels=columns,
        loc='center',
        cellLoc='center',
        colColours=['#f2f2f2'] * len(columns),  # Light gray background for header
        cellColours=[['#ffffff'] * len(columns) for _ in range(len(data))]  # White background for cells
    )

    # Adjust table style
    table.auto_set_font_size(False)
    table.set_fontsize(40)  # Set font size for table cells
    table.scale(1, 3)  # Scale cell sizes

    # Set font for Persian text
    if persian_font:
        for key, cell in table.get_celld().items():
            cell_text = cell.get_text()
            cell_text.set_fontproperties(persian_font)  # Apply Persian font to text

    # Save the image to a temporary file
    image_path = "reserves_table.png"
    plt.savefig(image_path, dpi=100, bbox_inches='tight')
    plt.close()  # Close the plot to free up memory

    return image_path