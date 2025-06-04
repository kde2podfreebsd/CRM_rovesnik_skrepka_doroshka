from sqlalchemy import Column, Integer, BigInteger, String, Boolean, ForeignKey, DateTime, Float, UUID

from BackendApp.Database.Models import Base

class Reservation(Base):
    __tablename__ = 'reservations'

    id = Column(Integer, primary_key=True)
    client_chat_id = Column(BigInteger, ForeignKey('client.chat_id'), nullable=False)
    order_uuid = Column(String, nullable=False)
    table_uuid = Column(String, ForeignKey('tables.table_uuid'), nullable=False)
    reservation_start = Column(DateTime, nullable=False)
    reserve_id = Column(String, nullable=False, unique=True)
    status = Column(String, nullable=False)
    deposit = Column(Float, nullable=True)
    
