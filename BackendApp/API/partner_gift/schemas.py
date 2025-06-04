from pydantic import BaseModel
from typing import Optional, List

class PartnerGiftForCreating(BaseModel):
    short_name: str
    promotion_text: str
    bar_id: int

class PartnerGiftForUpdating(BaseModel):
    partner_gift_id: int
    short_name: Optional[str] = None
    promotion_text: Optional[str] = None
    got_gift: Optional[List] = None
    bar_id: Optional[int] = None

class PartnerGiftForReturn(BaseModel):
    id: int
    short_name: str
    promotion_text: str
    got_gift: list
    bar_id: int
