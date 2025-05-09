from enum import Enum


class BotText(Enum):
    START = {
        "en": "Hello!\nI can help you to Reserve a Meeting Room 🚪",
        "fa": "سلام!\nاین بات برای رزرو اتاق جلسات ایجاد شده است 🚪",
    }
    HELP_CONTINUOUS_RESERVE_AVAILABLE = {
        "en": "..:: Meeting Reservation Bot ::..\n\n"
        "Keyboard Buttons:\n"
        "🚪 Reservation - Submit-View-Edit Meeting Reservations\n"
        "🔄 Continuous Reservation - 🔄 Submit a Continuous Reservation (up to a maximum of six months)\n"
        "🗓 View Schedule - 🗓 View Schedule for Meeting Rooms (Daily-Custom Day-Weekly)\n\n"
        "Available Commands:\n"
        "/start - Start the bot to select from menu\n"
        "/admin_commands - 🔧 Admins can manage Meeting Rooms (view-add-edit)\n"
        "/settings - ⚙️ Bot Settings (You can set Language of the bot)\n"
        "/help - ℹ️ Get help information",
        "fa": "..:: بات رزرو اتاق جلسات ::..\n\n"
        "دکمه‌های کیبورد:\n"
        "🚪 رزرو اتاق - ثبت و مشاهده و ویرایش یا حذف رزرو ها\n"
        "🔄 رزرو دوره ای - ثبت یک رزرو دوره ای (حداکثر تا شش ماه)\n"
        "🗓 مشاهده جدول رزرو ها - مشاهده برنامه اتاق‌ های جلسه (امروز-روز خاص-هفتگی)\n\n"
        "دستورات موجود:\n"
        "/start - شروع ربات برای انتخاب از منو\n"
        "/admin_commands - 🔧 مدیران می ‌توانند اتاق‌ های جلسات را مدیریت کنند. (مشاهده-اضافه-ویرایش)\n"
        "/settings - ⚙️ تنظیمات ربات (می‌توانید زبان ربات را انتخاب کنید)\n"
        "/help - ℹ️ دریافت اطلاعات",
    }
    HELP = {
        "en": "..:: Meeting Reservation Bot ::..\n\n"
        "Keyboard Buttons:\n"
        "🚪 Reservation - Submit-View-Edit Meeting Reservations\n"
        "🗓 View Schedule - 🗓 View Schedule for Meeting Rooms (Daily-Custom Day-Weekly)\n\n"
        "Available Commands:\n"
        "/start - Start the bot to select from menu\n"
        "/admin_commands - 🔧 Admins can manage Meeting Rooms (view-add-edit)\n"
        "/settings - ⚙️ Bot Settings (You can set Language of the bot)\n"
        "/help - ℹ️ Get help information",
        "fa": "..:: بات رزرو اتاق جلسات ::..\n\n"
        "دکمه‌های کیبورد:\n"
        "🚪 رزرو اتاق - ثبت و مشاهده و ویرایش یا حذف رزرو ها\n"
        "🗓 مشاهده جدول رزرو ها - مشاهده برنامه اتاق‌ های جلسه (امروز-روز خاص-هفتگی)\n\n"
        "دستورات موجود:\n"
        "/start - شروع ربات برای انتخاب از منو\n"
        "/admin_commands - 🔧 مدیران می ‌توانند اتاق‌ های جلسات را مدیریت کنند. (مشاهده-اضافه-ویرایش)\n"
        "/settings - ⚙️ تنظیمات ربات (می‌توانید زبان ربات را انتخاب کنید)\n"
        "/help - ℹ️ دریافت اطلاعات",
    }
    RESERVATION_TEXT = {
        "en": "Reserve a room anytime with «🚪 New Reservation» or manage reservations via «📝 My Reservations»",
        "fa": "شما می توانید یک اتاق را برای هر زمانی که تمایل داشتید، با دکمه «🚪 رزرو جدید» رزرو کنید و یا از طریق دکمه «👀 رزرو های من» رزرو های خود را مدیریت کنید.",
    }
    NEW_RESERVATION_BUTTON = {"en": "🚪 New Reservation", "fa": "🚪 رزرو جدید"}
    MY_RESERVATIONS_BUTTON = {"en": "👀 My Reservations", "fa": "👀 رزرو های من"}
    CHOOSE_DATE_TEXT = {
        "en": "📅 Choose a Date for Your Meeting (Available up to Next Week)",
        "fa": "📅 تاریخ جلسه خود را انتخاب کنید. (تا هفته آینده)",
    }
    ROOM_SELECTION_TEXT = {
        "en": "📅 Date: {date} ({weekday})\n❓ Room:",
        "fa": "📅 تاریخ: {date} ({weekday})\n❓ اتاق:",
    }
    HOUR_SELECTION_TEXT = {
        "en": "📅 Date: {date} ({weekday})\n🚪 Room: {room_name}\n❓ From:",
        "fa": "📅 تاریخ: {date} ({weekday})\n🚪 اتاق: {room_name}\n❓ از:",
    }
    ADD_TIME_FIRST_STATUS = {
        "en": "📅 Date: {date} ({weekday})\n🚪 Room: {room_name}\n▶️ From: {start_time}\n◀️ To: {end_time}\n(You can change the end time)",
        "fa": "📅 تاریخ: {date} ({weekday})\n🚪 اتاق: {room_name}\n▶️ از: {start_time}\n◀️ تا: {end_time}\n(می توانید زمان پایان را تغییر دهید)",
    }
    ADD_TIME_SECOND_STATUS = {
        "en": "📅 Date: {date} ({weekday})\n🚪 Room: {room_name}\n▶️ From: {start_time}\n◀️ To: {end_time}",
        "fa": "📅 تاریخ: {date} ({weekday})\n🚪 اتاق: {room_name}\n▶️ از: {start_time}\n◀️ تا: {end_time}",
    }
    ADD_TIME_DEFAULT = {
        "en": "📅 Date: {date} ({weekday})\n🚪 Room: {room_name}\n❓ From:",
        "fa": "📅 تاریخ: {date} ({weekday})\n🚪 اتاق: {room_name}\n❓ از:",
    }
    CONFIRM_RESERVATION_TEXT = {
        "en": "Your Reservation submitted ✅\n\n📅 Date: {date} ({weekday})\n🚪 Room: {room_name}\n▶️ From: {start_time}\n◀️ To: {end_time}",
        "fa": "رزرو شما ثبت شد ✅\n\n📅 تاریخ: {date} ({weekday})\n🚪 اتاق: {room_name}\n▶️ از: {start_time}\n◀️ تا: {end_time}",
    }
    WHO_RESERVED = {
        "en": "❗️ User ({name}) has been reserved this hour.",
        "fa": "❗️ کاربری به نام ({name}) این زمان را رزرو کرده است.",
    }
    USER_RESERVATIONS_TEXT = {
        "en": "View upcoming reservations with «🗓 Future» or past reservations using «🔍 Past»",
        "fa": "برای مشاهده رزرو های آینده از «🗓 آینده» و برای رزرو های گذشته از «🔍 گذشته» استفاده کنید.",
    }
    NO_RESERVATIONS_TEXT = {
        "en": "You haven’t made any Reservations yet 🙁",
        "fa": "شما هنوز هیچ رزروی انجام نداده ‌اید 🙁",
    }
    FUTURE_RESERVATIONS_HEADER = {
        "en": "🗓 Your Future Reservations are:\n\n",
        "fa": "🗓 رزرو های آینده شما:\n\n",
    }
    NO_FUTURE_RESERVATIONS_TEXT = {
        "en": "You don't have any Future Reservation 🤲🏻",
        "fa": "شما هیچ رزروی برای آینده ندارید 🤲🏻",
    }
    EDIT_RESERVATIONS_TEXT = {
        "en": "📝 Choose the Reservation you'd like to edit:",
        "fa": "📝 رزروی که می ‌خواهید ویرایش کنید را انتخاب کنید:",
    }
    EDIT_DATE_TEXT = {
        "en": "🚪 Room: {room_name}\n▶️ From: {start_time}\n◀️ To: {end_time}\n❓ Date:",
        "fa": "🚪 اتاق: {room_name}\n▶️ از: {start_time}\n◀️ تا: {end_time}\n❓ تاریخ:",
    }
    EDIT_ROOM_TEXT = {
        "en": "📅 Date: {date} ({weekday})\n▶️ From: {start_time}\n◀️ To: {end_time}\n❓ Room:",
        "fa": "📅 تاریخ: {date} ({weekday})\n▶️ از: {start_time}\n◀️ تا: {end_time}\n❓ اتاق:",
    }
    EDIT_HOURS_TEXT = {
        "en": "📅 Date: {date} ({weekday})\n🚪 Room: {room_name}\n❓ From:",
        "fa": "📅 تاریخ: {date} ({weekday})\n🚪 اتاق: {room_name}\n❓ از:",
    }
    DELETE_RESERVATIONS_TEXT = {
        "en": "🗑 Choose the Reservation you'd like to delete:",
        "fa": "🗑 رزروی که می ‌خواهید حذف کنید را انتخاب کنید:",
    }
    DELETE_SUCCESS_TEXT = {
        "en": "Your meeting deleted successfully ✅\n\n📅 Date: {date} ({weekday})\n🚪 Room: {room_name}\n▶️ From: {start_time}\n◀️ To: {end_time}",
        "fa": "رزرو شما با موفقیت حذف شد ✅\n\n📅 تاریخ: {date} ({weekday})\n🚪 اتاق: {room_name}\n▶️ از: {start_time}\n◀️ تا: {end_time}",
    }
    PAST_RESERVATIONS_HEADER = {
        "en": "🔍 Your Past Reservations are:\n\n",
        "fa": "🔍 رزرو های گذشته شما:\n\n",
    }
    NO_PAST_RESERVATIONS_TEXT = {
        "en": "You don't have any Past Reservations 🤲🏻",
        "fa": "شما هیچ رزروی در گذشته ندارید 🤲🏻",
    }
    EDIT_RESERVATION_BUTTON = {"en": "✏️ Edit Reservations", "fa": "✏️ ویرایش رزرو ها"}
    DELETE_RESERVATION_BUTTON = {"en": "🗑 Delete Reservations", "fa": "🗑 حذف رزرو ها"}
    FUTURE_BUTTON = {"en": "🗓 Future", "fa": "🗓 آینده"}
    PAST_BUTTON = {"en": "🔍 Past", "fa": "🔍 گذشته"}
    EDIT_DATE_BUTTON = {"en": "📅 Edit Date", "fa": "📅 ویرایش تاریخ"}
    EDIT_ROOM_BUTTON = {"en": "🚪 Edit Room", "fa": "🚪 ویرایش اتاق"}
    EDIT_HOURS_BUTTON = {"en": "🕰 Edit Hours", "fa": "🕰 ویرایش زمان"}
    PREVIOUS_BUTTON = {"en": "⬅️ Previous", "fa": "⬅️ قبلی"}
    NEXT_BUTTON = {"en": "Next ➡️", "fa": "بعدی ➡️"}
    ENTER_NAME = {
        "en": "Enter your Name Please:\n\nIf you want to cancel the operation tap on /cancel",
        "fa": "لطفاً نام خود را وارد کنید:\n\nاگر می‌ خواهید عملیات را لغو کنید، روی /cancel کلیک کنید.",
    }
    NAME_SUBMITTED = {
        "en": "Your name submitted successfully 👍🏻\nYour name: {name}",
        "fa": "نام شما با موفقیت ثبت شد 👍🏻\nنام شما: {name}",
    }
    CHOOSE_WEEKDAY_TEXT = {
        "en": "📅 Choose a Weekday for Your Continuous Meeting:",
        "fa": "📅 روز جلسه دوره ای خود را انتخاب کنید:",
    }
    CHOOSE_HOURS_TEXT = {
        "en": "📅 Weekday: {weekday}\n❓ From:",
        "fa": "📅 روز هفته: {weekday}\n❓ از:",
    }
    START_HOURS_TEXT = {
        "en": "{weekday}\n❓ From:",
        "fa": "{weekday}\n❓ از:",
    }
    FIRST_HOURS_TEXT = {
        "en": "{weekday}\n▶️ From: {start}\n◀️ To: {end}\n(You can change the end time)",
        "fa": "{weekday}\n▶️ از: {start}\n◀️ تا: {end}\n(می توانید زمان پایان را تغییر دهید)",
    }
    SECOND_HOURS_TEXT = {
        "en": "{weekday}\n▶️ From: {start}\n◀️ To: {end}",
        "fa": "{weekday}\n▶️ از: {start}\n◀️ تا: {end}",
    }
    CHOOSE_HOURS_TEXT_CHARGE = {
        "en": "📅 Weekday: {weekday}\n🔋 Charge: {charge}\n❓ From:",
        "fa": "📅 روز هفته: {weekday}\n🔋 شارژ: {charge}\n❓ از:",
    }
    START_HOURS_TEXT_CHARGE = {
        "en": "{weekday}\n🔋 Charge: {charge}\n❓ From:",
        "fa": "{weekday}\n🔋 شارژ: {charge}\n❓ از:",
    }
    FIRST_HOURS_TEXT_CHARGE = {
        "en": "{weekday}\n🔋 Charge: {charge}\n▶️ From: {start}\n◀️ To: {end}\n(You can change the end time)",
        "fa": "{weekday}\n🔋 شارژ: {charge}\n▶️ از: {start}\n◀️ تا: {end}\n(می توانید زمان پایان را تغییر دهید)",
    }
    SECOND_HOURS_TEXT_CHARGE = {
        "en": "{weekday}\n🔋 Charge: {charge}\n▶️ From: {start}\n◀️ To: {end}",
        "fa": "{weekday}\n🔋 شارژ: {charge}\n▶️ از: {start}\n◀️ تا: {end}",
    }
    CHOOSE_ROOM_TEXT = {
        "en": "{last_data}\n❓ Room:",
        "fa": "{last_data}\n❓ اتاق:",
    }
    CHOOSE_CHARGE_TEXT = {
        "en": "{last_data}\n🚪 Room: {room}\n❓ Weeks:\n- 4 weeks ➡️ 1 month\n- 8 weeks ➡️ 2 months\n- 12 weeks ➡️ 3 months\n- 17 weeks ➡️ 4 months\n- 21 weeks ➡️ 5 months\n- 25 weeks ➡️ 6 months",
        "fa": "{last_data}\n🚪 اتاق: {room}\n❓ هفته‌ها:\n- 4 هفته ⬅️ 1 ماه\n- 8 هفته ⬅️ 2 ماه\n- 12 هفته ⬅️ 3 ماه\n- 17 هفته ⬅️ 4 ماه\n- 21 هفته ⬅️ 5 ماه\n- 25 هفته ⬅️ 6 ماه",
    }
    SECOND_CHARGE_TEXT = {
        "en": "{last_data}\n❓ Weeks: {weeks}\n- 4 weeks ➡️ 1 month\n- 8 weeks ➡️ 2 months\n- 12 weeks ➡️ 3 months\n- 17 weeks ➡️ 4 months\n- 21 weeks ➡️ 5 months\n- 25 weeks ➡️ 6 months",
        "fa": "{last_data}\n❓ هفته‌ها: {weeks}\n- 4 هفته ⬅️ 1 ماه\n- 8 هفته ⬅️ 2 ماه\n- 12 هفته ⬅️ 3 ماه\n- 17 هفته ⬅️ 4 ماه\n- 21 هفته ⬅️ 5 ماه\n- 25 هفته ⬅️ 6 ماه",
    }
    WEEKS_TEXT = {
        "en": "{last_data}\n🗓️ Weeks: {weeks}\n{week_as_date}",
        "fa": "{last_data}\n🗓️ هفته‌ها: {weeks}\n{week_as_date}",
    }
    ROOMS = {"en": "🚪 Rooms:\n", "fa": "🚪 اتاق ها:\n"}
    ADD_ROOM_BUTTON = {"en": "➕ Add Room", "fa": "➕ اتاق جدید"}
    EDIT_ROOM_ADMIN = {"en": "✏️ Edit Rooms", "fa": "✏️ ویرایش اتاق ها"}
    DELETE_ROOM_ADMIN = {"en": "🗑 Delete Rooms", "fa": "🗑 حذف اتاق ها"}
    VIEW_USERS_BUTTON = {"en": "🔍 View All Users", "fa": "🔍 مشاهده همه کاربران"}
    DELETE_USERS_BUTTON = {"en": "🗑 Delete Users", "fa": "🗑 حذف کاربران"}
    CHARGE_USER = {"en": "🔋Charge User", "fa": "🔋شارژ کاربر"}
    NO_MEETING_ROOMS = {
        "en": "No meeting room has been added yet 🙁",
        "fa": "هنوز هیچ اتاقی اضافه نشده است 🙁",
    }
    ADD_ROOM = {
        "en": "🚪 Enter the Name of the Room:\n\nIf you want to cancel the operation tap on /cancel",
        "fa": "🚪 نام اتاق را وارد کنید:\n\nاگر می‌ خواهید عملیات را لغو کنید، روی /cancel کلیک کنید.",
    }
    ROOM_ADDED = {
        "en": "Name of the Room submitted successfully 👍🏻\n",
        "fa": "نام اتاق با موفقیت ثبت شد 👍🏻\n",
    }
    ROOM_UPDATED = {
        "en": "Name of the Room updated successfully 👍🏻\n",
        "fa": "نام اتاق با موفقیت بروزرسانی شد 👍🏻\n",
    }
    EDIT_ROOM = {
        "en": "✏️ Select the Room which you want to edit:",
        "fa": "✏️ اتاقی که قصد ویرایش نام آن را دارید، انتخاب کنید:",
    }
    ADMINS_TEXT_UPDATE = {
        "en": "🔄 This admin updated «{old_name}» Room to «{room_name}»\n👤 Name: {name}\n✍🏻 TG Username: @{username}",
        "fa": "🔄 این ادمین نام اتاق «{old_name}» را به «{room_name}» بروزرسانی کرد.\n👤 نام: {name}\n✍🏻 یوزرنیم تلگرام: @{username}",
    }
    ADMINS_TEXT_ADD = {
        "en": "➕ This admin added «{room_name}» Room.\n👤 Name: {name}\n✍🏻 TG Username: @{username}",
        "fa": "➕ این ادمین اتاقی بنام «{room_name}» را اضافه کرد.\n👤 نام: {name}\n✍🏻 یوزرنیم تلگرام: @{username}",
    }
    ADMINS_TEXT_DELETE = {
        "en": "🗑 This admin deleted «{room_name}» Room.\n👤 Name: {name}\n✍🏻 TG Username: @{username}",
        "fa": "🗑 این ادمین اتاق «{room_name}» را حذف کرد.\n👤 نام: {name}\n✍🏻 یوزرنیم تلگرام: @{username}",
    }
    USERS_TEXT_UPDATE = {
        "en": "🔄 Name of «{old_name}» Room updated to «{room_name}»",
        "fa": "🔄 نام اتاق «{old_name}» به «{room_name}» بروزرسانی شد.",
    }
    DELETE_ROOM = {
        "en": "🗑 Select the Room which you want to delete:",
        "fa": "🗑 اتاقی که می‌خواهید حذف کنید را انتخاب کنید:",
    }
    ROOM_DELETED = {
        "en": "The Room with the name «{room_name}» deleted successfully 🗑\n",
        "fa": "اتاق با نام «{room_name}» با موفقیت حذف شد 🗑\n",
    }
    USERS_ROOM_DELETED = {
        "en": "🗑 The Room with the name «{room_name}» has been deleted.\nUnfortunately your reservation at this room canceled 🙏🏻\n\nIf you want to reserve a new room for your meeting tap on «🚪 Reservation»",
        "fa": "🗑 اتاق با نام «{room_name}» حذف شده است.\nمتأسفانه رزرو شما در این اتاق لغو شد 🙏🏻\n\nاگر می‌خواهید اتاق جدیدی برای جلسه خود رزرو کنید، روی «🚪 رزرو اتاق» کلیک کنید.",
    }
    UPDATE_ROOM_NAME = {
        "en": "🚪 Enter the new Name for «{room_name}»:\n\nIf you want to cancel the operation tap on /cancel",
        "fa": "🚪 نام جدید را برای اتاق «{room_name}» وارد کنید:\n\nاگر می‌خواهید عملیات را لغو کنید، روی /cancel کلیک کنید.",
    }
    VIEW_USERS_ONE = {
        "en": "👥 Users:\nName | TG Username | Chat_id (Optional)\n\n",
        "fa": "👥 کاربران:\nنام | یوزرنیم تلگرام | چت آیدی (اگر نیاز باشد)\n\n",
    }
    VIEW_USERS_TWO = {
        "en": "\n(* before user's name means that he is admin)",
        "fa": "\n(* قبل از نام کاربر به معنای ادمین بودن است)",
    }
    EDIT_NAME = {"en": "✏️ Edit Name", "fa": "✏️ ویرایش نام"}
    EDIT_USERS_NAME = {
        "en": "✏️ Select the TG username whose name you want to edit:",
        "fa": "✏️ یوزرنیم تلگرام کاربری که می‌ خواهید نام او را ویرایش کنید انتخاب کنید:",
    }
    EDIT_USERS_OLD_NAME_USERNAME = {
        "en": "Enter the New Name for @{username} (Old Name👉🏻{name}):\n\nIf you want to cancel the operation tap on /cancel",
        "fa": "نام جدید را برای @{username} وارد کنید (نام قبل👈🏻{name}):\n\nاگر می‌خواهید عملیات را لغو کنید، روی /cancel کلیک کنید.",
    }
    EDIT_USERS_OLD_NAME = {
        "en": "Enter the New Name for «{name}»:\n\nIf you want to cancel the operation tap on /cancel",
        "fa": "نام جدید را برای «{name}» وارد کنید:\n\nاگر می‌خواهید عملیات را لغو کنید، روی /cancel کلیک کنید.",
    }
    EDIT_USERS_OLD_NAME_CHAT_ID = {
        "en": "Enter the New Name for the user with chat_id {chat_id}:\n\nIf you want to cancel the operation tap on /cancel",
        "fa": "نام جدید را برای کاربر با چت آیدی {chat_id} وارد کنید:\n\nاگر می‌خواهید عملیات را لغو کنید، روی /cancel کلیک کنید.",
    }
    YOUR_NAME_UPDATED = {
        "en": "🔄 Your name updated to «{name}» by @{admin}",
        "fa": "🔄 اسم شما توسط @{admin} به «{name}» بروزرسانی شد.",
    }
    NAME_UPDATED_USERNAME = {
        "en": "🔄 The name for @{username} updated to «{new_name}» successfully 👍🏻",
        "fa": "🔄 نام @{username} به «{new_name}» با موفقیت بروزرسانی شد 👍🏻",
    }
    NAME_UPDATED_CHAT_ID = {
        "en": "🔄 The name for the user with chat_id {chat_id} updated to «{name}» successfully 👍🏻",
        "fa": "🔄 نام کاربر با چت آیدی {chat_id} به «{name}» با موفقیت بروزرسانی شد 👍🏻",
    }
    RETRY = {"en": "🆕 Retry", "fa": "🆕 تلاش دوباره"}
    DELETE_USERS_NAME = {
        "en": "🗑 Select the TG username whose name you want to delete:",
        "fa": "🗑 یوزرنیم تلگرام کاربری که می‌ خواهید نام او را حذف کنید انتخاب کنید:",
    }
    USER_DELETED_USERNAME = {
        "en": "The User with the TG username @{uname} deleted successfully 🗑\n",
        "fa": "کاربر با یوزرنیم تلگرام @{uname} با موفقیت حذف شد 🗑\n",
    }
    USER_DELETED_NAME = {
        "en": "The User with the name «{name}» deleted successfully 🗑\n",
        "fa": "کاربر با نام «{name}» با موفقیت حذف شد 🗑\n",
    }
    USER_DELETED_CHAT_ID = {
        "en": "The User with chat_id {chat_id} deleted successfully 🗑\n",
        "fa": "کاربر با چت آیدی {chat_id} با موفقیت حذف شد 🗑\n",
    }
    ADMIN_DELETED_USER = {
        "en": "You have been removed from the bot by admin 🙋🏻‍♂️",
        "fa": "شما توسط ادمین از بات حذف شدید 🙋🏻‍♂️",
    }
    ADMIN_NOT_ALLOWED_FOR_DELETE = {
        "en": "You are not allowed to delete admins ⛔️",
        "fa": "شما اجازه ندارید ادمین ها را حذف کنید ⛔️",
    }
    SELECTION_CHARGE_USER = {
        "en": "🔋 Select the TG username whose name you want to charge:",
        "fa": "🔋 یوزرنیم تلگرام کاربری که می‌ خواهید حساب او را شارژ کنید، انتخاب کنید:",
    }
    GET_CHARGE_USERNAME = {
        "en": "Enter the charge quantity for @{username} (current charge 👉🏻 {charge}):\n\nIf you want to cancel the operation tap on /cancel",
        "fa": "تعداد شارژ را برای @{username} وارد کنید (شارژ فعلی 👈🏻 {charge}):\n\nاگر می‌ خواهید عملیات را لغو کنید، روی /cancel کلیک کنید.",
    }
    GET_CHARGE_NAME = {
        "en": "Enter the charge quantity for «{name}» (current charge 👉🏻 {charge}):\n\nIf you want to cancel the operation tap on /cancel",
        "fa": "تعداد شارژ را برای «{name}» وارد کنید (شارژ فعلی 👈🏻 {charge}):\n\nاگر می‌ خواهید عملیات را لغو کنید، روی /cancel کلیک کنید.",
    }
    GET_CHARGE_CHAT_ID = {
        "en": "Enter the charge quantity for the user with chat_id {chat_id} (current charge 👉🏻 {charge}):\n\nIf you want to cancel the operation tap on /cancel",
        "fa": "تعداد شارژ را برای کاربر با چت آیدی {chat_id} وارد کنید (شارژ فعلی 👈🏻 {charge}):\n\nاگر می‌ خواهید عملیات را لغو کنید، روی /cancel کلیک کنید.",
    }
    USER_CHARGE_MESSAGE = {
        "en": "🔋 Your account charged 🔋\n♻️ Amount: {charge}\n💰 Current Charge: {new_charge}",
        "fa": "🔋 حساب شما شارژ شد 🔋\n♻️ مقدار شارژ: {charge}\n💰 شارژ فعلی: {new_charge}",
    }
    MANAGER_CHARGE_MESSAGE = {
        "en": "🔋 User's account charged 🔋\n👤 User: {user}\n♻️ Amount: {charge}\n💰 Current Charge: {new_charge}",
        "fa": "🔋 حساب کاربر شارژ شد 🔋\n👤 کاربر: {user}\n♻️ مقدار شارژ: {charge}\n💰 شارژ فعلی: {new_charge}",
    }
    MESSAGE_NOT_SENT_USERNAME = {
        "en": "An error occurred while sending charge message to @{username}:\n{error}",
        "fa": "مشکلی در ارسال پیام شارژ به @{username} پیش آمد:\n{error}",
    }
    MESSAGE_NOT_SENT_NAME = {
        "en": "An error occurred while sending charge message to «{name}»:\n{error}",
        "fa": "مشکلی در ارسال پیام شارژ به «{name}» پیش آمد:\n{error}",
    }
    MESSAGE_NOT_SENT_CHAT_ID = {
        "en": "An error occurred while sending charge message to the user with chat_id {chat_id}:\n{error}",
        "fa": "مشکلی در ارسال پیام شارژ به کاربر با چت آیدی {chat_id} پیش آمد:\n{error}",
    }
    EDIT_WEEKS_BUTTON = {"en": "✏️ Edit Weeks", "fa": "✏️ ویرایش هفته ها"}
    CHAT_WITH_BOOKER_BUTTON = {"en": "💬 Chat with Booker", "fa": "💬 صحبت با رزرو کننده"}
    RESERVE_POSSIBLES_BUTTON = {
        "en": "🛎 Reserve Possible weeks",
        "fa": "🛎 رزرو هفته های ممکن",
    }
    CANCEL_RESERVATION_BUTTON = {"en": "👎🏻 Cancel", "fa": "👎🏻 لغو عملیات"}
    CANCEL_RESERVATION_TEXT = {
        "en": "❗️ Your request for continuous reservation canceled.",
        "fa": "❗️ درخواست شما برای رزرو دوره ای کنسل شد.",
    }
    CONFIRMED_COUNTINUOUS_RESERVATION = {
        "en": "✅ Your request for a continuous reservation has been submitted successfully.\n💰 Billing Charge: {billing_charge}\n🔋 Current Charge: {charge}\n\n{last_data}",
        "fa": "✅ درخواست شما برای رزرو دوره ای با موفقیت ثبت شد.\n💰 مقدار شارژ مصرف شده: {billing_charge}\n🔋 شارژ فعلی: {charge}\n\n{last_data}",
    }
    FREE_CONFIRMED_COUNTINUOUS_RESERVATION = {
        "en": "✅ Your request for a continuous reservation has been submitted successfully.\n\n{last_data}",
        "fa": "✅ درخواست شما برای رزرو دوره ای با موفقیت ثبت شد.\n\n{last_data}",
    }
    SCHEDULE_SELECTION = {
        "en": "🗓 Choose Your Schedule:",
        "fa": "🗓 قصد مشاهده کدام جدول را دارید؟",
    }
    TODAY_BUTTON = {"en": "📅 Today", "fa": "📅 جدول امروز"}
    CUSTOM_SCHEDULE_BUTTON = {"en": "📆 Custom Day", "fa": "📆 جدول یک روز خاص"}
    WEEKLY_BUTTON = {"en": "🗓 Weekly", "fa": "🗓 جدول هفتگی"}
    TODAY_SCHEDULE = {
        "en": "📊 Today's Schedule for {room_name}",
        "fa": "📊 جدول امروز برای {room_name}",
    }
    CUSTOM_SCHEDULE = {
        "en": "📊 Schedule for {custom_date} in {room_name}",
        "fa": "📊 جدول {custom_date} روز برای {room_name}",
    }
    EMPTY_DAY_SCHEDULE = {
        "en": "No reservations for {room_name} 🕳",
        "fa": "هیچ رزروی برای «{room_name}» ثبت نشده است 🕳",
    }
    WEEKLY_SCHEDULE = {
        "en": "📊 Weekly schedule for {room_name}",
        "fa": "📊 جدول هفتگی برای {room_name}",
    }
    EMPTY_WEEKLY_SCHEDULE = {
        "en": "No weekly reservations for {room_name} 🕳",
        "fa": "هیچ رزروی در این هفته برای «{room_name}» ثبت نشده است 🕳",
    }
    CUSTOM_DATE_TEXT = {
        "en": "📅 Choose a Date for View Meetings (Available up to Next Week):",
        "fa": "📅 تاریخ مورد نظر برای مشاهده جدول اتاق جلسات را انتخاب کنید (تا هفته آینده موجود است):",
    }
    REMINDER_MESSAGE = {
        "en": "⏰ Reminder ⏰\nYou have a meeting reservation for «{reserve}» in 2 hours.\n\nNeed to cancel the reservation❓\nTap «❌ Cancel»\nOtherwise, your reservation will remain confirmed ☺️",
        "fa": "⏰ یادآوری ⏰\nشما یک رزرو برای «{reserve}» در 2 ساعت آینده دارید.\n\nنیاز به لغو رزرو دارید ؟\nروی «لازم ندارم،پاکش کن» کلیک کنید.\nدر غیر این صورت، رزرو شما تأیید شده باقی خواهد ماند ☺️",
    }
    CHECKOUT_MESSAGE = {
        "en": "▶️ Your meeting reservation has started.\n\n❕ If your meeting finished sooner than {reserve}, please tap on «⏹️ Checkout» to allow others to reserve the room in the future.",
        "fa": "▶️ جلسه ای که رزرو کرده بودید شروع شده است.\n\n❕ اگر جلسه شما زودتر از {reserve} به پایان رسید، لطفاً روی «⏹️ پایان جلسه» کلیک کنید تا دیگران بتوانند از آن زمان به بعد اتاق را رزرو کنند.",
    }
    OK_REMINDER_BUTTON = {"en": "🆗", "fa": "باشه ممنون ✅"}
    CANCEL_REMINDER_BUTTON = {"en": "❌ Cancel", "fa": "لازم ندارم،پاکش کن"}
    CHECKOUT_BUTTON = {"en": "⏹️ Checkout", "fa": "⏹️ پایان جلسه"}
    FUTURE_MEETING_START = {
        "en": "Your meeting will start at {start_time} ✅",
        "fa": "جلسه شما ساعت {start_time} شروع خواهد شد ✅",
    }
    FUTURE_MEETING_END = {
        "en": "Your meeting will end at {end_time} ✅",
        "fa": "جلسه شما ساعت {end_time} به پایان خواهد رسید ✅",
    }
    RESERVE_NOT_EXISTS = {
        "en": "This reservation doesn't exist ⛔️",
        "fa": "این رزرو دیگر وجود ندارد ⛔️",
    }
    CANCEL_FIXED = {
        "en": "Your meeting canceled successfully ✅",
        "fa": "جلسه شما کنسل شد ✅",
    }
    CANCEL_FIXED_TIME = {
        "en": "You canceled your meeting at «{str_time}» successfully ✅",
        "fa": "رزرو شما کنسل شد ✅\nزمان کنسل: {str_time}",
    }
    CHECKOUT_FIXED = {
        "en": "Thanks for your attention 🙏🏻\nYou checked out your meeting at {str_time}",
        "fa": "ممنونیم از حسن توجه شما 🙏🏻\n زمان پایان جلسه: {str_time}",
    }
    LANGUAGE_TEXT = {
        "en": "🗣 Language: English\nIf you'd like to change the bot's language tap on the button below.",
        "fa": " 🗣 زبان: فارسی\nاگر تمایل به تغییر زبان دارید روی دکمه زیر کلیک کنید.",
    }
    PERSIAN_CALLBACK = {
        "en": "🗣 The bot's language changed to English for you.",
        "fa": "🗣 زبان بات برای شما به فارسی تغییر کرد.",
    }
    BACK_BUTTON = {"en": "⬅️ Back", "fa": "⬅️ بازگشت"}
    CONFIRM_BUTTON = {"en": "🟢 Confirm 🟢", "fa": "🟢 تأیید 🟢"}
    OPERATION_CANCELED = {"en": "Operation cancelled!", "fa": "عملیات لغو شد!"}
    INVALID_TIME_ALERT = {
        "en": "The end time can't be before the start time 🗿",
        "fa": "زمان پایان نمی ‌تواند قبل از زمان شروع باشد 🗿",
    }
    INCOMPLETE_HOURS_ALERT = {
        "en": "You can't confirm before completing the hours ⛔️",
        "fa": "قبل از تکمیل ساعات نمی ‌توانید تأیید کنید ⛔️",
    }
    INVALID_RESERVED_TIMES = {
        "en": "Reserved times can't be selected ⛔️",
        "fa": "زمان های از پیش رزرو شده نمی توانند در بازه انتخابی شما باشند ⛔️",
    }
    INVALID_DURATION = {
        "en": "The duration must be less than 4 hours ⛔️",
        "fa": "طول بازه زمانی جلسه نباید بیش از 4 ساعت باشد ⛔️",
    }
    INVALID_PAST_TIMES = {
        "en": "Only future times can be reserved ⛔️",
        "fa": "امکان رزرو زمان های گذشته وجود ندارد ⛔️",
    }
    INVALID_ROOM_NAME = {
        "en": "Name of the Room must not contain any _ or @ ⛔️",
        "fa": "نام اتاق نباید شامل _ یا @ باشد ⛔️",
    }
    INVALID_END_RESERVATION = {
        "en": "This reservation has finished ⛔️",
        "fa": "این رزرو به پایان رسیده ⛔️",
    }
    INVALID_CANCEL_RESERVATION = {
        "en": "This reservation has finished and you can't cancel it ⛔️",
        "fa": "این رزرو پایان یافته و امکان کنسل کردن وجود ندارد ⛔️",
    }
    INVALID_CHECKOUT_RESERVATION = {
        "en": "This reservation has finished and you can't checkout it ⛔️",
        "fa": "این رزرو پایان یافته و امکان ثبت پابان جلسه وجود ندارد ⛔️",
    }
    INVALID_NAME_TAKEN = {
        "en": "This name has already been used. Please choose a different one ⛔️",
        "fa": "این نام قبلاً استفاده شده است. لطفاً نام دیگری انتخاب کنید ⛔️",
    }
    INVALID_NAME = {
        "en": "Your name must be a string and should not contain any digits or symbols ⛔️",
        "fa": "نام شما باید یک متن باشد و نباید شامل عدد یا علامت های خاص باشد ⛔️",
    }
    INVALID_ADMIN = {
        "en": "You are not admin, and you can't access this command ⛔️",
        "fa": "تنها ادمین های بات اجازه دسترسی به این بخش را دارند ⛔️",
    }
    INVALID_CHARGE = {
        "en": "To reserve a continuous reservation, you need to charge your account.\n💰 Please contact the admin to charge your account.",
        "fa": "برای رزرو دوره ای، لازم است اکانت خود را شارژ کنید.\n💰 لطفاً برای شارژ اکانت به ادمین پیام دهید.",
    }
    INSUFFICIENT_CHARGE = {
        "en": "Insufficient charge ⛔️\nThis reservation requires {charge} charges.\nPlease contact the admin to charge your account 💰",
        "fa": "شارژ حساب شما ناکافی است ⛔️\nاین رزرو به {charge} شارژ نیاز دارد.\nلطفاً برای شارژ اکانت به ادمین پیام دهید 💰",
    }
    NAME_TAKEN_ADMIN = {
        "en": "This name has already been used. Please choose a different one ⛔️",
        "fa": "این نام قبلاً استفاده شده است. لطفاً نام دیگری انتخاب کنید ⛔️",
    }
    NAME_INVALID_ADMIN = {
        "en": "Your name must be a string and should not contain any digit or symbol ⛔️",
        "fa": "نام شما باید یک متن باشد و نباید شامل عدد یا نمادهای خاص باشد ⛔️",
    }
    INVALID_ENTERED_CHARGE = {
        "en": "The charge must be integer and should not contain any letter or symbol ⛔️",
        "fa": "مقدار شارژ باید یک عدد باشد و نباید شامل حروف یا نمادهای خاص باشد ⛔️",
    }
    INVALID_WEEK_SELECTION = {
        "en": "You must select the number of weeks, and it cannot be empty ⛔️",
        "fa": "شما باید تعداد هفته ‌ها را انتخاب کنید و این بخش نباید خالی باشد ⛔️",
    }
    INVALID_NONE_WEEKS = {
        "en": "You must select a time that has not been reserved by someone else 🙂",
        "fa": "شما باید زمانی را انتخاب کنید که شخص دیگری آن را رزرو نکرده باشد 🙂",
    }


persian_numerals = {
    "0": "۰",
    "1": "۱",
    "2": "۲",
    "3": "۳",
    "4": "۴",
    "5": "۵",
    "6": "۶",
    "7": "۷",
    "8": "۸",
    "9": "۹",
}
english_numerals = {
    "۰": "0",
    "۱": "1",
    "۲": "2",
    "۳": "3",
    "۴": "4",
    "۵": "5",
    "۶": "6",
    "۷": "7",
    "۸": "8",
    "۹": "9",
}


def get_text(text_key, language):
    return text_key.value[language]


def convert_to_persian_numerals(text):
    for eng, per in persian_numerals.items():
        text = text.replace(eng, per)
    return text


def convert_to_english_numerals(text):
    for per, eng in english_numerals.items():
        text = text.replace(per, eng)
    return text


def change_num_as_lang(txt, user_language):
    if user_language == "fa":
        return convert_to_persian_numerals(txt)
    else:
        return convert_to_english_numerals(txt)


def change_num_as_lang_and_username(txt, user_language):
    txt = txt.split("\n")
    new_txt_list = []
    for line in txt:
        if "@" not in line:
            line = change_num_as_lang(line, user_language)
        new_txt_list.append(line)
    return "\n".join(new_txt_list)
