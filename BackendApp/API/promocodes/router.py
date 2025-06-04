import json
from typing import Union
from fastapi import APIRouter

from BackendApp.API.promocodes.schemas import *
from BackendApp.API.promocodes.utils import parse_promocode_into_format
from BackendApp.Database.Models.promocode_model import Promocode as PromocodeModel
from BackendApp.Database.Models.promocode_types import _PromocodeType as PromocodeType
from BackendApp.Database.session import DBTransactionStatus
from BackendApp.Middleware.event_middleware import EventMiddleware
from BackendApp.Middleware.client_middleware import ClientMiddleware
from BackendApp.Middleware.ticket_middleware import TicketMiddleware
from BackendApp.Middleware.promocodes_middleware import PromocodesMiddleware
from BackendApp.TelegramBots.HeadBot.Config.bot import bot
from BackendApp.Logger import logger, LogLevel

router = APIRouter()

@router.post(path="/promocodes/create/", tags=["Promocodes"])
async def create_promocode(promocode: Promocode):
    try:
        result = await PromocodesMiddleware.create(**promocode.model_dump())
        if result == DBTransactionStatus.SUCCESS:
            id = await PromocodesMiddleware.get_entity_id(number=promocode.number)
            return {
                "Status": "Succeeded",
                "Message": f"Promocode with id {id} has been successfully created in the data base"
            }
        else:
            if result == DBTransactionStatus.ALREADY_EXIST:
                return {
                    "Status": "Failed",
                    "Error": f"Promocode with number {promocode.number} already exists in the data base",
                }
            else:
                return {
                    "Status": "Failed",
                    "Error": "An error occurred while communicating with the data base"
                }
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR,
            message=f"An error occurred in /promocodes/create/: {e}",
            module_name="API"
        )

@router.patch(path="/promocodes/update/{number}", tags=["Promocodes"])
async def update_promocode(request: PromocodeUpdateRequest):
    try:
        result = await PromocodesMiddleware.update_promocode(**request.model_dump())
        if result == DBTransactionStatus.SUCCESS:
            return {
                "status": "Succeeded",
                "message": f"Promocode with number {request.number} has been successfully updated"
            }
        elif result == DBTransactionStatus.NOT_EXIST:
            return {
                "Status": "Failed",
                "Error": f"Promocode with number {request.number} doesn't exist in the data base",
            }
        else:
            return {
                "Status": "Failed",
                "Error": "An error occurred while communicating with the data base"
            }
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR,
            message=f"An error occurred in /promocodes/update/: {e}",
            module_name="API"
        )

@router.delete(path="/promocodes/delete/{number}", tags=["Promocodes"])
async def delete_promocode(number: int):
    try:
        result = await PromocodesMiddleware.delete_promocode(number=number)
        if result == DBTransactionStatus.SUCCESS:
            return {
                "Status": "Succeeded"
            }
        else:
            if result == DBTransactionStatus.NOT_EXIST:
                return {
                    "Status": "Failed",
                    "Error": f"Promocode with number {number} doesn't exist in the data base",
                }
            else:
                return {
                    "Status": "Failed",
                    "Error": "An error occurred while communicating with the data base"
                }
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR,
            message=f"An error occurred in /promocodes/delete/: {e}",
            module_name="API"
        )
        
@router.post(path="/promocodes/check_validity/{client_chat_id}/", tags=["Promocodes"])
async def check_promocodes_validity(client_chat_id: int):
    try:
        result = await PromocodesMiddleware.check_promocodes_validity(client_chat_id=client_chat_id)
        if result == DBTransactionStatus.SUCCESS:
            return {
                "Status": "Succeeded",
                "Message": f"Client with chat_id {client_chat_id} promocodes validity has been verified"
            }
        else:
            return {
                "Status": "Failed",
                "Error": "An error occurred while communicating with the data base"
            }
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR,
            message=f"An error occurred in /promocodes/check_validity/: {e}",
            module_name="API"
        )


