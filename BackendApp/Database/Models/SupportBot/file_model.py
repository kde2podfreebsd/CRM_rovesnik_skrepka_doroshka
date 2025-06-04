from sqlalchemy import Boolean, Column, Float, ForeignKey, Integer, String

from BackendApp.Database.Models import Base


class File(Base):
    __tablename__ = "files"

    id = Column(Integer, primary_key=True)
    req_id = Column(Integer, nullable=False)
    file_id = Column(String, nullable=False)
    file_name = Column(String, nullable=False)
    type = Column(String, nullable=False)
