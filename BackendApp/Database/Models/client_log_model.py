from datetime import datetime

from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import relationship

from BackendApp.Database.Models import Base


class ClientActionLog(Base):
    __tablename__ = 'client_action_log'

    id = Column(Integer, primary_key=True)
    action = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False)
    
    client_chat_id = Column(BigInteger, ForeignKey('client.chat_id'), nullable=False)
    client = relationship("Client", back_populates="action_logs")
    