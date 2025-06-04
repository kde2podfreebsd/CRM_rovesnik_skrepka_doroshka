from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.ext.mutable import MutableList, MutableDict
from sqlalchemy.types import ARRAY

from BackendApp.Database.Models import Base


class Mailing(Base):
    __tablename__ = 'mailing'

    id = Column(Integer, primary_key=True)
    mailing_name = Column(String, unique=True, nullable=False)
    photo_paths = Column(MutableList.as_mutable(ARRAY(String)), nullable=True)
    video_paths = Column(MutableList.as_mutable(ARRAY(String)), nullable=True)
    document_paths = Column(MutableList.as_mutable(ARRAY(String)), nullable=True)
    text = Column(String, nullable=False)
    url_buttons = Column(MutableList.as_mutable(ARRAY(String)), nullable=True) # url - key, button_text - value
    preset = Column(String, nullable=False)
    alpha = Column(Integer, default=0)
    alpha_sent = Column(Integer, nullable=True)
    alpha_delivered = Column(Integer, nullable=True)
    beta = Column(Integer, default=100)
    beta_sent = Column(Integer, nullable=True)
    beta_delivered = Column(Integer, nullable=True)