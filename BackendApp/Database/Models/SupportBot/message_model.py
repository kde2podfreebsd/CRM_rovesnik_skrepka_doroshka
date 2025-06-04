from sqlalchemy import Boolean, Column, Float, ForeignKey, Integer, String

from BackendApp.Database.Models import Base


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True)
    req_id = Column(Integer, nullable=False)
    message = Column(String, nullable=False)
    user_status = Column(String, nullable=False)
    date = Column(String, nullable=False)