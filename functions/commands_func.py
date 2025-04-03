from functions.admin_commands import process_admin_commands
from functions.continuous_reservation_one import process_continuous_reservation
from functions.new_reserves import process_reservation
from functions.settings import process_settings
from functions.view_weekly_schedule import process_view_schedule

commands_dict = {
    "reservation": process_reservation,
    "continuous_reservation": process_continuous_reservation,
    "admin_commands": process_admin_commands,
    "view": process_view_schedule,
    "settings": process_settings,
}
