from pydantic import BaseModel
from typing import Optional, List
from BackendApp.Database.Models.promocode_types import _PromocodeType

class CreatePromotionRequest(BaseModel):
    channel_link: str
    promotion_text: str
    promocode_type: _PromocodeType
    short_name: str
    bar_id: int
    
class PromotionResponse(BaseModel):
    id: int
    channel_link: str
    promotion_text: str
    promocode_type: _PromocodeType
    short_name: str
    bar_id: int
    sub_chat_id: Optional[List[str]]
    
class UpdatePromotionRequest(BaseModel):
    id: int
    channel_link: Optional[str] = None
    promotion_text: Optional[str] = None
    promocode_type: Optional[_PromocodeType] = None
    short_name: Optional[str] = None
    sub_chat_id: Optional[List[str]] = None
    bar_id: Optional[int] = None