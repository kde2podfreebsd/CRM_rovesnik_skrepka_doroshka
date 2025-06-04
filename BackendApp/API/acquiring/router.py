from fastapi import APIRouter

from BackendApp.acquiring.tinkoff_api import *
from BackendApp.acquiring.tinkoff_api_spb import *
from BackendApp.API.acquiring.schemas import *
from BackendApp.API.acquiring.utils import *
from BackendApp.Database.DAL.client_dal import ClientDAL
from BackendApp.Database.session import DBTransactionStatus, async_session
from BackendApp.Middleware.loyalty_middleware import LoyaltyMiddleware
from BackendApp.Logger import logger, LogLevel

router = APIRouter()


@router.post(path="/acquiring/init_tx/", tags=["Acquiring"])
async def init_common_transaction(tx: Transaction) -> Union[str, dict]:
    try:
        response = await MerchantService.init_transaction(tx.model_dump())
        response = response.json()
        if response["Success"]:
            return response
        return {"error": response}
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR,
            message=f"An error occurred in /acquiring/init_tx/: {e}",
            module_name="API"
        )


@router.post(path="/acquiring/cancel_tx/", tags=["Acquiring"])
async def cancel_transaction(tx: Transaction) -> Union[str, dict]:
    try:
        response = await MerchantService.cancel_transaction(tx.model_dump())
        response = response.json()
        if response["Success"]:
            return response
        return {"message": response}
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR,
            message=f"An error occurred in /acquiring/cancel/: {e}",
            module_name="API"
        )


@router.post(path="/acquiring/get_payment_status/{payment_id}/", tags=["Acquiring"])
async def get_payment_status(payment_id: int) -> Union[str, dict]:
    try:
        response = await MerchantService.get_payment_status(payment_id)
        response = response.json()
        if response["Success"]:
            return response
        return {"message": response}
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR,
            message=f"An error occurred in /acquiring/get_payment_status/: {e}",
            module_name="API"
        )


@router.post(path="/acquiring/get_payment_status/{order_id}", tags=["Acquiring"])
async def get_order_status(order_id: int) -> Union[str, dict]:
    try:
        response = await MerchantService.get_order_status(order_id)
        response = response.json()
        if response["Success"]:
            return response
        return {"message": response}
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR,
            message=f"An error occurred in /acquiring/get_payment_status/: {e}",
            module_name="API"
        )


@router.post(path="/acquiring/send_closing_receipt/", tags=["Acquiring"])
async def send_receipt(tx: Transaction):
    try:
        response = await MerchantService.send_receipt(tx.model_dump())
        response = response.json()
        if response["Success"]:
            return response
        return {"message": response}
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR,
            message=f"An error occurred in /acquiring/send_closing_receipt/: {e}",
            module_name="API"
        )


@router.post(path="/acquiring/init_widget_tx/", tags=["Acquiring"])
async def init_widget_transaction(tx: Transaction):
    try:
        response = await MerchantServiceSpb.init_widget_transaction(tx.model_dump())
        response = response.json()
        if response["Success"]:
            return response
        return {"message": response}
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR,
            message=f"An error occurred in /acquiring/init_widget_tx/: {e}",
            module_name="API"
        )


@router.post(path="/acquiring/get_qr/{payment_id}/", tags=["Acquiring"])
async def get_qr(payment_id: int) -> Union[str, dict]:
    try:
        response = await MerchantServiceSpb.get_qr(payment_id)
        response = response.json()
        if response["Success"]:
            return response["Data"]
        return {"message": response}
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR,
            message=f"An error occurred in /acquiring/get_qr/: {e}",
            module_name="API"
        )


@router.post(path="/acquiring/get_users_bank_qr/{payment_id}/", tags=["Acquiring"])
async def get_users_bank_qr(payment_id: int) -> Union[str, dict]:
    try:
        response = await MerchantServiceSpb.get_users_bank_qr(payment_id)
        response = response.json()
        if response["Success"]:
            return response
        return {"message": response}
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR,
            message=f"An error occurred in /acquiring/get_users_bank_qr/: {e}",
            module_name="API"
        )


@router.post(path="/acquiring/get_qr_state/{payment_id}/", tags=["Acquiring"])
async def get_qr_state(payment_id: int) -> Union[str, dict]:
    try:
        response = await MerchantServiceSpb.get_qr_state(payment_id)
        response = response.json()
        if response["Success"]:
            return response
        return {"message": response}
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR,
            message=f"An error occurred in /acquiring/get_qr_state/: {e}",
            module_name="API"
        )


@router.post(path="/acquiring/get_account_qr_list/{payment_id}/", tags=["Acquiring"])
async def get_account_qr_list(payment_id: int) -> Union[str, dict]:
    try:
        response = await MerchantServiceSpb.get_account_qr_list(payment_id)
        response = response.json()
        if response["Success"]:
            return response["AccountTokens"]
        return {"message": response}
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR,
            message=f"An error occurred in /acquiring/get_account_qr_list/: {e}",
            module_name="API"
        )


@router.post(path="/acquiring/get_add_account_qr_state/{payment_id}/", tags=["Acquiring"])
async def get_add_account_qr_state(payment_id: int) -> Union[str, dict]:
    try:
        response = await MerchantServiceSpb.get_add_account_qr_state(payment_id)
        response = response.json()
        if response["Success"]:
            return response
        return {"message": response}
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR,
            message=f"An error occurred in /acquiring/get_add_account_qr_state/: {e}",
            module_name="API"
        )


@router.post(path="/acquiring/handle_spent_money/", tags=["Acquiring"])
async def handle_spent_money(request: SpentMoney):
    """Использовать после успешной опалаты эквайрингом для обновления лояльности юзера."""
    try:
        async with async_session() as session:
            client_dal = ClientDAL(session)

            response = await client_dal.update_spend_money(
                chat_id=request.chat_id, spend_money=request.spent_amount
            )
        await LoyaltyMiddleware.check_client_level(request.chat_id)
        if response == DBTransactionStatus.SUCCESS:
            return {"Success": True}
        else:
            return {"Success": False}
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR,
            message=f"An error occurred in /acquiring/handle_spent_money/: {e}",
            module_name="API"
        )
