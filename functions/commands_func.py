from functions.admin_commands import process_admin_commands
from functions.new_reserves import process_reservation
from functions.view_weekly_schedule import process_view_schedule

commands_dict = {
    "reservation": process_reservation,
    "admin_commands": process_admin_commands,
    "view": process_view_schedule
}
