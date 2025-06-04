from typing import List, Optional, Union
from uuid import UUID

from fastapi import APIRouter
from pydantic import BaseModel

from BackendApp.Database.DAL.client_dal import ClientDAL
from BackendApp.Database.session import async_session
from BackendApp.Middleware.loyalty_middleware import LoyaltyMiddleware
from BackendApp.Middleware.ticket_middleware import TicketMiddleware

router = APIRouter()


class Transaction(BaseModel):
    sum: float
    balance: float
    orderId: Optional[UUID]
    orderNumber: Optional[str]
    isDelivery: Optional[bool]
    terminalGroupId: Optional[UUID]
    walletId: UUID
    id: UUID
    organizationId: UUID
    uocId: UUID
    notificationType: int
    customerId: UUID
    phone: str
    transactionType: str
    subscriptionPassword: Optional[str]
    changedOn: str
