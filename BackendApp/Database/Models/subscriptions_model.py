from sqlalchemy import Column, Integer, String, ForeignKey, BigInteger
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.orm import relationship
from sqlalchemy.types import ARRAY

from BackendApp.Database.Models import Base

class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True)
    subs_ids = Column(MutableList.as_mutable(ARRAY(String)), default=[])
    client_id = Column(BigInteger, ForeignKey("client.id"))

    clients = relationship("Client", back_populates="subscriptions")