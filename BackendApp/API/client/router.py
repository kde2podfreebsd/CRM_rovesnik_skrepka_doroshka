from fastapi import APIRouter

from BackendApp.API.client.schemas import *
from BackendApp.API.client.utils import *
from BackendApp.Database.Models import Client
from BackendApp.IIKO.api import Client as ClientIIKO
from BackendApp.Database.session import DBTransactionStatus
from BackendApp.Middleware.client_middleware import ClientMiddleware
from BackendApp.Logger import logger, LogLevel

from datetime import datetime, timedelta
from dotenv import load_dotenv
import json
import re
import os

load_dotenv()

API_LOGIN = os.getenv("API_LOGIN")
CONTEXT_MANAGER = os.getcwd() + "/BackendApp/API/client/context_manager.json"

router = APIRouter()

@router.get(path="/client/{chat_id}/", tags=["Client"])
async def get_client(chat_id: int) -> ClientForReturn:
    try:
        result = await ClientMiddleware.get_client(chat_id=chat_id)
        if isinstance(result, Client):
            client_iiko = await ClientIIKO.create(API_LOGIN, "Rovesnik")
            iiko_user = await client_iiko.get_customer_info(id=result.iiko_id)
            balance = iiko_user.walletBalances[0]["balance"]
            loyalty_info = await client_iiko.get_customer_loyalty_info(result.iiko_id)

            return parse_client_into_format(client=result, balance=balance, loyalty_info=loyalty_info)
        else:
            return {"message": f"Client with {chat_id} doesn't exist"}
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR,
            message=f"An error occurred in /client/: {e}",
            module_name="API"
        )


@router.post(path="/client/refill_balance/", tags=["Client"])
async def refill_balance(payload: RefillRequest):
    try:
        result = await ClientMiddleware.refill_balance(**payload.model_dump())
        if result == DBTransactionStatus.SUCCESS:
            return {
                "status": "Success",
                "message": f"Client's balance with chat_id {payload.chat_id} has been succesfully refilled by {payload.amount}"
            }
        elif result == DBTransactionStatus.NOT_EXIST:
            return {
                "status": "Failed",
                "message": f"Client with chat_id {payload.chat_id} does not exist"
            }
        elif result == "Not enough balance":
            return {
                "status": "Failed",
                "message": f"There are not enough points on the client's profile"
            }
        else:
            return {
                "status": "Failed",
                "message": "An error occured while interacting with the data base"
            }
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR,
            message=f"An error occurred in /client/refill_balance/: {e}",
            module_name="API"
        )


@router.get(path="/client/get_referral_link/{chat_id}/", tags=["Client"])
async def get_referral_link(chat_id: int):
    try:
        result = await ClientMiddleware.get_referral_link(chat_id=chat_id)
        if isinstance(result, str):
            return {"Status": "Success", "message": result}
        elif result == DBTransactionStatus.NOT_EXIST:
            return {
                "Status": "Failed",
                "message": f"Client with chat_id {chat_id} does not exist",
            }
        else:
            return {
                "Status": "Failed",
                "message": "An error occured while communicating with the data base",
            }
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR,
            message=f"An error occurred in /client/get_referral_link/: {e}",
            module_name="API"
        )


@router.get(path="/client/get_client_by_ref_link/{referral_link}/", tags=["Client"])
async def get_client_by_ref_link(referral_link: str) -> ClientForReturn:
    try:
        result = await ClientMiddleware.get_client_by_ref_link(
            referral_link=referral_link
        )
        if isinstance(result, Client):
            client_iiko = await ClientIIKO.create(API_LOGIN, "Rovesnik")
            iiko_user = await client_iiko.get_customer_info(id=result.iiko_id)
            balance = iiko_user.walletBalances[0]["balance"]
            loyalty_info = await client_iiko.get_customer_loyalty_info(result.iiko_id)

            return parse_client_into_format(client=result, balance=balance, loyalty_info=loyalty_info)
        else:
            return {
                "Status": "Failed",
                "message": f"Client with {referral_link} doesn't exist",
            }
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR,
            message=f"An error occurred in /client/get_client_by_ref_link/: {e}",
            module_name="API"
        )


@router.get(path="/client/get_client_by_iiko_id/{iiko_id}/", tags=["Client"])
async def get_client_by_iiko_id(iiko_id: str) -> ClientForReturn:
    try:
        result = await ClientMiddleware.get_client_by_iiko_id(iiko_id=iiko_id)
        if isinstance(result, Client):
            client_iiko = await ClientIIKO.create(API_LOGIN, "Rovesnik")
            iiko_user = await client_iiko.get_customer_info(id=result.iiko_id)
            balance = iiko_user.walletBalances[0]["balance"]
            loyalty_info = await client_iiko.get_customer_loyalty_info(result.iiko_id)

            return parse_client_into_format(client=result, balance=balance, loyalty_info=loyalty_info)
        else:
            if result == DBTransactionStatus.NOT_EXIST:
                return {
                    "Status": "Failed",
                    "message": f"Client with chat_id {iiko_id} does not exist",
                }
            else:
                return {
                    "Status": "Failed",
                    "message": "An error occured while communicating with the data base",
                }
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR,
            message=f"An error occurred in /client/get_client_by_iiko_id/: {e}",
            module_name="API"
        )


