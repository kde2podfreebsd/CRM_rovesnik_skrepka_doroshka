from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, Boolean
from sqlalchemy.orm import relationship
from BackendApp.Database.Models import Base
from BackendApp.Database.Models.bar_model import Bar
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.types import ARRAY

class Event(Base):
    __tablename__ = 'event'

    id = Column(Integer, primary_key=True)
    short_name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    img_path = Column(String)
    datetime = Column(DateTime, nullable=False)
    end_datetime = Column(DateTime, nullable=False)
    bar_id = Column(Integer, ForeignKey('bar.bar_id'), nullable=False)
    place = Column(String)
    age_restriction = Column(Integer)
    event_type = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    notification_time = Column(MutableList.as_mutable(ARRAY(String)), nullable=True)
    motto = Column(String, nullable=True)

    tickets = relationship("Ticket", cascade="all,delete", back_populates="event")
