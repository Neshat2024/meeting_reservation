from sqlalchemy.exc import SQLAlchemyError
from telebot import types
from telebot.apihelper import ApiTelegramException
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton as btn

from functions.get_functions import future_date
from models.reservations import Reservations
from models.rooms import Rooms
from models.users import Users
from services.config import get_user, send_cancel_message, telegram_api_exception, set_command_in_wraps, BACK_ROOM, \
    change_command_to_none, CONFIRMED, check_text_in_name, ONE, TWO, THREE
from services.log import add_log


def process_admin_commands(message, session, bot):
    chat_id = str(message.chat.id)
    txt, key = get_text_key_in_admin_commands(session)
    user = session.query(Users).filter_by(chat_id=chat_id).first()
    if user.command == BACK_ROOM:
        msg_id = message.id
        bot.edit_message_text(chat_id=chat_id, message_id=msg_id, text=txt, reply_markup=key)
        change_command_to_none(user, session)
    else:
        bot.send_message(chat_id=chat_id, text=txt, reply_markup=key)


def get_text_key_in_admin_commands(session):
    key = InlineKeyboardMarkup()
    key.add(btn(text="➕ Add Room", callback_data="add_room"))
    rooms = session.query(Rooms).all()
    if rooms:
        txt = "🚪 Rooms:\n"
        for room in rooms:
            txt += f"{room.name}\n"
        key.add(btn(text="✏️ Edit Rooms", callback_data="editroom"))
        key.add(btn(text="🗑 Delete Rooms", callback_data="deleteroom"))
    else:
        txt = "No meeting room has been added yet 🙁"
    key.add(btn(text="🔍 View All Users", callback_data="view_users"))
    return txt, key


def process_add_room(call_message, session, bot):
    txt = "🚪 Enter the Name of the Room:\n\nIf you want to cancel the operation tap on /cancel"
    message = None
    if isinstance(call_message, types.Message):
        message = call_message
        chat_id = str(message.chat.id)
        bot.send_message(chat_id, txt)
    elif isinstance(call_message, types.CallbackQuery):
        message = call_message.message
        chat_id = str(call_message.message.chat.id)
        msg_id = call_message.message.id
        key = InlineKeyboardMarkup()
        bot.edit_message_text(chat_id=chat_id, message_id=msg_id, text=txt, reply_markup=key)
    bot.register_next_step_handler(message, check_room, session, bot)


def check_room(message, session, bot):
    try:
        chat_id = str(message.chat.id)
        user = get_user(message, session)
        text = check_text_in_room(message)
        if text is None:
            change_command_to_none(user, session)
            new_txt = "Operation cancelled!\n"
        elif text and user.command and user.command.startswith("edit_room"):
            update_room_in_db(message, session, bot)
            change_command_to_none(user, session)
            new_txt = "Name of the Room updated successfully 👍🏻\n"
        elif text:
            add_room_in_db(message, session, bot)
            new_txt = "Name of the Room submitted successfully 👍🏻\n"
        else:
            txt = "Name of the Room must not contain any _ or @ ⛔️"
            bot.send_message(chat_id, txt)
            return process_add_room(message, session, bot)
        txt, key = get_text_key_in_admin_commands(session)
        bot.send_message(chat_id=chat_id, text=new_txt + txt, reply_markup=key)
    except SQLAlchemyError as e:
        add_log(f"SQLAlchemyError in check_room: {e}")
    except Exception as e:
        add_log(f"Exception in check_room: {e}")


def check_text_in_room(message):
    if send_cancel_message(message):
        return
    elif contains_no_underscore_or_at_sign(message.text):
        return True
    return False


def update_room_in_db(message, session, bot):
    try:
        user = get_user(message, session)
        room_id = user.command.split("_")[2]
        room = session.query(Rooms).filter_by(id=room_id).first()
        old_name = room.name
        room.name = message.text
        session.commit()
        txt_for_admins = f"🔄 This admin updated «{old_name}» Room to «{room.name}»\n👤 Name: {user.name}\n✍🏻 TG Username: @{user.username}"
        send_message_to_admins(txt_for_admins, session, bot)
        send_edit_message_to_reserved_users([room, old_name], session, bot)
    except SQLAlchemyError as e:
        add_log(f"SQLAlchemyError in update_room_in_db: {e}")
    except Exception as e:
        add_log(f"Exception in update_room_in_db: {e}")


def add_room_in_db(message, session, bot):
    try:
        user = get_user(message, session)
        room = Rooms(name=message.text, user_id=user.id)
        session.add(room)
        session.commit()
        txt_for_admins = f"➕ This admin added «{message.text}» Room.\n👤 Name: {user.name}\n✍🏻 TG Username: @{user.username}"
        send_message_to_admins(txt_for_admins, session, bot)
    except SQLAlchemyError as e:
        add_log(f"SQLAlchemyError in add_room_in_db: {e}")
    except Exception as e:
        add_log(f"Exception in add_room_in_db: {e}")


