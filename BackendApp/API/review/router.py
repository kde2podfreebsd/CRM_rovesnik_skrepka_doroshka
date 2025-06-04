from fastapi import APIRouter
from BackendApp.API.review.schemas import *
from BackendApp.API.review.utils import *

from BackendApp.Database.session import DBTransactionStatus
from BackendApp.Database.Models.review_model import Review
from BackendApp.Middleware.review_middleware import ReviewMiddleware
from BackendApp.Logger import logger, LogLevel

router = APIRouter()

@router.post("/review/create/", tags=["Review"])
async def create(request: ReviewMold):
    try:
        result = await ReviewMiddleware.create(**request.model_dump())
        if (result == DBTransactionStatus.SUCCESS):
            id = await ReviewMiddleware.get_entity_id(**request.model_dump())
            return {
                "Status": "Success",
                "Message": f"Review with id {id} has been succesfully created in the data base"
            }
        else:
            return {
                "Status": "Failed",
                "Message": "An error occured while communicating with the data base"
            }
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR,
            message=f"An error occurred in /review/create/: {e}",
            module_name="API"
        )

@router.delete("/review/delete/{review_id}", tags=["Review"])
async def delete(review_id: int):
    try:
        result = await ReviewMiddleware.delete(review_id=review_id)
        if (result == DBTransactionStatus.SUCCESS):
            return {
                "Status": "Success",
                "Message": f"Review has been succesfully removed from the data base"
            }
        elif (result == DBTransactionStatus.NOT_EXIST):
            return {
                "Status": "Failed",
                "Message": f"Review with review_id {review_id} does not exist in the data base"
            }
        else:
            return {
                "Status": "Failed",
                "Message": "An error occured while communicating with the data base"
            }
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR,
            message=f"An error occurred in /review/delete/: {e}",
            module_name="API"
        )

@router.get("/review/get_all/", tags=["Review"])
async def get_all():
    try:
        result = await ReviewMiddleware.get_all()
        if (result):
            return {
                "Status": "Success",
                "Message": [parse_review_into_format(review) for review in result]
            }
        else:
            return {
                "Status": "Failed",
                "Message": "There are not any reviews in the data base"
            }
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR,
            message=f"An error occurred in /review/get_all/: {e}",
            module_name="API"
        )

@router.get("/review/get_by_id/{review_id}", tags=["Review"])
async def get_by_id(review_id: int):
    try:
        result = await ReviewMiddleware.get_by_id(review_id=review_id)
        if (result):
            return {
                "Status": "Success",
                "Message": result
            }
        else:
            return {
                "Status": "Failed",
                "Message": f"There is not a review with the review_id {review_id} in the data base"
            }
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR,
            message=f"An error occurred in /review/get_by_id/: {e}",
            module_name="API"
        )

@router.post("/review/get_by_chat_id_and_bar_id/", tags=["Review"])
async def get_by_chat_id_and_bar_id(request: GetByChatAndBarIdsRequest):
    try:
        result = await ReviewMiddleware.get_by_chat_id_and_bar_id(**request.model_dump())
        if (result):
            return {
                "Status": "Success",
                "Message": result
            }
        else:
            return {
                "Status": "Failed",
                "Message": f"The client with chat_id {request.chat_id} has not left a review on the bar with bar_id {request.bar_id}"
            }
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR,
            message=f"An error occurred in /review/get_by_chat_id_and_bar_id/: {e}",
            module_name="API"
        )

@router.post("/review/get_by_chat_id_and_event_id/", tags=["Review"])
async def get_by_chat_id_and_event_id(request: GetByChatAndEventIdsRequest):
    try:
        result = await ReviewMiddleware.get_by_chat_id_and_event_id(**request.model_dump())
        if (result):
            return {
                "Status": "Success",
                "Message": result
            }
        else:
            return {
                "Status": "Failed",
                "Message": f"The client with chat_id {request.chat_id} has not left a review on the event with event_id {request.event_id}"
            }
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR,
            message=f"An error occurred in /review/get_by_chat_id_and_event_id/: {e}",
            module_name="API"
        )

@router.get("/reviews/{chat_id}", tags=["Review"])
async def get_by_chat_id(chat_id: int):
    try:
        result = await ReviewMiddleware.get_by_chat_id(chat_id=chat_id)
        if (result):
            return {
                "Status": "Success",
                "Message": result
            }
        else:
            return {
                "Status": "Failed",
                "Message": f"There are not any reviews for the client with chat_id {chat_id} in the data base"
            }
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR,
            message=f"An error occurred in /reviews/: {e}",
            module_name="API"
        )