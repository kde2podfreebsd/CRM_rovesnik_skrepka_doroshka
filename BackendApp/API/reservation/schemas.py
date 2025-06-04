from pydantic import BaseModel
from typing import Optional, Literal
from datetime import datetime

class ReservationForCreating(BaseModel):
    client_chat_id: int
    order_uuid: str
    table_uuid: str
    reservation_start: str
    deposit: Optional[float] = None

class ReservationForUpdating(BaseModel):
    reserve_id: str
    client_chat_id: Optional[int] = None
    table_uuid: Optional[str] = None
    reservation_start: Optional[str] = None
    deposit: Optional[float] = None 

class ReservationForCancelling(BaseModel):
    reserve_id: str
    cancel_reason: Optional[Literal["ClientNotAppeared", "ClientRefused", "Other"]] = "Other"

class ReservationForReturn(BaseModel):
    reservation_id: int
    client_chat_id: int
    order_uuid: str
    table_uuid: str
    reserve_id: str
    reservation_start: datetime
    status: str
    deposit: Optional[float] = None

class TableForReturn(BaseModel):
    bar_id: int
    storey: int
    table_id: int
    table_uuid: str
    terminal_group_uuid: str
    capacity: int
    reserved: bool
    is_bowling: bool
    is_pool: bool

class ReservationAndTableForReturn(BaseModel):
    reservation_id: int
    client_chat_id: int
    order_uuid: str
    table_uuid: str
    reserve_id: str
    reservation_start: datetime
    status: str
    deposit: Optional[float] = None
    table: TableForReturn

class GetClientReservationsRequest(BaseModel):
    chat_id: int
    bar_id: int
