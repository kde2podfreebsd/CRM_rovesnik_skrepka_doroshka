from sqlalchemy import Column, Integer, Float, Boolean, ForeignKey, BigInteger
from sqlalchemy.orm import relationship

from BackendApp.Database.Models import Base

class TestResult(Base):
    __tablename__ = 'test_result'

    id = Column(Integer, primary_key=True)
    chat_id = Column(BigInteger, ForeignKey('client.chat_id', ondelete="CASCADE"))
    test_id = Column(Integer, ForeignKey('test.test_id', ondelete="CASCADE"))
    correct_cnt = Column(Integer)
    total_cnt = Column(Integer)
    get_reward = Column(Boolean)
    is_first_try = Column(Boolean)
    claimed_reward = Column(Boolean, default = False)

    client = relationship("Client", cascade="all,delete")
    test = relationship("Test", cascade="all,delete")

    def __init__(self, chat_id, test_id, correct_cnt, total_cnt, get_reward, is_first_try):
        self.chat_id = chat_id
        self.test_id = test_id
        self.correct_cnt = correct_cnt
        self.total_cnt = total_cnt
        self.get_reward = get_reward
        self.is_first_try = is_first_try