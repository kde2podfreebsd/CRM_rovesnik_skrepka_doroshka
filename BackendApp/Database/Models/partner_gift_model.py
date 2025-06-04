from sqlalchemy import Column, Integer, String, BigInteger, ForeignKey
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.types import ARRAY

from BackendApp.Database.Models import Base

class PartnerGift(Base):
    __tablename__ = 'partner_gift'

    id = Column(Integer, primary_key=True)
    short_name = Column(String, nullable=False)
    promotion_text = Column(String, nullable=False)
    got_gift = Column(MutableList.as_mutable(ARRAY(BigInteger)), default=[])
    bar_id = Column(Integer, ForeignKey("bar.bar_id"), nullable=False)
