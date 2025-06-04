from sqlalchemy import Boolean, Column, Float, ForeignKey, Integer, BigInteger, String

from BackendApp.Database.Models import Base


class Request(Base):
    __tablename__ = "requests"

    req_id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, nullable=False)
    req_status = Column(String, nullable=False)