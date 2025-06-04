from fastapi import APIRouter
from BackendApp.API.faq.utils import *
from BackendApp.API.faq.schemas import *

from BackendApp.Database.session import DBTransactionStatus
from BackendApp.Middleware.faq_middleware import FAQMiddleware
from BackendApp.Logger import logger, LogLevel

router = APIRouter()

@router.post(path="/faq/create/", tags=["FAQ"])
async def create(request: FAQForCreating):
    try:
        result = await FAQMiddleware.create(**request.model_dump())
        if (result == DBTransactionStatus.SUCCESS):
            id = await FAQMiddleware.get_entity_id(**request.model_dump())
            return {
                "status": "Success",
                "message": f"FAQ with id {id} has been successfully created in the data base"
            }
        elif (result == DBTransactionStatus.ALREADY_EXIST):
            return {
                "status": "Failed",
                "message": f"FAQ with the given parameters already exists in the data base"
            }
        else:
            return {
                "status": "Failed",
                "message": "An error occurred while communicating with the data base"
            }
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR,
            message=f"An error occurred in /faq/create/: {e}",
            module_name="API"
        )

@router.post(path="/faq/update/", tags=["FAQ"])
async def update(request: FAQForUpdating):
    try:
        result = await FAQMiddleware.update(**request.model_dump())
        if (result == DBTransactionStatus.SUCCESS):
            return {
                "status": "Success",
                "message": f"FAQ entity has been successfully updated"
            }
        elif (result == DBTransactionStatus.NOT_EXIST):
            return {
                "status": "Failed",
                "message": f"FAQ with id {request.faq_id} does not exist in the data base"
            }
        else:
            return {
                "status": "Failed",
                "message": "An error occurred while communicating with the data base"
            }
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR,
            message=f"An error occurred in /faq/update/: {e}",
            module_name="API"
        )

@router.delete(path="/faq/delete/{faq_id}", tags=["FAQ"])
async def delete(faq_id: int):
    try:
        result = await FAQMiddleware.delete(faq_id=faq_id)
        if (result == DBTransactionStatus.SUCCESS):
            return {
                "status": "Success",
                "message": f"FAQ entity has been successfully deleted from the data base"
            }
        elif (result == DBTransactionStatus.NOT_EXIST):
            return {
                "status": "Failed",
                "message": f"FAQ with id {faq_id} does not exist in the data base"
            }
        else:
            return {
                "status": "Failed",
                "message": "An error occurred while communicating with the data base"
            }
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR,
            message=f"An error occurred in /faq/delete/: {e}",
            module_name="API"
        )

@router.get(path="/faq/get_by_id/{faq_id}", tags=["FAQ"])
async def get_by_id(faq_id: int):
    try:
        result = await FAQMiddleware.get_by_id(faq_id=faq_id)
        if (result):
            return {
                "status": "Success",
                "message": parse_faq_into_format(result)
            }
        else:
            return {
                "status": "Failed",
                "message": f"FAQ with id {faq_id} does not exist in the data base"
            }
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR,
            message=f"An error occurred in /faq/get_by_id/: {e}",
            module_name="API"
        )

@router.get(path="/faq/get_all/", tags=["FAQ"])
async def get_all():
    try:
        result = await FAQMiddleware.get_all()
        if (result):
            return {
                "status": "Success",
                "message": [parse_faq_into_format(faq) for faq in result]
            }
        else:
            return {
                "status": "Failed",
                "message": "There are no FAQ entities in the data base"
            }
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR,
            message=f"An error occurred in /faq/get_all/: {e}",
            module_name="API"
        )