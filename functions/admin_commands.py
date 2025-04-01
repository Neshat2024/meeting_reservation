from sqlalchemy.exc import SQLAlchemyError
from telebot import types
from telebot.apihelper import ApiTelegramException
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton as btn

from functions.get_functions import future_date
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
    check_text_in_name,
    ONE,
    TWO,
    THREE, check_text_in_charge,
)
from services.language import get_text, BotText, change_num_as_lang, change_num_as_lang_and_username
from services.log import add_log


def process_admin_commands(message, session, bot):
    chat_id = str(message.chat.id)
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
    admins = session.query(Users).filter_by(role="admin").all()
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
    admins = session.query(Users).filter_by(role="admin").all()
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
    msg_id = str(call.message.id)
    user = get_user(call, session)
    txt = get_text(BotText.EDIT_ROOM, user.language)
    rooms = session.query(Rooms).all()
    key = InlineKeyboardMarkup()
    for room in rooms:
        key.add(btn(text=f"{room.name}", callback_data=f"edit_{room.id}"))
    key.add(
        btn(text=get_text(BotText.BACK_BUTTON, user.language), callback_data="backroom")
    )
    try:
        bot.edit_message_text(
            chat_id=int(user.chat_id), message_id=msg_id, reply_markup=key, text=txt
        )
    except ApiTelegramException as e:
        telegram_api_exception("process_edit_room", e)
    except Exception as e:
        add_log(f"Exception in process_edit_room: {e}")


def process_update_specific_room(call, session, bot):
    try:
        room_id = call.data.split("_")[1]
        user = get_user(call, session)
        chat_id, msg_id = int(user.chat_id), str(call.message.id)
        room_name = session.query(Rooms).filter_by(id=room_id).first().name
        set_command_in_wraps(user, session, f"edit_room_{room_id}")
        txt = get_text(BotText.UPDATE_ROOM_NAME, user.language).format(
            room_name=room_name
        )
        bot.edit_message_text(chat_id=chat_id, message_id=msg_id, text=txt)
        bot.register_next_step_handler(call.message, check_room, session, bot)
    except ApiTelegramException as e:
        telegram_api_exception("process_update_specific_room", e)
    except Exception as e:
        add_log(f"Exception in process_update_specific_room: {e}")


def process_delete_room(call, session, bot):
    msg_id = str(call.message.id)
    user = get_user(call, session)
    txt = get_text(BotText.DELETE_ROOM, user.language)
    rooms = session.query(Rooms).all()
    key = InlineKeyboardMarkup()
    for room in rooms:
        key.add(btn(text=f"{room.name}", callback_data=f"delete_{room.id}"))
    key.add(
        btn(text=get_text(BotText.BACK_BUTTON, user.language), callback_data="backroom")
    )
    try:
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
    admins = session.query(Users).filter_by(role="admin").all()
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
    try:
        bot.edit_message_text(chat_id=ch_id, message_id=msg, text=txt, reply_markup=key)
    except ApiTelegramException as e:
        telegram_api_exception("process_view_users", e)
    except Exception as e:
        add_log(f"Exception in process_view_users: {e}")


def process_edit_users_name(call, session, bot):
    user = get_user(call, session)
    ch_id, msg_id = user.chat_id, str(call.message.id)
    txt = get_text(BotText.EDIT_USERS_NAME, user.language)
    key, buttons = InlineKeyboardMarkup(row_width=2), []
    users = session.query(Users).all()
    for user in users:
        buttons.append(btn(text=f"@{user.username}", callback_data=f"e_name_{user.id}"))
        if len(buttons) == 2:
            key.row(*buttons)
            buttons = []
    if buttons:
        key.row(*buttons)
    key.add(
        btn(
            text=get_text(BotText.BACK_BUTTON, user.language), callback_data="back-view"
        )
    )
    bot.edit_message_text(chat_id=ch_id, message_id=msg_id, text=txt, reply_markup=key)


def process_edit_specific_name(call, session, bot):
    db_id = int(call.data.split("_")[2])
    selected_user = session.query(Users).filter_by(id=db_id).first()
    user = get_user(call, session)
    chat_id, msg_id = int(user.chat_id), str(call.message.id)
    txt = get_text(BotText.EDIT_USERS_OLD_NAME, user.language).format(
        username=selected_user.username, name=selected_user.name
    )
    bot.edit_message_text(chat_id=chat_id, message_id=msg_id, text=txt)
    bot.register_next_step_handler(
        call.message, change_name, session, [selected_user, bot]
    )


def change_name(message, session, user_bot):
    try:
        user = get_user(message, session)
        selected_user, bot = user_bot
        text = check_text_in_name(message)
        if text is None:
            txt, key = get_text_key_in_change_name(user, 1)
        elif text:
            name_exists = session.query(Users).filter_by(name=message.text).first()
            if not name_exists:
                update_users_name_in_db(message, session, user_bot)
                txt, key = get_text_key_in_change_name(user, 2, selected_user)
            else:
                txt, key = get_text_key_in_change_name(user, 3, selected_user)
        else:
            txt, key = get_text_key_in_change_name(user, 4, selected_user)
        bot.send_message(chat_id=int(user.chat_id), text=txt, reply_markup=key)
    except SQLAlchemyError as e:
        add_log(f"SQLAlchemyError in change_name: {e}")
    except Exception as e:
        add_log(f"Exception in change_name: {e}")