@router.get(path="/client/get_client_by_iiko_card/{iiko_card}/", tags=["Client"])
async def get_client_by_iiko_card(iiko_card: str) -> ClientForReturn:
    try:
        result = await ClientMiddleware.get_client_by_iiko_card(
            iiko_card=iiko_card
        )
        if isinstance(result, Client):
            client_iiko = await ClientIIKO.create(API_LOGIN, "Rovesnik")
            iiko_user = await client_iiko.get_customer_info(id=result.iiko_id)
            balance = iiko_user.walletBalances[0]["balance"]
            loyalty_info = await client_iiko.get_customer_loyalty_info(result.iiko_id)

            return parse_client_into_format(client=result, balance=balance, loyalty_info=loyalty_info)
        else:
            if result == DBTransactionStatus.NOT_EXIST:
                return {
                    "Status": "Failed",
                    "message": f"Client with chat_id {iiko_card} does not exist",
                }
            else:
                return {
                    "Status": "Failed",
                    "message": "An error occured while communicating with the data base",
                }
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR,
            message=f"An error occurred in /client/get_client_by_iiko_card/: {e}",
            module_name="API"
        )

@router.get(path="/clients/get_all/", tags=["Client"])
async def get_all_clients():
    try:
        clients = await ClientMiddleware.get_all_clients()
        if clients != DBTransactionStatus.NOT_EXIST:
            client_iiko = await ClientIIKO.create(API_LOGIN, "Rovesnik")
            result = []
            for client in clients:
                iiko_user = await client_iiko.get_customer_info(id=client.iiko_id)
                balance = iiko_user.walletBalances[0]["balance"]
                loyalty_info = await client_iiko.get_customer_loyalty_info(client.iiko_id)
                result.append(parse_client_into_format(
                        client=client, 
                        balance=balance, 
                        loyalty_info=loyalty_info
                    )
                )
            return {
                "Status": "Success",
                "message": result
            }
        else:
            return {
                "Status": "Failed",
                "message": f"There are no clients in the data base",
            }
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR,
            message=f"An error occurred in /client/get_all/: {e}",
            module_name="API"
        )

@router.get(path="/clients/get_all_chat_id_and_username/", tags=["Client"])
async def get_all_clients_chat_id_and_username():
    try:
        clients = await ClientMiddleware.get_all_clients()
        if clients != DBTransactionStatus.NOT_EXIST:
            result = []
            for client in clients:
                result.append(parse_client_chat_id_and_username(client=client))
            return {
                "Status": "Success",
                "message": result
            }
        else:
            return {
                "Status": "Failed",
                "message": f"There are no clients in the data base",
            }
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR,
            message=f"An error occurred in /client/get_all_chat_id_and_username/: {e}",
            module_name="API"
        )
       

@router.patch(path="/client/update_phone/", tags=["Client"])
async def update_phone(request: UpdatePhoneRequest):
    try:
        pattern = r"\+7\d{10}"
        if (not re.match(pattern, request.phone)):
            return {
                "status": "Failed",
                "message": "Incorrect format of the phone number, it should be passed as: +7xxxxxxxxxx"
            }
        result = await ClientMiddleware.update_phone(**request.model_dump())
        if (result == DBTransactionStatus.SUCCESS):
            return {
                "status": "Success",
                "message": f"Client's phone with chat_id {request.chat_id} has been succesfully updated"
            }
        elif (result == DBTransactionStatus.NOT_EXIST):
            return {
                "status": "Failed",
                "message": f"Client's with chat_id {request.chat_id} does not exist"
            }
        else:
            return {
                "status": "Failed",
                "message": "An error occured while interacting with the data base"
            }
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR,
            message=f"An error occurred in /client/update_phone/: {e}",
            module_name="API"
        )

@router.patch(path="/client/update_first_name/", tags=["Client"])
async def update_first_name(request: UpdateFirstNameRequest):
    try:
        result = await ClientMiddleware.update_first_name(**request.model_dump())
        if (result == DBTransactionStatus.SUCCESS):
            return {
                "status": "Success",
                "message": f"Client's first name with chat_id {request.chat_id} has been succesfully updated"
            }
        elif (result == DBTransactionStatus.NOT_EXIST):
            return {
                "status": "Failed",
                "message": f"Client's with chat_id {request.chat_id} does not exist"
            }
        else:
            return {
                "status": "Failed",
                "message": "An error occured while interacting with the data base"
            }
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR,
            message=f"An error occurred in /client/update_first_name/: {e}",
            module_name="API"
        )
    
