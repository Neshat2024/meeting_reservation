from telebot import types

CANCEL, SELECT, REMOVE = "/cancel", "select", "remove"
BACK_DATE, BACK_MAIN, BACK_USER = "backdate", "backmain", "backuser"
BACK_ROOM = "backroom"
FIRST, SECOND, CONFIRMED = "first", "second", "confirmed"
DAYS_FOR_HEADERS = ["SA", "SU", "MO", "TU", "WE", "TH", "FR"]
DAYS_FOR_HEADERS_FA = ["ش", "۱ش", "۲ش", "۳ش", "۴ش", "۵ش", "ج"]
day_in_persian = {
    "Friday": "جمعه",
    "Thursday": "پنج‌شنبه",
    "Wednesday": "چهارشنبه",
    "Tuesday": "سه‌شنبه",
    "Monday": "دوشنبه",
    "Sunday": "یکشنبه",
    "Saturday": "شنبه",
}
WEEKDAYS_LIST = [
    ["شنبه", "Saturday"],
    ["یکشنبه", "Sunday"],
    ["دوشنبه", "Monday"],
    ["سه‌شنبه", "Tuesday"],
    ["چهارشنبه", "Wednesday"],
    ["پنج‌شنبه", "Thursday"],
    ["جمعه", "Friday"],
]
weekday_map = {
    "monday": 0,
    "tuesday": 1,
    "wednesday": 2,
    "thursday": 3,
    "friday": 4,
    "saturday": 5,
    "sunday": 6,
}
ONE, TWO, THREE = 1, 2, 3
CHECKOUT = "checkout"
FARSI, ENGLISH = "fa", "en"

commands = [types.BotCommand(command="/start", description="Start menu")]