def get_text_key_in_change_name(user, num, selected_user=None):
    back_txt = get_text(BotText.BACK_BUTTON, user.language)
    retry_txt = get_text(BotText.RETRY, user.language)
    key = InlineKeyboardMarkup()
    if num == ONE:
        txt = get_text(BotText.OPERATION_CANCELED, user.language)
        key.add(btn(text=back_txt, callback_data="back-users-view"))
    elif num == TWO:
        txt = get_text(BotText.NAME_UPDATED, user.language).format(
            username=selected_user.username, new_name=selected_user.name
        )
        key.add(btn(text=back_txt, callback_data="back-view"))
    elif num == THREE:
        txt = get_text(BotText.NAME_TAKEN_ADMIN, user.language)
        key.add(btn(text=retry_txt, callback_data=f"e_name_{selected_user.id}"))
        key.add(btn(text=back_txt, callback_data="back-users-view"))
    else:
        txt = get_text(BotText.NAME_INVALID_ADMIN, user.language)
        key.add(btn(text=retry_txt, callback_data=f"e_name_{selected_user.id}"))
        key.add(btn(text=back_txt, callback_data="back-users-view"))
    return txt, key


def update_users_name_in_db(message, session, user_bot):
    try:
        user = get_user(message, session)
        selected_user, bot = user_bot
        selected_user.name = message.text
        session.commit()
        bot.send_message(
            int(selected_user.chat_id),
            get_text(BotText.YOUR_NAME_UPDATED, selected_user.language).format(
                name=message.text, admin=user.username
            ),
        )
    except SQLAlchemyError as e:
        add_log(f"SQLAlchemyError in add_new_name_in_db: {e}")
    except Exception as e:
        add_log(f"Exception in add_new_name_in_db: {e}")


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


def process_charge_user(call, session, bot):
    user = get_user(call, session)
    ch_id, msg_id = user.chat_id, str(call.message.id)
    txt = get_text(BotText.SELECTION_CHARGE_USER, user.language)
    key, buttons = InlineKeyboardMarkup(row_width=2), []
    users = session.query(Users).all()
    for u in users:
        if u.username:
            buttons.append(btn(text=f"@{u.username}", callback_data=f"ch-name_{u.id}"))
        else:
            buttons.append(btn(text=f"name={u.name}", callback_data=f"ch-name_{u.id}"))
        if len(buttons) == 2:
            key.row(*buttons)
            buttons = []
    if buttons:
        key.row(*buttons)
    bot.edit_message_text(chat_id=ch_id, message_id=msg_id, text=txt, reply_markup=key)


def process_get_charge_for_user(call, session, bot):
    user = get_user(call, session)
    chat_id, msg_id = int(user.chat_id), str(call.message.id)
    db_id = call.data.split("_")[1]
    s_user = session.query(Users).filter_by(id=db_id).first()
    if s_user.username not in ["", None, 0]:
        uname = s_user.username
        t = get_text(BotText.GET_CHARGE_USERNAME, user.language).format(username=uname, charge=s_user.charge)
    else:
        name = s_user.name
        t = get_text(BotText.GET_CHARGE_NAME, user.language).format(username=name, charge=s_user.charge)
    bot.edit_message_text(chat_id=chat_id, message_id=msg_id, text=t)
    bot.register_next_step_handler(call.message, get_charge, session, [s_user, bot])


def get_charge(message, session, user_bot):
    try:
        user = get_user(message, session)
        ch_id = int(user.chat_id)
        selected_user, bot = user_bot
        text = check_text_in_charge(message)
        key = InlineKeyboardMarkup()
        back_txt = get_text(BotText.BACK_BUTTON, user.language)
        if text is None:
            txt = get_text(BotText.OPERATION_CANCELED, user.language)
            key.add(btn(text=back_txt, callback_data="back-charge-user"))
            bot.send_message(chat_id=ch_id, text=txt, reply_markup=key)
        elif text:
            charge = int(change_num_as_lang(message.text, "en"))
            new_charge = selected_user.charge + charge
            selected_user.charge = new_charge
            session.commit()
            if selected_user.username not in ["", None, 0]:
                name = f"@{selected_user.username}"
            else:
                name = selected_user.name
            manager_msg = get_text(BotText.MANAGER_CHARGE_MESSAGE, user.language).format(user=name ,charge=charge, new_charge=new_charge)
            manager_msg = change_num_as_lang_and_username(manager_msg, user.language)
            ok_text = get_text(BotText.OK_REMINDER_BUTTON, user.language)
            key.add(btn(text=ok_text, callback_data="backroom"))
            bot.send_message(chat_id=ch_id, text=manager_msg, reply_markup=key)
            user_msg = get_text(BotText.USER_CHARGE_MESSAGE, selected_user.language).format(charge=charge, new_charge=new_charge)
            user_msg = change_num_as_lang(user_msg, selected_user.language)
            try:
                bot.send_message(selected_user.chat_id, user_msg)
            except Exception as e:
                txt = get_text(BotText.MESSAGE_NOT_SENT, user.language).format(user=selected_user.name, error=e)
                bot.send_message(ch_id, txt)
        else:
            txt = get_text(BotText.INVALID_ENTERED_CHARGE, user.language)
            retry_txt = get_text(BotText.RETRY, user.language)
            key.add(btn(text=retry_txt, callback_data=f"ch-name_{selected_user.id}"))
            bot.send_message(chat_id=int(user.chat_id), text=txt, reply_markup=key)
    except SQLAlchemyError as e:
        add_log(f"SQLAlchemyError in get_charge: {e}")
    except Exception as e:
        add_log(f"Exception in get_charge: {e}")