def contains_no_underscore_or_at_sign(text):
    if "_" in text or "@" in text:
        return False
    return True


def send_message_to_admins(txt, session, bot):
    admins = session.query(Users).filter_by(role="admin").all()
    main_admin = txt.split("@")[1]
    for admin in admins:
        try:
            if admin.username != main_admin:
                bot.send_message(admin.chat_id, txt)
        except:
            pass


def send_edit_message_to_reserved_users(room_old, session, bot):
    room, old_name = room_old[0], room_old[1]
    txt = f"🔄 Name of «{old_name}» Room updated to «{room.name}»"
    reserved_rooms = session.query(Reservations).filter_by(room_id=str(room.id)).all()
    users = [reserved_room.main_user.chat_id for reserved_room in reserved_rooms]
    users = list(set(users))
    for chat_id in users:
        try:
            bot.send_message(chat_id, txt)
        except:
            pass


def process_update_room(call, session, bot):
    chat_id, msg_id = str(call.message.chat.id), str(call.message.id)
    txt = "✏️ Select the Room which you want to edit:"
    rooms = session.query(Rooms).all()
    key = InlineKeyboardMarkup()
    for room in rooms:
        key.add(btn(text=f"{room.name}", callback_data=f"edit_{room.id}"))
    key.add(btn(text="⬅️ Back", callback_data="backroom"))
    try:
        bot.edit_message_text(chat_id=chat_id, message_id=msg_id, reply_markup=key, text=txt)
    except ApiTelegramException as e:
        telegram_api_exception("process_edit_room", e)
    except Exception as e:
        add_log(f"Exception in process_edit_room: {e}")


def process_update_specific_room(call, session, bot):
    try:
        chat_id, msg_id = str(call.message.chat.id), str(call.message.id)
        room_id = call.data.split("_")[1]
        user = get_user(call, session)
        room_name = session.query(Rooms).filter_by(id=room_id).first().name
        set_command_in_wraps(user, session, f"edit_room_{room_id}")
        txt = f"🚪 Enter the new Name for «{room_name}»:\n\nIf you want to cancel the operation tap on /cancel"
        bot.edit_message_text(chat_id=chat_id, message_id=msg_id, text=txt)
        bot.register_next_step_handler(call.message, check_room, session, bot)
    except ApiTelegramException as e:
        telegram_api_exception("process_update_specific_room", e)
    except Exception as e:
        add_log(f"Exception in process_update_specific_room: {e}")


def process_delete_room(call, session, bot):
    chat_id, msg_id = str(call.message.chat.id), str(call.message.id)
    txt = "🗑 Select the Room which you want to delete:"
    rooms = session.query(Rooms).all()
    key = InlineKeyboardMarkup()
    for room in rooms:
        key.add(btn(text=f"{room.name}", callback_data=f"delete_{room.id}"))
    key.add(btn(text="⬅️ Back", callback_data="backroom"))
    try:
        bot.edit_message_text(chat_id=chat_id, message_id=msg_id, reply_markup=key, text=txt)
    except ApiTelegramException as e:
        telegram_api_exception("process_delete_room", e)
    except Exception as e:
        add_log(f"Exception in process_delete_room: {e}")


def process_delete_specific_room(call, session, bot):
    chat_id, msg_id = str(call.message.chat.id), str(call.message.id)
    user = get_user(call, session)
    room_id = call.data.split("_")[1]
    room = session.query(Rooms).filter_by(id=room_id).first()
    try:
        if room:
            session.delete(room)
            session.commit()
            txt, key = get_text_key_in_admin_commands(session)
            txt = f"The Room with the name «{room.name}» deleted successfully 🗑\n" + txt
            bot.edit_message_text(chat_id=chat_id, message_id=msg_id, text=txt, reply_markup=key)
            txt_for_admins = f"🗑 This admin deleted «{room.name}» Room.\n👤 Name: {user.name}\n✍🏻 TG Username: @{user.username}"
            send_message_to_admins(txt_for_admins, session, bot)
            send_delete_message_to_reserved_users(room, session, bot)
    except SQLAlchemyError as e:
        add_log(f"SQLAlchemyError in process_delete_specific_room: {e}")
    except Exception as e:
        add_log(f"Exception in process_delete_specific_room: {e}")


def send_delete_message_to_reserved_users(room, session, bot):
    txt = f"🗑 The Room with the name «{room.name}» has been deleted.\nUnfortunately your reservation at this room canceled 🙏🏻\n\nIf you want to reserve a new room for your meeting tap on /reservation"
    reserved_times = session.query(Reservations).filter_by(room_id=str(room.id)).all()
    for reserved_time in reserved_times:
        if reserved_time.status != CONFIRMED:
            session.delete(reserved_time)
            session.commit()
    users = [reserved_room.main_user.chat_id for reserved_room in reserved_times]
    users = list(set(users))
    past_reserves = [reserve for reserve in reserved_times if not future_date(reserve)]
    for reserved_time in past_reserves:
        reserved_time.room_id = room.name
        session.commit()
    future_reserves = [reserve for reserve in reserved_times if future_date(reserve)]
    for reserved_time in future_reserves:
        session.delete(reserved_time)
        session.commit()
    for chat_id in users:
        try:
            bot.send_message(chat_id, txt)
        except:
            pass


