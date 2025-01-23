from enum import Enum


class BotText(Enum):
    RESERVATION_TEXT = {
        "en": "Reserve a room anytime with «🚪 New Reservation» or manage reservations via «📝 My Reservations»",
        "fa": "شما می توانید یک اتاق را برای هر زمانی که تمایل داشتید، با دکمه «🚪 رزرو جدید» رزرو کنید و یا از طریق دکمه «👀 رزرو های من» رزرو های خود را مدیریت کنید."
    }
    NEW_RESERVATION_BUTTON = {
        "en": "🚪 New Reservation",
        "fa": "🚪 رزرو جدید"
    }
    MY_RESERVATIONS_BUTTON = {
        "en": "👀 My Reservations",
        "fa": "👀 رزرو های من"
    }
    LANGUAGE_TEXT = {
        "en": "🗣 Language: English\nIf you'd like to change the bot's language tap on the button below.",
        "fa": " 🗣 زبان: فارسی\nاگر تمایل به تغییر زبان دارید روی دکمه زیر کلیک کنید."
    }
    PERSIAN_CALLBACK = {
        "en": "🗣 The bot's language changed to English for you.",
        "fa": "🗣 زبان بات برای شما به فارسی تغییر کرد."
    }
    CHOOSE_DATE_TEXT = {
        "en": "📅 Choose a Date for Your Meeting (Available up to Next Week)",
        "fa": "📅 تاریخ جلسه خود را انتخاب کنید. (تا هفته آینده)"
    }
    ROOM_SELECTION_TEXT = {
        "en": "📅 Date: {date} ({weekday})\n❓ Room:",
        "fa": "📅 تاریخ: {date} ({weekday})\n❓ اتاق:"
    }
    HOUR_SELECTION_TEXT = {
        "en": "📅 Date: {date} ({weekday})\n🚪 Room: {room_name}\n❓ From:",
        "fa": "📅 تاریخ: {date} ({weekday})\n🚪 اتاق: {room_name}\n❓ از:"
    }
    ADD_TIME_FIRST_STATUS = {
        "en": "📅 Date: {date} ({weekday})\n🚪 Room: {room_name}\n▶️ From: {start_time}\n◀️ To: {end_time}\n(You can change the end time)",
        "fa": "📅 تاریخ: {date} ({weekday})\n🚪 اتاق: {room_name}\n▶️ از: {start_time}\n◀️ تا: {end_time}\n(می توانید زمان پایان را تغییر دهید)"
    }
    ADD_TIME_SECOND_STATUS = {
        "en": "📅 Date: {date} ({weekday})\n🚪 Room: {room_name}\n▶️ From: {start_time}\n◀️ To: {end_time}",
        "fa": "📅 تاریخ: {date} ({weekday})\n🚪 اتاق: {room_name}\n▶️ از: {start_time}\n◀️ تا: {end_time}"
    }
    ADD_TIME_DEFAULT = {
        "en": "📅 Date: {date} ({weekday})\n🚪 Room: {room_name}\n❓ From:",
        "fa": "📅 تاریخ: {date} ({weekday})\n🚪 اتاق: {room_name}\n❓ از:"
    }
    CONFIRM_RESERVATION_TEXT = {
        "en": "Your Reservation submitted ✅\n\n📅 Date: {date} ({weekday})\n🚪 Room: {room_name}\n▶️ From: {start_time}\n◀️ To: {end_time}",
        "fa": "رزرو شما ثبت شد ✅\n\n📅 تاریخ: {date} ({weekday})\n🚪 اتاق: {room_name}\n▶️ از: {start_time}\n◀️ تا: {end_time}"
    }
    INVALID_TIME_ALERT = {
        "en": "The end time can't be before the start time 🗿",
        "fa": "زمان پایان نمی ‌تواند قبل از زمان شروع باشد 🗿"
    }
    INCOMPLETE_HOURS_ALERT = {
        "en": "You can't confirm before completing the hours ⛔️",
        "fa": "قبل از تکمیل ساعات نمی ‌توانید تأیید کنید ⛔️"
    }
    BACK_BUTTON = {
        "en": "⬅️ Back",
        "fa": "⬅️ بازگشت"
    }
    CONFIRM_BUTTON = {
        "en": "🟢 Confirm 🟢",
        "fa": "🟢 تأیید 🟢"
    }
    INVALID_RESERVED_TIMES = {
        "en": "Reserved times can't be selected ⛔️",
        "fa": "زمان های از پیش رزرو شده نمی توانند در بازه انتخابی شما باشند ⛔️"
    }
    INVALID_DURATION = {
        "en": "The duration must be less than 4 hours ⛔️",
        "fa": "طول بازه زمانی جلسه نباید بیش از 4 ساعت باشد ⛔️"
    }
    INVALID_PAST_TIMES = {
        "en": "Only future times can be reserved ⛔️",
        "fa": "امکان رزرو زمان های گذشته وجود ندارد ⛔️"
    }
    WHO_RESERVED = {
        "en": "❗️ User ({name}) has been reserved this hour.",
        "fa": "❗️ کاربری به نام ({name}) این زمان را رزرو کرده است."
    }
    USER_RESERVATIONS_TEXT = {
        "en": "View upcoming reservations with «🗓 Future» or past reservations using «🔍 Past»",
        "fa": "برای مشاهده رزرو های آینده از «🗓 آینده» و برای رزرو های گذشته از «🔍 گذشته» استفاده کنید."
    }
    NO_RESERVATIONS_TEXT = {
        "en": "You haven’t made any Reservations yet 🙁",
        "fa": "شما هنوز هیچ رزروی انجام نداده ‌اید 🙁"
    }
    FUTURE_RESERVATIONS_HEADER = {
        "en": "🗓 Your Future Reservations are:\n\n",
        "fa": "🗓 رزرو های آینده شما:\n\n"
    }
    NO_FUTURE_RESERVATIONS_TEXT = {
        "en": "You don't have any Future Reservation 🤲🏻",
        "fa": "شما هیچ رزروی برای آینده ندارید 🤲🏻"
    }
    EDIT_RESERVATIONS_TEXT = {
        "en": "📝 Choose the Reservation you'd like to edit:",
        "fa": "📝 رزروی که می ‌خواهید ویرایش کنید را انتخاب کنید:"
    }
    EDIT_DATE_TEXT = {
        "en": "🚪 Room: {room_name}\n▶️ From: {start_time}\n◀️ To: {end_time}\n❓ Date:",
        "fa": "🚪 اتاق: {room_name}\n▶️ از: {start_time}\n◀️ تا: {end_time}\n❓ تاریخ:"
    }
    EDIT_ROOM_TEXT = {
        "en": "📅 Date: {date} ({weekday})\n▶️ From: {start_time}\n◀️ To: {end_time}\n❓ Room:",
        "fa": "📅 تاریخ: {date} ({weekday})\n▶️ از: {start_time}\n◀️ تا: {end_time}\n❓ اتاق:"
    }
    EDIT_HOURS_TEXT = {
        "en": "📅 Date: {date} ({weekday})\n🚪 Room: {room_name}\n❓ From:",
        "fa": "📅 تاریخ: {date} ({weekday})\n🚪 اتاق: {room_name}\n❓ از:"
    }
    DELETE_RESERVATIONS_TEXT = {
        "en": "🗑 Choose the Reservation you'd like to delete:",
        "fa": "🗑 رزروی که می ‌خواهید حذف کنید را انتخاب کنید:"
    }
    DELETE_SUCCESS_TEXT = {
        "en": "Your meeting deleted successfully ✅\n\n📅 Date: {date} ({weekday})\n🚪 Room: {room_name}\n▶️ From: {start_time}\n◀️ To: {end_time}",
        "fa": "رزرو شما با موفقیت حذف شد ✅\n\n📅 تاریخ: {date} ({weekday})\n🚪 اتاق: {room_name}\n▶️ از: {start_time}\n◀️ تا: {end_time}"
    }
    PAST_RESERVATIONS_HEADER = {
        "en": "🔍 Your Past Reservations are:\n\n",
        "fa": "🔍 رزرو های گذشته شما:\n\n"
    }
    NO_PAST_RESERVATIONS_TEXT = {
        "en": "You don't have any Past Reservations 🤲🏻",
        "fa": "شما هیچ رزروی در گذشته ندارید 🤲🏻"
    }
    EDIT_RESERVATION_BUTTON = {
        "en": "✏️ Edit Reservations",
        "fa": "✏️ ویرایش رزرو ها"
    }
    DELETE_RESERVATION_BUTTON = {
        "en": "🗑 Delete Reservations",
        "fa": "🗑 حذف رزرو ها"
    }
    FUTURE_BUTTON = {
        "en": "🗓 Future",
        "fa": "🗓 آینده"
    }
    PAST_BUTTON = {
        "en": "🔍 Past",
        "fa": "🔍 گذشته"
    }
    EDIT_DATE_BUTTON = {
        "en": "📅 Edit Date",
        "fa": "📅 ویرایش تاریخ"
    }
    EDIT_ROOM_BUTTON = {
        "en": "🚪 Edit Room",
        "fa": "🚪 ویرایش اتاق"
    }
    EDIT_HOURS_BUTTON = {
        "en": "🕰 Edit Hours",
        "fa": "🕰 ویرایش زمان"
    }
    PREVIOUS_BUTTON = {
        "en": "⬅️ Previous",
        "fa": "⬅️ قبلی"
    }
    NEXT_BUTTON = {
        "en": "Next ➡️",
        "fa": "بعدی ➡️"
    }
    HELP = {
        "en": "🚪 Meeting Reservation Bot 🚪\n\n"
              "Available Commands:\n"
              "/start - Start the bot to select from menu\n"
              "/reservation - 🚪 Submit-View-Edit Meeting Reservations\n"
              "/admin_commands - 🔧 Admins can manage Meeting Rooms (view-add-edit)\n"
              "/view_schedule - 🗓 View Schedule for Meeting Rooms (Daily-Custom Day-Weekly)\n"
              "/settings - ⚙️ Bot Settings (You can set Language of the bot)\n"
              "/help - ℹ️ Get help information",
        "fa": "🚪 بات رزرو اتاق جلسات 🚪\n\n"
              "دستور های در دسترس:\n"
              "/start - دستور شروع بات برای دسترسی به منو\n"
              "/reservation - 🚪 دستور رزرو، ویرایش و حذف رزرو ها\n"
              "/admin_commands - 🔧 دستور مدیریت اتاق جلسات توسط ادمین ها (مشاهده، ویرایش و حذف)\n"
              "/view_schedule - 🗓 دستور مشاهده جدول رزرو اتاق ها (روزانه، روز خاص و هفتگی)\n"
              "/settings - ⚙️ دستور تنظیمات بات (انتخاب زبان بات)\n"
              "/help - ℹ️ راهنمای دستورات بات"
    }
    START = {
        "en": "Hello! I can help you to Reserve a Meeting Room 🚪",
        "fa": "سلام! این بات برای کمک به شما برای رزرو اتاق جلسات ایجاد شده است 🚪"
    }


def get_text(text_key, language):
    return text_key.value[language]


def convert_to_persian_numerals(text):
    persian_numerals = {
        '0': '۰',
        '1': '۱',
        '2': '۲',
        '3': '۳',
        '4': '۴',
        '5': '۵',
        '6': '۶',
        '7': '۷',
        '8': '۸',
        '9': '۹'
    }
    for eng, per in persian_numerals.items():
        text = text.replace(eng, per)
    return text


def change_num_as_lang(txt, user_language):
    if user_language == 'fa':
        return convert_to_persian_numerals(txt)
    return txt
