from pydantic import BaseModel
from datetime import datetime

class TransactionRequest(BaseModel):
    bar_id: int
    amount: float
    final_amount: float
    tx_type: str
    client_chat_id: int

class TransactionForReturn(BaseModel):
    id: int
    client_chat_id: int
    bar_id: int
    amount: float
    final_amount: float
    tx_type: str