@router.post(path="/promocodes/get_user_promocodes/{client_chat_id}/", tags=["Promocodes"])
async def get_user_promocodes(client_chat_id: int):
    try:
        result = await PromocodesMiddleware.get_user_promocodes(client_chat_id=client_chat_id)
        if result is not None:
            return [parse_promocode_into_format(promocode) for promocode in result]
        else:
            return {
                "Status": "Failed",
                "Error": f"The user with chat_id {client_chat_id} doesn't have any promocodes yet",
            }
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR,
            message=f"An error occurred in /promocodes/get_user_promocodes/: {e}",
            module_name="API"
        )


@router.get(path="/promocodes/get_all_promocodes/", tags=["Promocodes"])
async def get_all_promocodes():
    try:
        result = await PromocodesMiddleware.get_all_promocodes()
        if result != DBTransactionStatus.NOT_EXIST:
            return [parse_promocode_into_format(promocode) for promocode in result]
        else:
            return {
                "Status": "Failed",
                "Error": f"There aren't any promocodes yet"
            }
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR,
            message=f"An error occurred in /promocodes/get_all_promocodes/: {e}",
            module_name="API"
        )


@router.post(path="/promocodes/get_promocode_by_id/{promocode_id}/", tags=["Promocodes"])
async def get_promocode_by_id(promocode_id: int):
    try:
        result = await PromocodesMiddleware.get_promocode_by_id(promocode_id)
        if result != DBTransactionStatus.NOT_EXIST:
            return parse_promocode_into_format(result)
        else:
            return {
                "Status": "Failed",
                "Error": f"There isn't a promocode with promocode_id {promocode_id}",
            }
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR,
            message=f"An error occurred in /promocodes/get_promocode_by_id/: {e}",
            module_name="API"
        )


@router.get(path="/promocodes/get_free_promocodes/", tags=["Promocodes"])
async def get_free_promocodes():
    try:
        result = await PromocodesMiddleware.get_free_promocodes()
        if result != DBTransactionStatus.NOT_EXIST:
            return [parse_promocode_into_format(promocode) for promocode in result]
        else:
            return {
                "Status": "Failed",
                "Error": f"There aren't any free promocodes yet"
            }
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR,
            message=f"An error occurred in /promocodes/get_free_promocodes/: {e}",
            module_name="API"
        )


@router.patch(path="/promocodes/add_client_to_promocode/", tags=["Promocodes"])
async def add_client_to_promocode(request: PromocodeRequest):
    try:
        result = await PromocodesMiddleware.add_client_to_promocode(
            **request.model_dump()
        )
        if (result == DBTransactionStatus.SUCCESS):
            return {
                "Status": "Succeeded"
            }
        elif (result == DBTransactionStatus.NOT_EXIST):
            return {
                "Status": "Failed",
                "Error": f"Promocode with number {request.number} doesn't exist in the data base",
            }
        elif (result == DBTransactionStatus.ALREADY_EXIST):
            return {
                "Status": "Failed",
                "Error": f"Client with client_chat_id {request.client_chat_id} has already been tied to promocode with number {request.number}",
            }
        else:
            return {
                "Status": "Failed",
                "Error": "An error occurred while communicating with the data base",
            }
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR,
            message=f"An error occurred in /promocodes/add_client_to_promocode/: {e}",
            module_name="API"
        )

