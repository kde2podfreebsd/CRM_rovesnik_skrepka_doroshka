from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.types import PickleType

from BackendApp.Database.Models import Base

class Quiz(Base):
    __tablename__ = 'quiz'

    id = Column(Integer, primary_key=True)
    header = Column(String)
    answers = Column(PickleType)
    answer_count = Column(Integer)
    correct_ans_id = Column(Integer)
    test_id = Column(Integer, ForeignKey('test.test_id', ondelete="CASCADE"))

    linked_table = relationship("Test", cascade="all,delete")

    def __init__(self, header, answers, answer_count, correct_ans_id, test_id):
        self.header = header
        self.answers = answers
        self.answer_count = answer_count
        self.correct_ans_id = correct_ans_id
        self.test_id = test_id