def process_view_users(call, session, bot):
    chat_id, msg_id = call.message.chat.id, call.message.id
    users = session.query(Users).all()
    txt = "👥 Users:\nName | TG Username\n\n"
    for user in users:
        if user.role:
            txt += f"*{user.name} 👉🏻 @{user.username}\n"
        else:
            txt += f"{user.name} 👉🏻 @{user.username}\n"
    txt += "\n(* before user's name means that he is admin)"
    key = InlineKeyboardMarkup()
    key.add(btn(text="✏️ Edit Name", callback_data="editname"))
    key.add(btn(text="⬅️ Back", callback_data="backroom"))
    bot.edit_message_text(chat_id=chat_id, message_id=msg_id, text=txt, reply_markup=key)


def process_edit_users_name(call, session, bot):
    chat_id, msg_id = call.message.chat.id, call.message.id
    users = session.query(Users).all()
    txt = "✏️ Please select the user whose name you want to edit:"
    key, buttons = InlineKeyboardMarkup(row_width=2), []
    for user in users:
        buttons.append(btn(text=user.name, callback_data=f"e_name_{user.id}"))
        if len(buttons) == 2:
            key.row(*buttons)
            buttons = []
    if buttons:
        key.row(*buttons)
    key.add(btn(text="⬅️ Back", callback_data="back-view"))
    bot.edit_message_text(chat_id=chat_id, message_id=msg_id, text=txt, reply_markup=key)


def process_edit_specific_name(call, session, bot):
    db_id = int(call.data.split("_")[2])
    selected_user = session.query(Users).filter_by(id=db_id).first()
    chat_id, msg_id = call.message.chat.id, call.message.id
    txt = f"Enter the New Name for @{selected_user.username}:\n\nIf you want to cancel the operation tap on /cancel"
    bot.edit_message_text(chat_id=chat_id, message_id=msg_id, text=txt)
    bot.register_next_step_handler(call.message, change_name, session, [selected_user, bot])


def change_name(message, session, user_bot):
    try:
        selected_user, bot = user_bot
        chat_id = message.chat.id
        text = check_text_in_name(message)
        if text is None:
            txt, key = get_text_key_in_change_name(1)
        elif text:
            name_exists = session.query(Users).filter_by(name=message.text).first()
            if not name_exists:
                add_new_name_in_db(selected_user, message, session)
                txt, key = get_text_key_in_change_name(2, selected_user)
            else:
                txt, key = get_text_key_in_change_name(3, selected_user)
        else:
            txt, key = get_text_key_in_change_name(4, selected_user)
        bot.send_message(chat_id=chat_id, text=txt, reply_markup=key)
    except SQLAlchemyError as e:
        add_log(f"SQLAlchemyError in change_name: {e}")
    except Exception as e:
        add_log(f"Exception in change_name: {e}")


def get_text_key_in_change_name(num, selected_user=None):
    key = InlineKeyboardMarkup()
    if num == ONE:
        txt = "Operation cancelled!"
        key.add(btn(text="⬅️ Back", callback_data="back-users-view"))
    elif num == TWO:
        txt = f"🔄 The name for @{selected_user.username} updated to «{selected_user.name}» successfully 👍🏻"
        key.add(btn(text="⬅️ Back", callback_data="back-view"))
    elif num == THREE:
        txt = "This name has already been used. Please choose a different one ⛔️"
        key.add(btn(text="🆕 Retry", callback_data=f"e_name_{selected_user.id}"))
        key.add(btn(text="⬅️ Back", callback_data="back-users-view"))
    else:
        txt = "Your name must be a string and should not contain any digits or symbols ⛔️"
        key.add(btn(text="🆕 Retry", callback_data=f"e_name_{selected_user.id}"))
        key.add(btn(text="⬅️ Back", callback_data="back-users-view"))
    return txt, key


def add_new_name_in_db(selected_user, message, session):
    try:
        selected_user.name = message.text
        session.commit()
    except SQLAlchemyError as e:
        add_log(f"SQLAlchemyError in add_new_name_in_db: {e}")
    except Exception as e:
        add_log(f"Exception in add_new_name_in_db: {e}")


def process_back_room(message, session, bot):
    try:
        chat_id = str(message.chat.id)
        user = session.query(Users).filter_by(chat_id=chat_id).first()
        user.command = BACK_ROOM
        session.commit()
        return process_admin_commands(message, session, bot)
    except SQLAlchemyError as e:
        add_log(f"SQLAlchemyError in process_back_room: {e}")
    except Exception as e:
        add_log(f"Exception in process_back_room: {e}")
