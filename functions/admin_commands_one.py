from sqlalchemy import or_
from sqlalchemy.exc import SQLAlchemyError
from telebot import types
from telebot.apihelper import ApiTelegramException
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton as btn

from functions.get_functions_reserves import future_date
from models.reservations import Reservations
from models.rooms import Rooms
from models.users import Users
from services.config import (
    get_user,
    send_cancel_message,
    telegram_api_exception,
    set_command_in_wraps,
    BACK_ROOM,
    change_command_to_none,
    CONFIRMED,
)
from services.language import (
    get_text,
    BotText,
)
from services.log import add_log


def process_admin_commands(message, session, bot):
    chat_id = str(message.chat.id)
    try:
        user = get_user(message, session)
        txt, key = get_text_key_in_admin_commands(user, session)
        if user.command == BACK_ROOM:
            msg_id = message.id
            bot.edit_message_text(
                chat_id=chat_id, message_id=msg_id, text=txt, reply_markup=key
            )
            change_command_to_none(user, session)
        else:
            bot.send_message(chat_id=chat_id, text=txt, reply_markup=key)
    except Exception as e:
        add_log(f"Exception in process_admin_commands: {e}")


def get_text_key_in_admin_commands(user, session):
    key = InlineKeyboardMarkup()
    txt_add_room = get_text(BotText.ADD_ROOM_BUTTON, user.language)
    key.add(btn(text=txt_add_room, callback_data="add_room"))
    rooms = session.query(Rooms).all()
    if rooms:
        txt = get_text(BotText.ROOMS, user.language)
        for room in rooms:
            txt += f"{room.name}\n"
        txt_edit_room = get_text(BotText.EDIT_ROOM_ADMIN, user.language)
        key.add(btn(text=txt_edit_room, callback_data="editroom"))
        txt_delete_room = get_text(BotText.DELETE_ROOM_ADMIN, user.language)
        key.add(btn(text=txt_delete_room, callback_data="deleteroom"))
    else:
        txt = get_text(BotText.NO_MEETING_ROOMS, user.language)
    txt_view_users = get_text(BotText.VIEW_USERS_BUTTON, user.language)
    key.add(btn(text=txt_view_users, callback_data="view_users"))
    if user.role == "manager":
        txt_charge_user = get_text(BotText.CHARGE_USER, user.language)
        key.add(btn(text=txt_charge_user, callback_data="charge_user"))
    return txt, key


def process_add_room(call_message, session, bot):
    user = get_user(call_message, session)
    message = None
    if isinstance(call_message, types.Message):
        message = call_message
        txt = get_text(BotText.ADD_ROOM, user.language)
        bot.send_message(int(user.chat_id), txt)
    elif isinstance(call_message, types.CallbackQuery):
        message = call_message.message
        msg_id = call_message.message.id
        txt = get_text(BotText.ADD_ROOM, user.language)
        bot.edit_message_text(chat_id=int(user.chat_id), message_id=msg_id, text=txt)
    bot.register_next_step_handler(message, check_room, session, bot)


def check_room(message, session, bot):
    try:
        chat_id = str(message.chat.id)
        user = get_user(message, session)
        text = check_text_in_room(message)
        if text is None:
            change_command_to_none(user, session)
            new_txt = get_text(BotText.OPERATION_CANCELED, user.language) + "\n"
        elif text and user.command and user.command.startswith("edit_room"):
            update_room_in_db(message, session, bot)
            change_command_to_none(user, session)
            new_txt = get_text(BotText.ROOM_UPDATED, user.language)
        elif text:
            add_room_in_db(message, session, bot)
            new_txt = get_text(BotText.ROOM_ADDED, user.language)
        else:
            txt = get_text(BotText.INVALID_ROOM_NAME, user.language)
            bot.send_message(chat_id, txt)
            return process_add_room(message, session, bot)
        txt, key = get_text_key_in_admin_commands(user, session)
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
        send_update_message_to_admins([user, old_name, room.name], session, bot)
        send_edit_message_to_reserved_users([user, room, old_name], session, bot)
    except SQLAlchemyError as e:
        add_log(f"SQLAlchemyError in update_room_in_db: {e}")
    except Exception as e:
        add_log(f"Exception in update_room_in_db: {e}")


