from sqlalchemy import Boolean, Column, Float, ForeignKey, Integer, String

from BackendApp.Database.Models import Base


class Password(Base):
    __tablename__ = "passwords"

    id = Column(Integer, primary_key=True)
    password = Column(String, nullable=False)
