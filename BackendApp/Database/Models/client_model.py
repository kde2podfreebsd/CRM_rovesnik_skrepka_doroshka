from sqlalchemy import Boolean, Column, Float, ForeignKey, Integer, String, BigInteger
from sqlalchemy.orm import relationship

from BackendApp.Database.Models import Base


class Client(Base):
    __tablename__ = "client"

    id = Column(Integer, primary_key=True)
    chat_id = Column(BigInteger, nullable=False, unique=True)
    iiko_id = Column(String, unique=True)
    iiko_card = Column(String, unique=True)
    username = Column(String)
    first_name = Column(String)
    last_name = Column(String)
    phone = Column(String, nullable=True)
    spent_amount = Column(Float, nullable=True, default=0)
    qr_code_path = Column(String, nullable=True)
    referral_link = Column(String, unique=True, default=None)
    change_reservation = Column(Boolean, default=True)
    reserve_table = Column(Boolean, default=True)
    got_review_award = Column(Boolean, default=False)
    got_yandex_maps_award = Column(Boolean, default=False)

    transactions = relationship("Transaction", back_populates="client")
    subscriptions = relationship("Subscription")
    action_logs = relationship("ClientActionLog", back_populates="client")