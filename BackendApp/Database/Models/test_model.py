from sqlalchemy import Column, Integer, String, Float, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import ENUM as PgEnum
from BackendApp.Database.Models.promocode_types import _PromocodeType
from sqlalchemy.orm import relationship

from BackendApp.Database.Models import Base

class Test(Base):
    __tablename__ = 'test'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    correct_cnt = Column(Integer)
    total_cnt = Column(Integer)
    description = Column(String)
    test_id = Column(Integer, nullable=False, unique=True)
    promocode_type = Column(PgEnum(_PromocodeType), nullable=False)
    bar_id = Column(Integer, ForeignKey("bar.bar_id"), nullable=False)

    def __init__(self, name, correct_cnt, total_cnt, description, promocode_type, test_id, bar_id):
        self.name = name
        self.correct_cnt = correct_cnt
        self.description = description
        self.test_id = test_id
        self.promocode_type = promocode_type
        self.total_cnt = total_cnt
        self.bar_id = bar_id
