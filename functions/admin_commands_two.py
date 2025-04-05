from sqlalchemy.exc import SQLAlchemyError
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton as Btn

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
        ch_id, msg_id = user.chat_id, str(call.message.id)
        txt = get_text(BotText.EDIT_USERS_NAME, user.language)
        key, buttons = InlineKeyboardMarkup(row_width=2), []
        users = session.query(Users).all()
        for user in users:
            buttons.append(
                Btn(text=f"@{user.username}", callback_data=f"e_name_{user.id}")
            )
            if len(buttons) == 2:
                key.row(*buttons)
                buttons = []
        if buttons:
            key.row(*buttons)
        t = get_text(BotText.BACK_BUTTON, user.language)
        key.add(Btn(text=t, callback_data="back-view"))
        bot.edit_message_text(
            chat_id=ch_id, message_id=msg_id, text=txt, reply_markup=key
        )
    except Exception as e:
        add_log(f"Exception in process_edit_users_name: {e}")


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
        key.add(Btn(text=back_txt, callback_data="back-users-view"))
    elif num == TWO:
        txt = get_text(BotText.NAME_UPDATED, user.language).format(
            username=selected_user.username, new_name=selected_user.name
        )
        key.add(Btn(text=back_txt, callback_data="back-view"))
    elif num == THREE:
        txt = get_text(BotText.NAME_TAKEN_ADMIN, user.language)
        key.add(Btn(text=retry_txt, callback_data=f"e_name_{selected_user.id}"))
        key.add(Btn(text=back_txt, callback_data="back-users-view"))
    else:
        txt = get_text(BotText.NAME_INVALID_ADMIN, user.language)
        key.add(Btn(text=retry_txt, callback_data=f"e_name_{selected_user.id}"))
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


def process_charge_user(call, session, bot):
    try:
        user = get_user(call, session)
        ch_id, msg_id = user.chat_id, str(call.message.id)
        txt = get_text(BotText.SELECTION_CHARGE_USER, user.language)
        key, buttons = InlineKeyboardMarkup(row_width=2), []
        users = session.query(Users).all()
        for u in users:
            if u.username:
                buttons.append(
                    Btn(text=f"@{u.username}", callback_data=f"ch-name_{u.id}")
                )
            else:
                buttons.append(
                    Btn(text=f"name={u.name}", callback_data=f"ch-name_{u.id}")
                )
            if len(buttons) == 2:
                key.row(*buttons)
                buttons = []
        if buttons:
            key.row(*buttons)
        bot.edit_message_text(
            chat_id=ch_id, message_id=msg_id, text=txt, reply_markup=key
        )
    except Exception as e:
        add_log(f"Exception in process_charge_user: {e}")


def process_get_charge_for_user(call, session, bot):
    user = get_user(call, session)
    chat_id, msg_id = int(user.chat_id), str(call.message.id)
    db_id = call.data.split("_")[1]
    s_user = session.query(Users).filter_by(id=db_id).first()
    if s_user.username not in ["", None, 0]:
        uname = s_user.username
        t = get_text(BotText.GET_CHARGE_USERNAME, user.language).format(
            username=uname, charge=s_user.charge
        )
    else:
        name = s_user.name
        t = get_text(BotText.GET_CHARGE_NAME, user.language).format(
            username=name, charge=s_user.charge
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
            bot.send_message(chat_id=user.chat_id, text=manager_msg, reply_markup=key)
            user_msg = get_text(BotText.USER_CHARGE_MESSAGE, s_user.language).format(
                charge=charge, new_charge=new_charge
            )
            user_msg = change_num_as_lang(user_msg, s_user.language)
            try:
                bot.send_message(s_user.chat_id, user_msg)
            except Exception as e:
                txt = get_text(BotText.MESSAGE_NOT_SENT, user.language).format(
                    user=s_user.name, error=e
                )
                bot.send_message(user.chat_id, txt)
        else:
            send_invalid_entered_charge(user, s_user, bot)
    except SQLAlchemyError as e:
        add_log(f"SQLAlchemyError in get_charge: {e}")
    except Exception as e:
        add_log(f"Exception in get_charge: {e}")


def send_operation_canceled_in_charge(user, bot):
    key = InlineKeyboardMarkup()
    back_txt = get_text(BotText.BACK_BUTTON, user.language)
    txt = get_text(BotText.OPERATION_CANCELED, user.language)
    key.add(Btn(text=back_txt, callback_data="back-charge-user"))
    bot.send_message(chat_id=user.chat_id, text=txt, reply_markup=key)


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
    if s_user.username not in ["", None, 0]:
        name = f"@{s_user.username}"
    else:
        name = s_user.name
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
    key.add(Btn(text=retry_txt, callback_data=f"ch-name_{selected_user.id}"))
    bot.send_message(chat_id=user.chat_id, text=txt, reply_markup=key)
