from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, Boolean, PickleType, BigInteger
from sqlalchemy.orm import relationship
from BackendApp.Database.Models import Base

class Ticket(Base):
    __tablename__ = 'ticket'

    id = Column(Integer, primary_key=True)
    client_chat_id = Column(BigInteger, nullable=False)
    qr_path = Column(String, nullable=False)
    activation_status = Column(Boolean, default=False)
    friends = Column(PickleType, nullable=True)
    hashcode = Column(String, unique=True)
    event_id = Column(Integer, ForeignKey('event.id'), nullable=False)
    activation_time = Column(DateTime, nullable=True)

    event = relationship("Event", back_populates="tickets")
