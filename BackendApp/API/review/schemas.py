from pydantic import BaseModel
from typing import Optional

class ReviewMold(BaseModel):
    chat_id: int
    text: str
    bar_id: Optional[int] = None
    event_id: Optional[int] = None

class GetByChatAndBarIdsRequest(BaseModel):
    chat_id: int
    bar_id: int

class GetByChatAndEventIdsRequest(BaseModel):
    chat_id: int
    event_id: int