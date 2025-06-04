from fastapi import APIRouter
from BackendApp.API.referrals.schemas import *
from BackendApp.API.referrals.utils import *

from BackendApp.Database.Models.referrals_model import Referral
from BackendApp.Middleware.client_middleware import ClientMiddleware
from BackendApp.Middleware.referrals_middleware import ReferralMiddleware
from BackendApp.Database.Models import Client
from BackendApp.Database.session import DBTransactionStatus
from BackendApp.Logger import logger, LogLevel

router = APIRouter()

@router.get("/referrals/get_all_referrals/", tags=["Referrals"])
async def get_all_referrals():
    try:
        result = await ReferralMiddleware.get_all_referrals()
        if (isinstance(result, list)):
            return [
                parse_referral_into_format(referral) for referral in result
            ]
        else:
            return {
                "Status": "Failed",
                "message": "An error occured while communicating with the data base"
            }
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR,
            message=f"An error occurred in /referrals/get_all_referrals/: {e}",
            module_name="API"
        )

@router.get("/referrals/get_all_referrals_by_link/{referral_link}/", tags=["Referrals"])
async def get_all_referrals_by_link(referral_link: str) -> list:
    try:
        result = await ReferralMiddleware.get_all_referrals_by_link(referral_link)
        if (isinstance(result, list)):
            return [
                parse_referral_into_format(referral) for referral in result
            ]
        else:
            return {
                "Status": "Failed",
                "message": "An error occured while communicating with the data base"
            }
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR,
            message=f"An error occurred in /referrals/get_all_referrals_by_link/: {e}",
            module_name="API"
        )

@router.get("/referrals/get_referral/{chat_id}/", tags=["Referrals"])
async def get_referral(chat_id: int):
    try:
        result = await ReferralMiddleware.get_referral(referrer_id=chat_id)
        if (isinstance(result, Referral)):
            return parse_referral_into_format(result)
        elif (result == DBTransactionStatus.NOT_EXIST):
            return {
                "Status": "Failed",
                "message": f"The referral with the chat_id {chat_id} does not exist"
            }
        else:
            return {
                "Status": "Failed",
                "message": "An error occured while communicating with the data base"
            }
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR,
            message=f"An error occurred in /referrals/get_referral/: {e}",
            module_name="API"
        )

@router.get("/referrals/get_referral_got_bonus/{chat_id}/", tags=["Referrals"])
async def get_status(chat_id: int):
    try:
        result = await ReferralMiddleware.get_status(referrer_id=chat_id)
        if (isinstance(result, Referral)):
            return {
                "Status": "Success",
                "message": result
            }
        elif (result == DBTransactionStatus.NOT_EXIST):
            return {
                "Status": "Failed",
                "message": f"The referral with the chat_id {chat_id} does not exist"
            }
        else:
            return {
                "Status": "Failed",
                "message": "An error occured while communicating with the data base"
            }
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR,
            message=f"An error occurred in /referrals/get_referral_got_bonus/: {e}",
            module_name="API"
        )

@router.patch("/referrals/update_referral_got_bonus/{chat_id}/", tags=["Referrals"])
async def update_status(chat_id: int):
    try:
        result = await ReferralMiddleware.update_status(referrer_id=chat_id)
        if (result == DBTransactionStatus.SUCCESS):
            return {
                "Status": "Success",
                "message": f"Referral with chat_id {chat_id} got their field \'got_bonus\' succesfully changed to \'true\'"
            }
        elif (result == DBTransactionStatus.ALREADY_EXIST):
            return {
                "Status": "Failed",
                "message": f"Referral with chat_id {chat_id} has already got their field \'got_bonus\' set to \'true\'"
            }
        else:
            return {
                "Status": "Failed",
                "message": "An error occured while communicating with the data base"
            }
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR,
            message=f"An error occurred in /referrals/update_referral_got_bonus/: {e}",
            module_name="API"
        )