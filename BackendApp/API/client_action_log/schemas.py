from pydantic import BaseModel
from datetime import datetime

class LogForReturn(BaseModel):
    action: str
    created_at: datetime