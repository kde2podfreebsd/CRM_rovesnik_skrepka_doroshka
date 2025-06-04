from sqlalchemy import Boolean, Column, Integer, String, ForeignKey, Float
from sqlalchemy.orm import relationship

from BackendApp.Database.Models import Base


class FAQ(Base):
    __tablename__ = 'faq'

    id = Column(Integer, primary_key=True)
    text = Column(String, nullable=False)

    bar_id = Column(Integer, ForeignKey('bar.bar_id'))
    bar = relationship("Bar", back_populates="faqs")
