from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class EventForCreating(BaseModel):
    short_name: str
    description: str
    img_path: str
    dateandtime: datetime
    end_datetime: datetime
    bar_id: int
    place: str
    age_restriction: int
    event_type: str
    price: float
    notification_time: Optional[List[str]] = None
    motto: Optional[str] = None

class EventForUpdating(BaseModel):
    event_id: int
    short_name: Optional[str] = None
    description: Optional[str] = None
    img_path: Optional[str] = None
    dateandtime: Optional[datetime] = None
    end_datetime: Optional[datetime] = None
    bar_id: Optional[int] = None
    place: Optional[str] = None
    age_restriction: Optional[int] = None
    event_type: Optional[str] = None
    price: Optional[float] = None
    notification_time: Optional[List[str]] = None
    motto: Optional[str] = None
    
class EventForReturn(BaseModel):
    event_id: int
    short_name: str
    description: str
    img_path: str
    dateandtime: datetime
    end_datetime: datetime
    bar_id: int
    place: str
    age_restriction: int
    event_type: str
    price: float
    notification_time: Optional[List[str]] = None
    motto: Optional[str] = None
    
    
class EventArtistRelationshipResponse(BaseModel):
    relationship_id: int
    event_id: int
    artist_id: int
    