@router.patch(path="/client/update_last_name/", tags=["Client"])
async def update_last_name(request: UpdateLastNameRequest):
    try:
        result = await ClientMiddleware.update_last_name(**request.model_dump())
        if (result == DBTransactionStatus.SUCCESS):
            return {
                "status": "Success",
                "message": f"Client's last name with chat_id {request.chat_id} has been succesfully updated"
            }
        elif (result == DBTransactionStatus.NOT_EXIST):
            return {
                "status": "Failed",
                "message": f"Client's with chat_id {request.chat_id} does not exist"
            }
        else:
            return {
                "status": "Failed",
                "message": "An error occured while interacting with the data base"
            }
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR,
            message=f"An error occurred in /client/update_last_name/: {e}",
            module_name="API"
        )

@router.patch(path="/client/update_reserve_table/{chat_id}", tags=["Client"])
async def update_reserve_table(chat_id: int):
    try:
        result = await ClientMiddleware.update_reserve_table(chat_id=chat_id)
        if (result == DBTransactionStatus.SUCCESS):
            return {
                "status": "Success",
                "message": f"Client's ability to reserve tables with chat_id {chat_id} has been succesfully updated"
            }
        elif (result == DBTransactionStatus.NOT_EXIST):
            return {
                "status": "Failed",
                "message": f"Client's with chat_id {chat_id} does not exist"
            }
        else:
            return {
                "status": "Failed",
                "message": "An error occured while interacting with the data base"
            }
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR,
            message=f"An error occurred in /client/update_reserve_table/: {e}",
            module_name="API"
        )

@router.patch(path="/client/update_change_reservation/{chat_id}", tags=["Client"])
async def update_change_reservation(chat_id: int):
    try:
        result = await ClientMiddleware.update_change_reservation(chat_id=chat_id)
        if (result == DBTransactionStatus.SUCCESS):
            return {
                "status": "Success",
                "message": f"Client's ability to update reservations with chat_id {chat_id} has been succesfully updated"
            }
        elif (result == DBTransactionStatus.NOT_EXIST):
            return {
                "status": "Failed",
                "message": f"Client's with chat_id {chat_id} does not exist"
            }
        else:
            return {
                "status": "Failed",
                "message": "An error occured while interacting with the data base"
            }
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR,
            message=f"An error occurred in /client/update_change_reservation/: {e}",
            module_name="API"
        )

@router.get(path="/client/get_referral_link/{chat_id}/", tags=["Client"])
async def get_referral_link(chat_id: int):
    try:
        result = await ClientMiddleware.get_referral_link(chat_id=chat_id)
        if isinstance(result, str):
            return {"Status": "Success", "message": result}
        elif result == DBTransactionStatus.NOT_EXIST:
            return {
                "Status": "Failed",
                "message": f"Client with chat_id {chat_id} does not exist",
            }
        else:
            return {
                "Status": "Failed",
                "message": "An error occured while communicating with the data base",
            }
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR,
            message=f"An error occurred in /client/get_referral_link/: {e}",
            module_name="API"
        )

@router.post(path="/client/send_shipping_query/", tags=["Client"])
async def send_shipping_query(request: SendShippingQueryRequest):
    try:
        result = await ClientMiddleware.send_shipping_query(**request.model_dump())

        if not isinstance(result, Exception):
            res_data = []
            try:
                with open(CONTEXT_MANAGER, "r", encoding="utf-8") as infile:
                    data = json.load(infile)
            except json.JSONDecodeError:
                data = []
            
            for chunk in data:
                res_data.append(chunk)
            now = datetime.now() + timedelta(hours=3)
            res_data.append(
                {
                    "msg_id": result.id,
                    "chat_id": result.chat.id,
                    "datetime": now.strftime("%Y-%m-%d %H:%M:%S")
                }
            )
            with open(CONTEXT_MANAGER, "w", encoding="utf-8") as outfile:
                json.dump(res_data, outfile, indent=4, ensure_ascii=False)
            return {
                "Status": "Success", 
                "message": f"Shipping query for reservation for more than 10 clients has been sent to the client with chat_id {request.chat_id}"
            }
        else:
            return {
                "Status": "Failed",
                "message": f"An error occured while sending a shipping query to the client: {result}",
            }
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR,
            message=f"An error occurred in /client/send_shipping_query/: {e}",
            module_name="API"
        )

@router.get(path="/clients/username/", tags=["Client"])
async def get_all_clients_username():
    try:
        clients = await ClientMiddleware.get_all_clients()
        if clients != DBTransactionStatus.NOT_EXIST:
            result = []
            for client in clients:
                result.append(client.username)
            return {
                "Status": "Success",
                "message": result
            }
        else:
            return {
                "Status": "Failed",
                "message": f"There are no clients in the data base",
            }
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR,
            message=f"An error occurred in /clients/username/: {e}",
            module_name="API"
        )