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
        "fa": "🗣 زبان بات برای شما به فارسی تغییر کرد.",
        "en": "🗣 The bot's language changed to English for you."
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
    # def format(self, language, **kwargs):
    #     text_template = self.value.get(language, "Text not found")
    #     return text_template.format(**kwargs)


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
