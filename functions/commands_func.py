from functions.manage_room import process_manage_room
from functions.new_reserves import process_reservation
from functions.view_weekly_schedule import process_view_weekly_schedule

commands_dict = {
    "reservation": process_reservation,
    "manage_rooms": process_manage_room,
    "view": process_view_weekly_schedule,
}
