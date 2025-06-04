from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from BackendApp.Database.Models import Base

class ArtistEventRelationship(Base):
    __tablename__ = 'artis_event_relationship'

    id = Column(Integer, primary_key=True)
    artist_id = Column(Integer, ForeignKey('artist.id'))
    event_id = Column(Integer, ForeignKey('event.id'))

    linked_table_artist = relationship("Artist")
    linked_table_event = relationship("Event")

    def __init__(self, artist_id, event_id):
        self.artist_id = artist_id
        self.event_id = event_id