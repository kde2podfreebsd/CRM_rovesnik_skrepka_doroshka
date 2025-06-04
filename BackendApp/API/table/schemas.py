from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class TableForCreating(BaseModel):
    bar_id: int
    storey: int
    table_id: int
    table_uuid: str
    terminal_group_uuid: str
    capacity: int
    is_bowling: Optional[bool] = None
    is_pool: Optional[bool] = None
    block_start: Optional[datetime] = None
    block_end: Optional[datetime] = None

class TableForUpdating(BaseModel):
    table_uuid: str
    table_id: Optional[int] = None
    bar_id: Optional[int] = None
    storey: Optional[int] = None
    reserved: Optional[bool] = None
    terminal_group_uuid: Optional[str] = None
    capacity: Optional[int] = None
    is_bowling: Optional[bool] = None
    is_pool: Optional[bool] = None
    block_start: Optional[datetime] = None
    block_end: Optional[datetime] = None

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
    block_start: Optional[datetime] = None
    block_end: Optional[datetime] = None

class ChangeStatusRequest(BaseModel):
    storey: int
    bar_id: int

class GetByStoreyRequest(BaseModel):
    storey: int
    bar_id: int

class GetByCapacityAndTimeRequest(BaseModel):
    bar_id: int
    datetime: datetime
    capacity: int

class CheckAvailabilityRequest(BaseModel):
    table_uuid: str
    datetime: datetime

class BlockTablesRequest(BaseModel):
    bar_id: int
    storey: int
    block_start: datetime
    block_end: datetime