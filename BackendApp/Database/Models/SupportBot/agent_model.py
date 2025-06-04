from sqlalchemy import Boolean, Column, Float, ForeignKey, Integer, String

from BackendApp.Database.Models import Base


class Agent(Base):
    __tablename__ = "agent"

    id = Column(Integer, primary_key=True)
    agent_id = Column(Integer, nullable=False, unique=True)
