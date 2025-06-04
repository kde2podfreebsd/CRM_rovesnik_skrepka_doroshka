from BackendApp.Database.Models import Base
from sqlalchemy import BigInteger, String, Integer, Column, ForeignKey

class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True)
    chat_id = Column(BigInteger, ForeignKey("client.chat_id"), nullable=False)
    bar_id = Column(Integer, ForeignKey("bar.bar_id"), nullable=True)
    event_id = Column(Integer, nullable=True)
    text = Column(String, nullable=False)
