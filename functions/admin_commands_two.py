from sqlalchemy.exc import SQLAlchemyError
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton as Btn

from functions.admin_commands_one import get_text_key_in_admin_commands
from functions.get_functions_cr import get_users_in_buttons
from models.reservations import Reservations
from models.users import Users
from services.config import (
    get_user,
    check_text_in_name,
    ONE,
    TWO,
    THREE,
    check_text_in_charge,
)
from services.language import (
    get_text,
    BotText,
    change_num_as_lang,
    change_num_as_lang_and_username,
)
from services.log import add_log


def process_edit_users_name(call, session, bot):
    try:
        user = get_user(call, session)
        ch_id, msg = user.chat_id, str(call.message.id)
        txt = get_text(BotText.EDIT_USERS_NAME, user.language)
        key = get_users_in_buttons(user, session, "e_name")
        t = get_text(BotText.BACK_BUTTON, user.language)
        key.add(Btn(text=t, callback_data="back-view"))
        bot.edit_message_text(chat_id=ch_id, message_id=msg, text=txt, reply_markup=key)
    except Exception as e:
        add_log(f"Exception in process_edit_users_name: {e}")


def process_edit_specific_name(call, session, bot):
    db_id = int(call.data.split("_")[2])
    s_user = session.query(Users).filter_by(id=db_id).first()
    user = get_user(call, session)
    chat_id, msg_id = int(user.chat_id), str(call.message.id)
    if s_user.username:
        txt = get_text(BotText.EDIT_USERS_OLD_NAME_USERNAME, user.language).format(username=s_user.username, name=s_user.name)
    elif s_user.name:
        txt = get_text(BotText.EDIT_USERS_OLD_NAME, user.language).format(name=s_user.name)
    else:
        txt = get_text(BotText.EDIT_USERS_OLD_NAME_CHAT_ID, user.language).format(chat_id=s_user.chat_id)
    bot.edit_message_text(chat_id=chat_id, message_id=msg_id, text=txt)
    bot.register_next_step_handler(
        call.message, change_name, session, [s_user, bot]
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
        bot.send_message(user.chat_id, txt, reply_markup=key)
    except SQLAlchemyError as e:
        add_log(f"SQLAlchemyError in change_name: {e}")
    except Exception as e:
        add_log(f"Exception in change_name: {e}")


def get_text_key_in_change_name(user, num, s_user=None):
    back_txt = get_text(BotText.BACK_BUTTON, user.language)
    retry_txt = get_text(BotText.RETRY, user.language)
    key = InlineKeyboardMarkup()
    if num == ONE:
        txt = get_text(BotText.OPERATION_CANCELED, user.language)
        key.add(Btn(text=back_txt, callback_data="back-users-view"))
    elif num == TWO:
        if s_user.username:
            txt = get_text(BotText.NAME_UPDATED_USERNAME, user.language).format(
                username=s_user.username, new_name=s_user.name
            )
        else:
            txt = get_text(BotText.NAME_UPDATED_CHAT_ID, user.language).format(
                chat_id=s_user.chat_id, name=s_user.name
            )
        key.add(Btn(text=back_txt, callback_data="back-view"))
    elif num == THREE:
        txt = get_text(BotText.NAME_TAKEN_ADMIN, user.language)
        key.add(Btn(text=retry_txt, callback_data=f"e_name_{s_user.id}"))
        key.add(Btn(text=back_txt, callback_data="back-users-view"))
    else:
        txt = get_text(BotText.NAME_INVALID_ADMIN, user.language)
        key.add(Btn(text=retry_txt, callback_data=f"e_name_{s_user.id}"))
        key.add(Btn(text=back_txt, callback_data="back-users-view"))
    return txt, key


def update_users_name_in_db(message, session, user_bot):
    try:
        user = get_user(message, session)
        selected_user, bot = user_bot
        selected_user.name = message.text
        session.commit()
        ch_id = selected_user.chat_id
        txt = get_text(BotText.YOUR_NAME_UPDATED, selected_user.language).format(
            name=message.text, admin=user.username
        )
        bot.send_message(ch_id, txt)
    except SQLAlchemyError as e:
        add_log(f"SQLAlchemyError in update_users_name_in_db: {e}")
    except Exception as e:
        add_log(f"Exception in update_users_name_in_db: {e}")


def process_delete_specific_user(call, session, bot):
    user = get_user(call, session)
    ch_id, msg = user.chat_id, str(call.message.id)
    user_id = int(call.data.split("_")[1])
    d_user = session.query(Users).filter_by(id=user_id).first()
    try:
        if d_user and not d_user.role:
            t, k = get_text_key_in_admin_commands(user, session)
            if d_user.username:
                d_txt = get_text(BotText.USER_DELETED_USERNAME, user.language).format(uname=d_user.username)
            elif d_user.name:
                d_txt = get_text(BotText.USER_DELETED_NAME, user.language).format(name=d_user.name)
            else:
                d_txt = get_text(BotText.USER_DELETED_CHAT_ID, user.language).format(chat_id=d_user.chat_id)
            t = d_txt + t
            bot.edit_message_text(chat_id=ch_id, message_id=msg, text=t, reply_markup=k)
            delete_user_reservations(d_user, session)
            send_delete_message_to_user(d_user, bot)
        elif d_user:
            t = get_text(BotText.ADMIN_NOT_ALLOWED_FOR_DELETE, user.language)
            bot.answer_callback_query(call.id, text=t, show_alert=True)
    except SQLAlchemyError as e:
        add_log(f"SQLAlchemyError in process_delete_specific_user: {e}")
    except Exception as e:
        add_log(f"Exception in process_delete_specific_user: {e}")


def delete_user_reservations(d_user, session):
    try:
        reserves = session.query(Reservations).filter_by(user_id=d_user.id).all()
        for reserve in reserves:
            session.delete(reserve)
        session.delete(d_user)
        session.commit()
    except SQLAlchemyError as e:
        add_log(f"SQLAlchemyError in delete_user_reservations: {e}")


def send_delete_message_to_user(d_user, bot):
    try:
        t = get_text(BotText.ADMIN_DELETED_USER, d_user.language)
        bot.send_message(chat_id=d_user.chat_id, text=t)
    except:
        pass


def process_charge_user(call, session, bot):
    try:
        user = get_user(call, session)
        ch_id, msg = user.chat_id, str(call.message.id)
        txt = get_text(BotText.SELECTION_CHARGE_USER, user.language)
        key = get_users_in_buttons(user, session, "ch-user")
        t = get_text(BotText.BACK_BUTTON, user.language)
        key.add(Btn(text=t, callback_data="backroom"))
        bot.edit_message_text(chat_id=ch_id, message_id=msg, text=txt, reply_markup=key)
    except Exception as e:
        add_log(f"Exception in process_charge_user: {e}")


def process_get_charge_for_user(call, session, bot):
    user = get_user(call, session)
    chat_id, msg_id = int(user.chat_id), str(call.message.id)
    db_id = call.data.split("_")[1]
    s_user = session.query(Users).filter_by(id=db_id).first()
    if s_user.username:
        t = get_text(BotText.GET_CHARGE_USERNAME, user.language).format(
            username=s_user.username, charge=s_user.charge
        )
    elif s_user.name:
        t = get_text(BotText.GET_CHARGE_NAME, user.language).format(
            username=s_user.name, charge=s_user.charge
        )
    else:
        t = get_text(BotText.GET_CHARGE_CHAT_ID, user.language).format(
            chat_id=s_user.chat_id, charge=s_user.charge
        )
    bot.edit_message_text(chat_id=chat_id, message_id=msg_id, text=t)
    bot.register_next_step_handler(call.message, get_charge, session, [s_user, bot])


def get_charge(message, session, user_bot):
    try:
        user = get_user(message, session)
        s_user, bot = user_bot
        text = check_text_in_charge(message)
        if text is None:
            send_operation_canceled_in_charge(user, bot)
        elif text:
            charge, new_charge = update_charge_for_user(message, session, s_user)
            manager_msg, key = get_manager_msg_key(user, [charge, new_charge], s_user)
            bot.send_message(user.chat_id, manager_msg, reply_markup=key)
            user_msg = get_text(BotText.USER_CHARGE_MESSAGE, s_user.language).format(
                charge=charge, new_charge=new_charge
            )
            user_msg = change_num_as_lang(user_msg, s_user.language)
            try:
                bot.send_message(s_user.chat_id, user_msg)
            except Exception as e:
                txt = get_text_for_error_charge_message(s_user, e, user)
                bot.send_message(user.chat_id, txt)
        else:
            send_invalid_entered_charge(user, s_user, bot)
    except SQLAlchemyError as e:
        add_log(f"SQLAlchemyError in get_charge: {e}")
    except Exception as e:
        add_log(f"Exception in get_charge: {e}")


def get_text_for_error_charge_message(s_user, e, user):
    if s_user.username:
        return get_text(BotText.MESSAGE_NOT_SENT_USERNAME, user.language).format(username=s_user.username, error=e)
    elif s_user.name:
        return get_text(BotText.MESSAGE_NOT_SENT_NAME, user.language).format(name=s_user.name, error=e)
    else:
        return get_text(BotText.MESSAGE_NOT_SENT_CHAT_ID, user.language).format(chat_id=s_user.chat_id, error=e)


def send_operation_canceled_in_charge(user, bot):
    key = InlineKeyboardMarkup()
    back_txt = get_text(BotText.BACK_BUTTON, user.language)
    txt = get_text(BotText.OPERATION_CANCELED, user.language)
    key.add(Btn(text=back_txt, callback_data="back-charge-user"))
    bot.send_message(user.chat_id, txt, reply_markup=key)


def update_charge_for_user(message, session, s_user):
    try:
        charge = int(change_num_as_lang(message.text, "en"))
        new_charge = s_user.charge + charge
        s_user.charge = new_charge
        session.commit()
        return charge, new_charge
    except SQLAlchemyError as e:
        add_log(f"SQLAlchemyError in update_charge_for_user: {e}")


def get_manager_msg_key(user, charges, s_user):
    charge, new_charge = charges
    key = InlineKeyboardMarkup()
    if s_user.username:
        name = f"@{s_user.username}"
    elif s_user.name:
        name = s_user.name
    else:
        name = s_user.chat_id
    manager_msg = get_text(BotText.MANAGER_CHARGE_MESSAGE, user.language).format(
        user=name, charge=charge, new_charge=new_charge
    )
    manager_msg = change_num_as_lang_and_username(manager_msg, user.language)
    ok_text = get_text(BotText.OK_REMINDER_BUTTON, user.language)
    key.add(Btn(text=ok_text, callback_data="backroom"))
    return manager_msg, key


def send_invalid_entered_charge(user, selected_user, bot):
    key = InlineKeyboardMarkup()
    txt = get_text(BotText.INVALID_ENTERED_CHARGE, user.language)
    retry_txt = get_text(BotText.RETRY, user.language)
    key.add(Btn(text=retry_txt, callback_data=f"ch-user_{selected_user.id}"))
    bot.send_message(user.chat_id, txt, reply_markup=key)
