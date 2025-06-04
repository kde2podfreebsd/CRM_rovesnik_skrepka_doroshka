from typing import Optional, Union

from pydantic import BaseModel

from BackendApp.acquiring.common import CalculationSubject


class Item(BaseModel):
    Name: str
    Price: int  # in kopecs
    Quantity: int
    Amount: int  # Quantity * Price
    PaymentMethod: Optional[str] = None
    PaymentObject: Optional[CalculationSubject] = None
    Tax: str
    Ean13: Optional[str] = None


class Receipt(BaseModel):
    Items: list[Item]
    FfdVersion: Optional[str] = None  # by default - 1.05, could be 1.2
    Email: Optional[str] = None
    Phone: Optional[str] = None
    Taxation: str  # usn_income


class Transaction(BaseModel):
    TerminalKey: str
    Amount: int  # this field is represented in kopecs; e.g: 100 (rubles) -> 10000
    OrderId: int
    PaymentId: Optional[int] = None
    Description: Optional[str] = None
    DATA: Optional[dict] = None
    Receipt: Optional[Receipt] = None
    SuccessURL: Optional[str] = None
    FailURL: Optional[str] = None


# any info could be passed to this dictionary: keys up 20 to chars and calues up to 100 char long
class DATA(BaseModel):
    Phone: Optional[str] = None
    Email: Optional[str] = None


class SpentMoney(BaseModel):
    spent_amount: float
    chat_id: int
