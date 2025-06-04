from BackendApp.Database.session import DBTransactionStatus
from BackendApp.Middleware.transaction_middleware import TransactionMiddleware
from BackendApp.API.transaction.schemas import *
from BackendApp.API.transaction.utils import *
from BackendApp.Logger import logger, LogLevel

from datetime import datetime
from typing import Union, List
from fastapi import APIRouter

router = APIRouter()

@router.post("/transaction/create/", tags=["Transaction"])
async def create(request: TransactionRequest):
    try:
        result = await TransactionMiddleware.create_tx(**request.model_dump())
        if (result == DBTransactionStatus.SUCCESS):
            return {
                "status": "Success",
                "message": "Transaction has been succesfully created"
            }
        else:
            return {
                "status": "Failed",
                "message": "An error occurred while interacting with the data base"
            }
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR,
            message=f"An error occurred in /transaction/create/: {e}",
            module_name="API"
        )

@router.get("/transactions/{chat_id}", tags=["Transaction"])
async def get_all_tx_by_chat_id(chat_id: int):
    try:
        result = await TransactionMiddleware.get_all_tx(client_chat_id=chat_id)
        if (result):
            return {
                "status": "Success",
                "message": [parse_tx_into_format(tx) for tx in result]
            }
        else:
            return {
                "status": "Failed",
                "message": f"There are no transaction for the client with chat_id {chat_id}"
            }
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR,
            message=f"An error occurred in /transactions/: {e}",
            module_name="API"
        )