def send_update_message_to_admins(user_old_name_room, session, bot):
    user, old_name, room = user_old_name_room
    admins = (
        session.query(Users)
        .filter(or_(Users.role == "admin", Users.role == "manager"))
        .all()
    )
    main_admin = user.username
    for admin in admins:
        try:
            if admin.username != main_admin:
                txt = get_text(BotText.ADMINS_TEXT_UPDATE, admin.language).format(
                    old_name=old_name,
                    room_name=room,
                    name=user.name,
                    username=user.username,
                )
                bot.send_message(admin.chat_id, txt)
        except:
            pass


def add_room_in_db(message, session, bot):
    try:
        user = get_user(message, session)
        room = Rooms(name=message.text, user_id=user.id)
        session.add(room)
        session.commit()
        send_add_message_to_admins(message, session, bot)
    except SQLAlchemyError as e:
        add_log(f"SQLAlchemyError in add_room_in_db: {e}")
    except Exception as e:
        add_log(f"Exception in add_room_in_db: {e}")


def send_add_message_to_admins(message, session, bot):
    user = get_user(message, session)
    admins = (
        session.query(Users)
        .filter(or_(Users.role == "admin", Users.role == "manager"))
        .all()
    )
    main_admin = user.username
    for admin in admins:
        try:
            if admin.username != main_admin:
                txt = get_text(BotText.ADMINS_TEXT_ADD, admin.language).format(
                    room_name=message.text, name=user.name, username=user.username
                )
                bot.send_message(admin.chat_id, txt)
        except:
            pass


def contains_no_underscore_or_at_sign(text):
    if "_" in text or "@" in text:
        return False
    return True


def send_edit_message_to_reserved_users(user_room_old, session, bot):
    user, room, old_name = user_room_old
    reserved_rooms = session.query(Reservations).filter_by(room_id=str(room.id)).all()
    users = [reserved_room.main_user for reserved_room in reserved_rooms]
    users = list(set(users))
    for user in users:
        try:
            txt = get_text(BotText.USERS_TEXT_UPDATE, user.language).format(
                old_name=old_name, room_name=room.name
            )
            bot.send_message(int(user.chat_id), txt)
        except:
            pass


def process_update_room(call, session, bot):
    try:
        msg_id = str(call.message.id)
        user = get_user(call, session)
        txt = get_text(BotText.EDIT_ROOM, user.language)
        rooms = session.query(Rooms).all()
        key = InlineKeyboardMarkup()
        for room in rooms:
            key.add(btn(text=f"{room.name}", callback_data=f"edit_{room.id}"))
        key.add(
            btn(
                text=get_text(BotText.BACK_BUTTON, user.language),
                callback_data="backroom",
            )
        )
        bot.edit_message_text(
            chat_id=int(user.chat_id), message_id=msg_id, reply_markup=key, text=txt
        )
    except ApiTelegramException as e:
        telegram_api_exception("process_update_room", e)
    except Exception as e:
        add_log(f"Exception in process_update_room: {e}")


def process_update_specific_room(call, session, bot):
    room_id = call.data.split("_")[1]
    user = get_user(call, session)
    chat_id, msg_id = int(user.chat_id), str(call.message.id)
    room_name = session.query(Rooms).filter_by(id=room_id).first().name
    set_command_in_wraps(user, session, f"edit_room_{room_id}")
    txt = get_text(BotText.UPDATE_ROOM_NAME, user.language).format(room_name=room_name)
    bot.edit_message_text(chat_id=chat_id, message_id=msg_id, text=txt)
    bot.register_next_step_handler(call.message, check_room, session, bot)


def process_delete_room(call, session, bot):
    try:
        msg_id = str(call.message.id)
        user = get_user(call, session)
        txt = get_text(BotText.DELETE_ROOM, user.language)
        rooms = session.query(Rooms).all()
        key = InlineKeyboardMarkup()
        for room in rooms:
            key.add(btn(text=f"{room.name}", callback_data=f"delete_{room.id}"))
        key.add(
            btn(
                text=get_text(BotText.BACK_BUTTON, user.language),
                callback_data="backroom",
            )
        )
        bot.edit_message_text(
            chat_id=int(user.chat_id), message_id=msg_id, reply_markup=key, text=txt
        )
    except ApiTelegramException as e:
        telegram_api_exception("process_delete_room", e)
    except Exception as e:
        add_log(f"Exception in process_delete_room: {e}")


