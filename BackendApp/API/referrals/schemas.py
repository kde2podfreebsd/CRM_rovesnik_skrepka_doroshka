from typing import Optional, Union

from pydantic import BaseModel

class ReferralForReturn(BaseModel):
    chat_id: int
    referral_link: str
    got_bonus: bool
