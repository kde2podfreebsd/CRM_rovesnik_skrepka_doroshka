from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime

from BackendApp.Database.Models import Base

class Table(Base):
    __tablename__ = 'tables'

    id = Column(Integer, primary_key=True)
    bar_id = Column(Integer, ForeignKey('bar.bar_id'), nullable=False)
    storey = Column(Integer, nullable=False)
    table_id = Column(Integer, nullable=False)
    table_uuid = Column(String, nullable=False, unique=True)
    terminal_group_uuid = Column(String, nullable=False)
    capacity = Column(Integer, nullable=False)
    reserved = Column(Boolean, default=False)
    is_bowling = Column(Boolean, default=False)
    is_pool = Column(Boolean, default=False)
    block_start = Column(DateTime, nullable=True)
    block_end = Column(DateTime, nullable=True)