@router.patch(path="/promocodes/activate_promocode/{number}/", tags=["Promocodes"])
async def activate_promocode(number: int):
    try:
        is_valid = await PromocodesMiddleware.validate_promocode_by_number(number=number)
        if (is_valid == True):
            result = await PromocodesMiddleware.activate_promocode(number)
            if (result == DBTransactionStatus.SUCCESS):
                promocode = await PromocodesMiddleware.get_by_number(number=number)

                if (promocode.type == PromocodeType.FREE_EVENT_TICKET):
                    event_id = int(promocode.operational_info)
                    chat_id = promocode.client_chat_id
                    is_purchased = await TicketMiddleware.purchase_ticket(
                        event_id=event_id,
                        client_chat_id=chat_id
                    )
                    if (not is_purchased):
                        return {
                            "status": "Failed",
                            "message": f"Failed to buy a ticket for the client with chat_id {chat_id} on the event with id {event_id}"
                        }
                    
                    event = await EventMiddleware.get_event_by_id(event_id=event_id)
                    await bot.send_message(
                        chat_id=chat_id,
                        text=f"✅ Вам успешно был выдан билет за промокод на платное мероприятие \"{event.short_name}\""
                    )
                    
                elif (promocode.type == PromocodeType.PARTY_WITHOUT_DEPOSIT):
                    event_id = int(promocode.operational_info)
                    chat_id = promocode.client_chat_id
                    is_purchased = await TicketMiddleware.purchase_ticket(
                        event_id=event_id,
                        client_chat_id=chat_id
                    )
                    if (not is_purchased):
                        return {
                            "status": "Failed",
                            "message": f"Failed to buy a ticket for the client with chat_id {chat_id} on the event with id {event_id}"
                        }
                    
                    event = await EventMiddleware.get_event_by_id(event_id=event_id)
                    await bot.send_message(
                        chat_id=chat_id,
                        text=f"✅ Вам успешно был выдан билет за промокод на депозитное мероприятие \"{event.short_name}\""
                    )
                elif (promocode.type == PromocodeType.REFILLING_BALANCE):

                    is_refilled = await ClientMiddleware.refill_balance(
                        chat_id=promocode.client_chat_id,
                        amount=float(promocode.operational_info)
                    )
                    if (is_refilled != DBTransactionStatus.SUCCESS):
                        return {
                            "status": "Failed",
                            "message": f"An error occurred while refilling the balance of the client with chat_id {promocode.client_chat_id}"
                        }

                await PromocodesMiddleware.update_activation_time(number=number)
                await bot.send_message(
                    chat_id=promocode.client_chat_id,
                    text=f"✅ Промокод с названием {promocode.name} был успешно активирован у вас"
                )

                return {
                    "Status": "Succeeded"
                }
            else:
                return {
                    "Status": "Failed",
                    "Error": "An error occurred while communicating with the data base",
                }
        elif (is_valid == False):
            await PromocodesMiddleware.activate_promocode(number)

            return {
                "Status": "Failed",
                "Message": f"Promocode with number {number} has been expired"
            }

        else:
            return {
                "Status": "Failed",
                "Error": f"Promocode with number {number} doesn't exist in the data base",
            }
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR,
            message=f"An error occurred in /promocodes/activate_promocode/: {e}",
            module_name="API"
        )

@router.patch(path="/promocodes/activate_promocode_by_hash/{hashcode}/", tags=["Promocodes"])
async def activate_promocode_by_hashcode(hashcode: str):
    try:
        is_valid = await PromocodesMiddleware.validate_promocode_by_hashcode(hashcode=hashcode)
        if (is_valid == True):
            result = await PromocodesMiddleware.activate_promocode_by_hashcode(hashcode)
            if (result == DBTransactionStatus.SUCCESS):
                promocode = await PromocodesMiddleware.get_promocode_by_hashcode(hashcode=hashcode)

                await PromocodesMiddleware.update_activation_time(number=promocode.number)
                await bot.send_message(
                    chat_id=promocode.client_chat_id,
                    text=f"✅ Промокод с названием {promocode.name} был успешно активирован у вас"
                )

                return {
                    "Status": "Succeeded"
                }
            else:
                return {
                    "Status": "Failed",
                    "Error": "An error occurred while communicating with the data base",
                }
        elif (is_valid == False):
            await PromocodesMiddleware.activate_promocode_by_hashcode(hashcode)

            return {
                "Status": "Failed",
                "Message": f"Promocode with hashcode {hashcode} has been expired"
            }

        else:
            return {
                "Status": "Failed",
                "Error": f"Promocode with hashcode {hashcode} doesn't exist in the data base",
            }
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR,
            message=f"An error occurred in /promocodes/activate_promocode_by_hash/: {e}",
            module_name="API"
        )

@router.post(path="/promocodes/get_promocode_by_hashcode/{hashcode}/", tags=["Promocodes"])
async def get_promocode_by_hashcode(hashcode: str):
    try:
        result = await PromocodesMiddleware.get_promocode_by_hashcode(hashcode=hashcode)
        if (isinstance(result, PromocodeModel)):
            return parse_promocode_into_format(result)
        else:
            return {
                "Status": "Failed",
                "Error": f"Promocode with hashcode {hashcode} does not exist",
            }
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR,
            message=f"An error occurred in /promocodes/get_promocode_by_hashcode/: {e}",
            module_name="API"
        )
