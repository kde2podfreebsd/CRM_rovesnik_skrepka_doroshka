from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, BigInteger
from sqlalchemy.orm import relationship


from BackendApp.Database.Models import Base

class Referral(Base):
    __tablename__ = "referrals"

    id = Column(Integer, primary_key=True)
    chat_id = Column(BigInteger, ForeignKey("client.chat_id"), nullable=False)
    referral_link = Column(String, nullable=False)
    got_bonus = Column(Boolean, default=False)
