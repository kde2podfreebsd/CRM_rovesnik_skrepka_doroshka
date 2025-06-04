from sqlalchemy import Column, Integer, Float, ForeignKey, String, BigInteger, DateTime
from sqlalchemy.orm import relationship
from BackendApp.Database.Models import Base
from BackendApp.Database.Models.client_model import Client
from BackendApp.Database.Models.bar_model import Bar

class Transaction(Base):
    __tablename__ = 'transaction'

    id = Column(Integer, primary_key=True)
    bar_id = Column(Integer, ForeignKey('bar.bar_id'), nullable=False)
    amount = Column(Float, nullable=False)
    final_amount = Column(Float, nullable=False)
    tx_type = Column(String)
    time_stamp = Column(DateTime, nullable=False)

    client_chat_id = Column(BigInteger, ForeignKey('client.chat_id'), nullable=False)
    client = relationship("Client", back_populates="transactions")
