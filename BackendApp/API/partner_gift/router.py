from fastapi import APIRouter

from BackendApp.API.partner_gift.schemas import *
from BackendApp.API.partner_gift.utils import *
from BackendApp.Database.session import DBTransactionStatus
from BackendApp.Middleware.partner_gift_middleware import PartnerGiftMiddleware
from BackendApp.Logger import logger, LogLevel

router = APIRouter()

@router.post("/partner_gift/create/", tags=["PartnerGift"])
async def create(request: PartnerGiftForCreating):
    try:
        result = await PartnerGiftMiddleware.create(**request.model_dump())
        if (result == DBTransactionStatus.SUCCESS):
            id = await PartnerGiftMiddleware.get_entity_id(**request.model_dump())
            return {
                "Status": "Success",
                "Message": f"Partner gift with id {id} has been successfully created in the data base"
            }
        elif (result == DBTransactionStatus.ALREADY_EXIST):
            return {
                "Status": "Failed",
                "Message": f"Partner gift with the given parameters has already been created in the database"
            }
        else:
            return {
                "Status": "Failed",
                "Message": "An error occurred while communicating with the data base"
            }
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR,
            message=f"An error occurred in /partner_gift/create/: {e}",
            module_name="API"
        )

@router.post("/partner_gift/update/", tags=["PartnerGift"])
async def update(request: PartnerGiftForUpdating):
    try:
        result = await PartnerGiftMiddleware.update(**request.model_dump())
        if (result == DBTransactionStatus.SUCCESS):
            return {
                "Status": "Success",
                "Message": f"Partner gift has been successfully updated in the data base"
            }
        elif (result == DBTransactionStatus.NOT_EXIST):
            return {
                "Status": "Failed",
                "Message": f"Partner gift with the given parameters does not exist in the database"
            }
        else:
            return {
                "Status": "Failed",
                "Message": "An error occurred while communicating with the data base"
            }
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR,
            message=f"An error occurred in /partner_gift/update/: {e}",
            module_name="API"
        )

@router.delete("/partner_gift/delete/{partner_gift_id}", tags=["PartnerGift"])
async def delete(partner_gift_id: int):
    try:
        result = await PartnerGiftMiddleware.delete(partner_gift_id=partner_gift_id)
        if (result == DBTransactionStatus.SUCCESS):
            return {
                "Status": "Success",
                "Message": f"Partner gift has been successfully removed from the data base"
            }
        elif (result == DBTransactionStatus.NOT_EXIST):
            return {
                "Status": "Failed",
                "Message": f"Partner gift with the given parameters does not exist in the database"
            }
        else:
            return {
                "Status": "Failed",
                "Message": "An error occurred while communicating with the data base"
            }
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR,
            message=f"An error occurred in /partner_gift/delete/: {e}",
            module_name="API"
        )

@router.get("/partner_gift/get_all/", tags=["PartnerGift"])
async def get_all():
    try:
        result = await PartnerGiftMiddleware.get_all()
        if (result):
            return {
                "Status": "Success",
                "Message": result
            }
        else:
            return {
                "Status": "Failed",
                "Message": "There are not any partner gifts in the data base now"
            }
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR,
            message=f"An error occurred in /partner_gift/get_all/: {e}",
            module_name="API"
        )

@router.get("/partner_gift/get_by_id/{partner_gift_id}", tags=["PartnerGift"])
async def get_by_id(partner_gift_id: int):
    try:
        result = await PartnerGiftMiddleware.get_by_id(partner_gift_id=partner_gift_id)
        if (result):
            return {
                "Status": "Success",
                "Message": result
            }
        else:
            return {
                "Status": "Failed",
                "Message": f"There are not any partner gifts with the id {partner_gift_id} in the data base now"
            }
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR,
            message=f"An error occurred in /partner_gift/get_by_id/: {e}",
            module_name="API"
        )