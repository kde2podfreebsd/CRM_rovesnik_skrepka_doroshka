from fastapi import APIRouter

from BackendApp.API.client_action_log.utils import *
from BackendApp.API.client_action_log.schemas import *
from BackendApp.Middleware.client_log_middleware import ClientLogMiddleware
from BackendApp.Logger import logger, LogLevel

router = APIRouter()

@router.post(path="/client_log/get_by_chat_id/{chat_id}", tags=["ClientLog"])
async def get_by_chat_id(chat_id: int):
    try:
        result = await ClientLogMiddleware.get_by_chat_id(chat_id=chat_id)
        if (result):
            return {
                "status": "Success",
                "message": [parse_log_into_format(log) for log in result]
            }
        else:
            return {
                "Status": "Failed",
                "Error": f"The client with chat_id {chat_id} has not done any actions in the bots",
            }
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR,
            message=f"An error occurred in /client_log/get_by_chat_id/: {e}",
            module_name="API"
        )
        