from pydantic import BaseModel
from typing import List, Optional, Union
from datetime import datetime

class CreatetTicketRequest(BaseModel):
    qr_path: str
    activation_status: bool
    event_id: int
    client_chat_id: int
    hashcode: Optional[str] = None
    friends: Optional[list] = None

class PurchaseTicketRequest(BaseModel):
    event_id: int
    client_chat_id: int
    
class PurchaseTicketByBonusPoints(BaseModel):
    event_id: int
    client_chat_id: int
    bar_id: int
    amount: float
    
class Friend(BaseModel):
    name: str
    username: str
    
class PurchaseFreeTicketRequest(PurchaseTicketRequest):
    friends: Union[List[Friend], None]
    
class TicketInfo(BaseModel):
    id: int
    client_chat_id: int
    qr_path: str
    activation_status: bool
    friends: Union[List[Friend], None]
    hashcode: str
    event_id: int
    
    
class TicketUpdateRequest(BaseModel):
    id: int
    qr_path: Optional[str] = None
    activation_status: Optional[bool] = None
    event_id: Optional[int] = None
    client_chat_id: Optional[int] = None
    hashcode: Optional[str] = None
    friends: Optional[List[Friend]] = None
    activation_time: Optional[datetime] = None