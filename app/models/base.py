from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """
    Базовый класс для SQLAlchemy-моделей
    """
    __table_args__ = {'schema': 'bookings'}
