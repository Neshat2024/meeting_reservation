from sqlalchemy.exc import SQLAlchemyError

from functions.get_functions import generate_random_hex_color
from models.users import Users
from services.log import add_log


def set_color_for_all_users(session):
    try:
        users = session.query(Users).all()
        for user in users:
            if user.color is None:
                user.color = generate_random_hex_color()
        session.commit()
    except SQLAlchemyError as e:
        add_log(f"SQLAlchemyError in set_color_for_all_users: {e}")
    except Exception as e:
        add_log(f"Exception in set_color_for_all_users: {e}")
