from pydantic import BaseModel
from typing import Optional, Union
from BackendApp.Database.Models.promocode_model import Promocode
from BackendApp.Database.Models.promocode_types import _PromocodeType
from datetime import datetime
from typing import Optional, Union

from pydantic import BaseModel

class Promocode(BaseModel):
    client_chat_id: Optional[int] = None
    type: _PromocodeType
    name: str
    operational_info: str
    description: str
    number: int
    end_time: Optional[datetime] = None
    is_activated: Optional[bool] = None
    weight: Optional[int] = None

class PromocodeRequest(BaseModel):
    number: int
    client_chat_id: int

class PromocodeUpdateRequest(BaseModel):
    number: int
    name: Optional[str] = None
    operational_info: Optional[str] = None
    description: Optional[str] = None
    type: Optional[_PromocodeType] = None
    client_chat_id: Optional[int] = None
    is_activated: Optional[bool] = None
    weight: Optional[int] = None
