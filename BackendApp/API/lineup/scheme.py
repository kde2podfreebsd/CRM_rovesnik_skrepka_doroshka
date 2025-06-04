from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ArtistRequest(BaseModel):
    name: str
    description: str
    img_path: str
    
class ArtistResponse(BaseModel):
    artist_id: int
    name: str
    description: str
    img_path: str
    
class ArtistToUpdate(BaseModel):
    artist_id: int
    name: Optional[str] = None
    description: Optional[str] = None
    img_path: Optional[str] = None
    
    
class ArtistEventRelationship(BaseModel):
    artist_id: int
    event_id: int