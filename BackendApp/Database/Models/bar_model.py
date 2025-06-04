from sqlalchemy import Boolean, Column, Integer, String, ForeignKey, Float
from sqlalchemy.orm import relationship

from BackendApp.Database.Models import Base


class Bar(Base):
    __tablename__ = 'bar'

    id = Column(Integer, primary_key=True)
    bar_id = Column(Integer, nullable=False, unique=True)
    bar_name = Column(String, nullable=False, unique=True)

    faqs = relationship("FAQ", back_populates="bar")