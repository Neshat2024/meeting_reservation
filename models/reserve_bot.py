from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from services.database import create_database_if_not_exists
from services.log import add_log
from settings import settings

engine = create_engine(settings.DATABASE_URL_RESERVE)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# engine = create_engine(
#     settings.DATABASE_URL_RESERVE, echo=False, pool_pre_ping=True, pool_recycle=10
# )
# SessionLocal = sessionmaker(
#     autocommit=False,
#     autoflush=False,
#     bind=engine,
#     expire_on_commit=False,  # Prevents issues with accessing objects after commit
# )
Base = declarative_base()


def init_db(bot):
    create_database_if_not_exists(settings.DATABASE_URL_RESERVE, bot)
    try:
        Base.metadata.create_all(engine)
    except Exception as e:
        add_log(f"Error creating Note-Booking table: {e}")


@contextmanager
def get_db_session():
    """Context manager for database sessions with proper error handling"""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception as e:
        add_log(f"Database error in Note-Booking bot: {e}")
        session.rollback()
        raise
    finally:
        session.close()
