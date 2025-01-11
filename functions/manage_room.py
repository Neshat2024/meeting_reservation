from sqlalchemy.exc import SQLAlchemyError
from telebot.apihelper import ApiTelegramException
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

from models.reservations import Reservations
from models.rooms import Rooms
from models.users import Users
from services.config import get_user, send_cancel_message, telegram_api_exception, set_command_in_wraps
from services.log import add_log


def process_manage_room(message, session, bot):
    chat_id = str(message.chat.id)
    key = InlineKeyboardMarkup()
    key.add(InlineKeyboardButton(text="➕ Add Room", callback_data="add_room"))
    rooms = session.query(Rooms).all()
    if rooms:
        txt = "🚪 These Meeting Rooms has been added before:\n"
        for room in rooms:
            txt += f"{room.name}\n"
        key.add(InlineKeyboardButton(text="✏️ Edit Rooms", callback_data="editroom"))
        key.add(InlineKeyboardButton(text="🗑 Delete Rooms", callback_data="deleteroom"))
    else:
        txt = "No Meeting Room has been defined yet 🙁"
    bot.send_message(chat_id, txt, reply_markup=key)


def process_add_room(message, session, bot):
    chat_id = str(message.chat.id)
    bot.send_message(
        chat_id,
        "🚪 Enter the Name of the Room:\n\nIf you want to cancel the operation tap on /cancel",
    )
    bot.register_next_step_handler(message, check_room, session, bot)


def check_room(message, session, bot):
    try:
        chat_id = str(message.chat.id)
        user = get_user(message, session)
        text = check_text_in_room(message, session)
        if text is None:
            bot.send_message(chat_id, "Operation cancelled!")
            return
        elif text and user.command.startswith("edit_room"):
            update_room_in_db(message, session, bot)
            bot.send_message(chat_id, "Name of the Room updated successfully 👍🏻")
        elif text:
            add_room_in_db(message, session)
            bot.send_message(chat_id, "Name of the Room submitted successfully 👍🏻")
        else:
            txt = "Name of the Room must not contain any _ or @ ⛔️"
            bot.send_message(chat_id, txt)
            process_add_room(message, session, bot)
    except SQLAlchemyError as e:
        add_log(f"SQLAlchemyError in check_room: {e}")
    except Exception as e:
        add_log(f"Exception in check_room: {e}")


def check_text_in_room(message, session):
    if send_cancel_message(message, session):
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
        txt_for_admins = f"Admin with these info updated the Room with the name «{old_name}» to {room.name} 🗑\nName: {user.name}\n✍🏻 TG Username: @{user.username}"
        send_message_to_admins(txt_for_admins, session, bot)
        send_edit_message_to_reserved_users([room, old_name], session, bot)
    except SQLAlchemyError as e:
        add_log(f"SQLAlchemyError in add_room_in_db: {e}")
    except Exception as e:
        add_log(f"Exception in add_room_in_db: {e}")


def add_room_in_db(message, session):
    try:
        user = get_user(message, session)
        room = Rooms(name=message.text, user_id=user.id)
        session.add(room)
        session.commit()
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
        except Exception as e:
            pass


def send_edit_message_to_reserved_users(room_old, session, bot):
    room, old_name = room_old[0], room_old[1]
    txt = f"Name of «{old_name}» Room updated to «{room.name}» ✏️"
    reserved_rooms = session.query(Reservations).filter_by(room_id=str(room.id)).all()
    users = [reserved_room.user_id.chat_id for reserved_room in reserved_rooms]
    for chat_id in users:
        try:
            bot.send_message(chat_id, txt)
        except Exception as e:
            pass


def process_update_room(call, session, bot):
    chat_id, msg_id = str(call.message.chat.id), str(call.message.id)
    txt = "✏️ Select the Room which you want to edit:"
    rooms = session.query(Rooms).all()
    key = InlineKeyboardMarkup()
    for room in rooms:
        key.add(InlineKeyboardButton(text=f"{room.name}", callback_data=f"edit_{room.id}"))
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
        key.add(InlineKeyboardButton(text=f"{room.name}", callback_data=f"delete_{room.id}"))
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
            txt = f"The Room with the name «{room.name}» deleted successfully 🗑"
            bot.edit_message_text(chat_id=chat_id, message_id=msg_id, text=txt)
            txt_for_admins = f"Admin with these info deleted «{room.name}» Room 🗑\nName: {user.name}\n✍🏻 TG Username: @{user.username}"
            send_message_to_admins(txt_for_admins, session, bot)
            send_delete_message_to_reserved_users(room, session, bot)
            session.delete(room)
            session.commit()
    except SQLAlchemyError as e:
        add_log(f"SQLAlchemyError in process_delete_specific_room: {e}")
    except Exception as e:
        add_log(f"Exception in process_delete_specific_room: {e}")


def send_delete_message_to_reserved_users(room, session, bot):
    txt = f"The Room with the name «{room.name}» has been deleted 🗑\nNow you can reserve a new time for your meeting by tapping on /reservation"
    reserved_rooms = session.query(Reservations).filter_by(room_id=str(room.id)).all()
    users = [reserved_room.user_id.chat_id for reserved_room in reserved_rooms]
    for chat_id in users:
        try:
            bot.send_message(chat_id, txt)
        except Exception as e:
            pass
