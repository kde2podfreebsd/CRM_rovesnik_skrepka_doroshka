from pydantic import BaseModel
from typing import Optional, Union

class ClientForReturn(BaseModel):
    chat_id: int
    iiko_id: Optional[str] = None
    iiko_card: Optional[str] = None
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    spent_amount: Optional[float] = None
    qr_code_path: Optional[str] = None
    referral_link: str
    change_reservation: bool
    reserve_table: bool
    got_review_award: bool
    got_yandex_maps_award: bool
    balance: float
    loyalty_info: list

class RefillRequest(BaseModel):
    chat_id: int
    amount: float

class UpdatePhoneRequest(BaseModel):
    chat_id: int
    phone: str

class UpdateFirstNameRequest(BaseModel):
    chat_id: int
    first_name: str

class UpdateLastNameRequest(BaseModel):
    chat_id: int
    last_name: str

class SendShippingQueryRequest(BaseModel):
    chat_id: int
    capacity: int

class ChatIdAndUsernameForReturn(BaseModel):
    username: str
    chat_id: int