def process_delete_specific_room(call, session, bot):
    msg_id = str(call.message.id)
    user = get_user(call, session)
    room_id = call.data.split("_")[1]
    room = session.query(Rooms).filter_by(id=room_id).first()
    try:
        if room:
            session.delete(room)
            session.commit()
            txt, key = get_text_key_in_admin_commands(user, session)
            txt = (
                get_text(BotText.ROOM_DELETED, user.language).format(
                    room_name=room.name
                )
                + txt
            )
            bot.edit_message_text(
                chat_id=int(user.chat_id), message_id=msg_id, text=txt, reply_markup=key
            )
            send_delete_message_to_admins([user, room], session, bot)
            send_delete_message_to_reserved_users(room, session, bot)
    except SQLAlchemyError as e:
        add_log(f"SQLAlchemyError in process_delete_specific_room: {e}")
    except Exception as e:
        add_log(f"Exception in process_delete_specific_room: {e}")


def send_delete_message_to_admins(user_room, session, bot):
    user, room = user_room
    admins = (
        session.query(Users)
        .filter(or_(Users.role == "admin", Users.role == "manager"))
        .all()
    )
    main_admin = user.username
    for admin in admins:
        try:
            if admin.username != main_admin:
                txt = get_text(BotText.ADMINS_TEXT_DELETE, admin.language).format(
                    room_name=room.name, name=user.name, username=user.username
                )
                bot.send_message(admin.chat_id, txt)
        except:
            pass


def send_delete_message_to_reserved_users(room, session, bot):
    reserved_times = session.query(Reservations).filter_by(room_id=str(room.id)).all()
    for reserved_time in reserved_times:
        if reserved_time.status != CONFIRMED:
            session.delete(reserved_time)
            session.commit()
    users = [reserved_room.main_user for reserved_room in reserved_times]
    users = list(set(users))
    past_reserves = [reserve for reserve in reserved_times if not future_date(reserve)]
    for reserved_time in past_reserves:
        reserved_time.room_id = room.name
        session.commit()
    future_reserves = [reserve for reserve in reserved_times if future_date(reserve)]
    for reserved_time in future_reserves:
        session.delete(reserved_time)
        session.commit()
    for user in users:
        try:
            txt = get_text(BotText.USERS_ROOM_DELETED, user.language).format(
                room_name=room.name
            )
            bot.send_message(int(user.chat_id), txt)
        except:
            pass


def process_view_users(call, session, bot):
    try:
        user = get_user(call, session)
        ch_id, msg = user.chat_id, str(call.message.id)
        txt = get_text(BotText.VIEW_USERS_ONE, user.language)
        for u in session.query(Users).all():
            username = f"@{u.username}" if u.username else str(u.username)
            prefix = "*" if u.role else ""
            txt += f"{prefix}{u.name} 👉🏻 {username}\n"
        txt += get_text(BotText.VIEW_USERS_TWO, user.language)
        key = InlineKeyboardMarkup()
        texts = [(BotText.EDIT_NAME, "editname"), (BotText.BACK_BUTTON, "backroom")]
        for text_key, callback in texts:
            key.add(btn(text=get_text(text_key, user.language), callback_data=callback))
        bot.edit_message_text(chat_id=ch_id, message_id=msg, text=txt, reply_markup=key)
    except ApiTelegramException as e:
        telegram_api_exception("process_view_users", e)
    except Exception as e:
        add_log(f"Exception in process_view_users: {e}")


def process_back_room(message, session, bot):
    try:
        user = get_user(message, session)
        user.command = BACK_ROOM
        session.commit()
        return process_admin_commands(message, session, bot)
    except SQLAlchemyError as e:
        add_log(f"SQLAlchemyError in process_back_room: {e}")
    except Exception as e:
        add_log(f"Exception in process_back_room: {e}")
