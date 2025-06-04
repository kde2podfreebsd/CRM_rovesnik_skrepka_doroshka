from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.dialects.postgresql import ENUM as PgEnum
from BackendApp.Database.Models.promocode_types import _PromocodeType
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.types import ARRAY

from BackendApp.Database.Models import Base

class AffilatePromotions(Base):
    __tablename__ = 'affilate_promotions'

    id = Column(Integer, primary_key=True)
    channel_link = Column(String)
    promotion_text = Column(String)
    promocode_type = Column(PgEnum(_PromocodeType), nullable=False)
    short_name = Column(String)
    sub_chat_id = Column(MutableList.as_mutable(ARRAY(String)), default=[])
    bar_id = Column(Integer, ForeignKey("bar.bar_id"), nullable=False)
    
    def __init__(self, channel_link, promotion_text, promocode_type, sub_chat_id, short_name, bar_id):
        self.channel_link = channel_link
        self.promotion_text = promotion_text
        self.promocode_type = promocode_type
        self.short_name = short_name
        self.sub_chat_id = sub_chat_id
        self.bar_id = bar_id
