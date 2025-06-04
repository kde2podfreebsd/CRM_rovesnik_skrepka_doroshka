import datetime
import enum

from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.dialects.postgresql import ENUM as PgEnum
from sqlalchemy.orm import relationship
from BackendApp.Database.Models.promocode_types import _PromocodeType

from BackendApp.Database.Models import Base

class Promocode(Base):
    __tablename__ = "promocode"

    id = Column(Integer, primary_key=True)
    type = Column(PgEnum(_PromocodeType), nullable=False)  # Тип промокода
    name = Column(String, nullable=False)  # Название промокода
    operational_info = Column(
        String, nullable=False
    )  # Операционная информация о том, что сделать тому, кто пробивает промокод
    description = Column(String, nullable=False)  # Описание промокода
    number = Column(Integer, nullable=False, unique=True)  # Номер промокода, сам промокод
    end_time = Column(DateTime, nullable=True)  # Дата и время окончания промокода
    is_activated = Column(Boolean, default=False)  # Активирован ли промокод?
    qr_path = Column(String, nullable=True)
    hashcode = Column(String, nullable=True)
    activation_time = Column(DateTime, nullable=True)
    weight = Column(Integer, nullable=True)

    client_chat_id = Column(BigInteger, nullable=True) # chat_id клиента, которому назначен промокод