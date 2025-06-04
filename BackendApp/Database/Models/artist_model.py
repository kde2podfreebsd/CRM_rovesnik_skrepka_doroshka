from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, Boolean
from sqlalchemy.orm import relationship
from BackendApp.Database.Models import Base
from BackendApp.Database.Models.bar_model import Bar

class Artist(Base):
    __tablename__ = 'artist'

    id = Column(Integer, primary_key=True)   
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    img_path = Column(String, nullable=False)

    def __init__(self, name, description, img_path):
        self.name = name
        self.description = description
        self.img_path = img_path