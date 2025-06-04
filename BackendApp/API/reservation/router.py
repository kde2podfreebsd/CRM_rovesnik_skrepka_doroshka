from fastapi import APIRouter

from BackendApp.API.reservation.schemas import *
from BackendApp.API.reservation.utils import *
from BackendApp.Middleware.reservation_middleware import ReservationMiddleware, ReservationResponse
from BackendApp.Middleware.table_middleware import TableMiddleware
from BackendApp.Middleware.bar_middleware import BarMiddleware
from BackendApp.Database.session import DBTransactionStatus
from BackendApp.TelegramBots.HeadBot.Config.bot import bot
from BackendApp.Logger import logger, LogLevel

from datetime import datetime, timedelta
from telebot import types

router = APIRouter()

ROVESNIK_MY_RESERVATIONS = "https://rovesnik-bot.online/rovesnik/my/reservations/"
SKREPKA_MY_RESERVATIONS = "https://rovesnik-bot.online/skrepka/my/reservations/"
DOROSHKA_MY_RESERVATIONS = "https://rovesnik-bot.online/doroshka/my/reservations/"

@router.post("/reservation/create/", tags=["Reservation"])
async def create(request: ReservationForCreating):
    try:
        result = await ReservationMiddleware.create(**request.model_dump())
        if (result == DBTransactionStatus.SUCCESS):

            table_entity = await TableMiddleware.get_by_uuid(table_uuid=request.table_uuid)
            bar_entity = await BarMiddleware.get_by_id(bar_id=table_entity.bar_id)

            dt_obj_start = datetime.strptime(request.reservation_start, "%Y-%m-%d %H:%M:%S.%f")
            dt_obj_end = (dt_obj_start + timedelta(hours=2))
            start = dt_obj_start.strftime("%H:%M:%S")
            end = dt_obj_end.strftime("%H:%M:%S")

            bar_id = bar_entity.bar_id

            if (bar_entity.bar_id == 1):
                url = f"{ROVESNIK_MY_RESERVATIONS}?barId={bar_id}"
            elif (bar_entity.bar_id == 2):
                url = f"{SKREPKA_MY_RESERVATIONS}?barId={bar_id}"
            elif (bar_entity.bar_id == 3):
                url = f"{DOROSHKA_MY_RESERVATIONS}?barId={bar_id}"

            await bot.send_message(
                chat_id=request.client_chat_id,
                text=f"✅ Вы успешно забронировали столик {table_entity.table_id}" + (f" на {table_entity.storey} этаже " if table_entity.bar_id == 1 else " ") + f"в баре {bar_entity.bar_name} c {start} до {end}",
                reply_markup=types.InlineKeyboardMarkup(
                    row_width=1,
                    keyboard=[
                        [ 
                            types.InlineKeyboardButton(
                                text="Моя бронь в веб-апп",
                                web_app=types.WebAppInfo(url)
                            )
                        ]
                    ]
                )
            )

            id = await ReservationMiddleware.get_entity_id(**request.model_dump())
            return {
                "Status": "Success",
                "Message": f"Reservation with reservation_id {id} has been succesfully created in the data base"
            }
        elif (result == ReservationResponse.ERROR):
            return {
                "Status": "Failed",
                "Message": f"An error occured while interacting with the IIKO client"
            }
        elif (result == ReservationResponse.NOT_AVAILABLE):
            return {
                "Status": "Failed",
                "Message": f"The table with id {request.table_uuid}, which you are trying to book, is inaccessible currently"
            }
        elif (result == ReservationResponse.NO_PERMISSION):
            return {
                "Status": "Failed",
                "Message": f"The client with chat_id {request.client_chat_id} has exhausted his ability to book today"
            }
        elif (result == DBTransactionStatus.ALREADY_EXIST):
            return {
                "Status": "Failed",
                "Message": f"A reservation with the parameters which you are passing has already been created"
            }
        else:
            return {
                "Status": "Failed",
                "Message": f"An error occured while communicating with the data base"
            }
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR,
            message=f"An error occurred in /reservation/create/: {e}",
            module_name="API"
        )

@router.post("/reservation/update/", tags=["Reservation"])
async def update(request: ReservationForUpdating):
    try:
        result = await ReservationMiddleware.update(**request.model_dump())
        if (result == DBTransactionStatus.SUCCESS):
            reservation_entity = await ReservationMiddleware.get_by_reserve_id(reserve_id=request.reserve_id)
            table_entity = await TableMiddleware.get_by_uuid(
                table_uuid=(request.table_uuid if request.table_uuid else reservation_entity.table_uuid)
            )
            bar_id = table_entity.bar_id
            
            if (bar_id == 1):
                url = f"{ROVESNIK_MY_RESERVATIONS}?barId={bar_id}"
            elif (bar_id == 2):
                url = f"{SKREPKA_MY_RESERVATIONS}?barId={bar_id}"
            elif (bar_id == 3):
                url = f"{DOROSHKA_MY_RESERVATIONS}?barId={bar_id}"

            msg_text = "✅ Вы успешно изменили в свою бронь"
            await bot.send_message(
                chat_id=(request.client_chat_id if request.client_chat_id else reservation_entity.client_chat_id),
                text=msg_text,
                reply_markup=types.InlineKeyboardMarkup(
                    row_width=1,
                    keyboard=[
                        [ 
                            types.InlineKeyboardButton(
                                text="Моя бронь в веб-апп",
                                web_app=types.WebAppInfo(url)
                            )
                        ]
                    ]
                )
            )
            return {
                "Status": "Success",
                "Message": f"Reservation entity has been succesfully updated in the data base"
            }
        elif (result == ReservationResponse.ERROR):
            return {
                "Status": "Failed",
                "Message": f"An error occured while interacting with the IIKO client"
            }
        elif (result == ReservationResponse.NOT_AVAILABLE):
            return {
                "Status": "Failed",
                "Message": f"The table with uuid {request.table_uuid if request.table_uuid else reservation_entity.table_uuid}, which you are trying to book, is inaccessible currently"
            }
        elif (result == ReservationResponse.NO_PERMISSION):
            return {
                "Status": "Failed",
                "Message": f"The client who owns the reservation with {request.reserve_id} cannot rebook today anymore"
            }
        elif (result == DBTransactionStatus.ALREADY_EXIST):
            return {
                "Status": "Failed",
                "Message": f"Unexpected system behaviour: a reservation with the given params for updating has already been created in the data base"
            }
        else:
            return {
                "Status": "Failed",
                "Message": f"An error occured while communicating with the data base"
            }
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR,
            message=f"An error occurred in /reservation/update/: {e}",
            module_name="API"
        )

@router.post("/reservation/cancel/", tags=["Reservation"])
async def cancel(request: ReservationForCancelling):
    try:
        result = await ReservationMiddleware.cancel(**request.model_dump())
        if (result == DBTransactionStatus.SUCCESS):
            reservation = await ReservationMiddleware.get_by_reserve_id(reserve_id=request.reserve_id)
            table_entity = await TableMiddleware.get_by_uuid(table_uuid=reservation.table_uuid)
            bar_id = table_entity.bar_id
            if (bar_id == 1):
                url = f"{ROVESNIK_MY_RESERVATIONS}?barId={bar_id}"
            elif (bar_id == 2):
                url = f"{SKREPKA_MY_RESERVATIONS}?barId={bar_id}"
            elif (bar_id == 3):
                url = f"{DOROSHKA_MY_RESERVATIONS}?barId={bar_id}"

            msg_text = "✅ Вы успешно отменили свою бронь"
            await bot.send_message(
                chat_id=reservation.client_chat_id,
                text=msg_text,
                reply_markup=types.InlineKeyboardMarkup(
                    row_width=1,
                    keyboard=[
                        [ 
                            types.InlineKeyboardButton(
                                text="Моя бронь в веб-апп",
                                web_app=types.WebAppInfo(url)
                            )
                        ]
                    ]
                )
            )
            return {
                "Status": "Success",
                "Message": f"Reservation with reserve_id {request.reserve_id} has been succesfully cancelled"
            }
        elif (result == ReservationResponse.ERROR):
            return {
                "Status": "Failed",
                "Message": f"An error occured while interacting with the IIKO client"
            }
        else:
            return {
                "Status": "Failed",
                "Message": f"An error occured while communicating with the data base"
            }
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR,
            message=f"An error occurred in /reservation/cancel/: {e}",
            module_name="API"
        )

@router.delete("/reservation/delete/{reservation_id}", tags=["Reservation"])
async def delete(reservation_id: int):
    try:
        result = await ReservationMiddleware.delete(reservation_id=reservation_id)
        if (result == DBTransactionStatus.SUCCESS):
            return {
                "Status": "Success",
                "Message": f"Reservation with reservation_id {reservation_id} has been succesfully deleted from the data base"
            }
        elif (result == ReservationResponse.ERROR):
            return {
                "Status": "Failed",
                "Message": f"An error occured while interacting with the IIKO client"
            }
        else:
            return {
                "Status": "Failed",
                "Message": f"An error occured while communicating with the data base"
            }
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR,
            message=f"An error occurred in /reservation/delete/: {e}",
            module_name="API"
        )

@router.get("/reservation/get_all/", tags=["Reservation"])
async def get_all():
    try:
        result = await ReservationMiddleware.get_all()
        if (result):
            return {
                "Status": "Success",
                "Message": [parse_reservation_into_format(reservation) for reservation in result]
            }
        else:
            return {
                "Status": "Failed",
                "Message": "There are no reservations available"
            }
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR,
            message=f"An error occurred in /reservation/get_all/: {e}",
            module_name="API"
        )

@router.post("/reservation/get_all_by_chat_id/{chat_id}", tags=["Reservation"])
async def get_all_by_chat_id(chat_id: int):
    try:
        result = await ReservationMiddleware.get_all_by_chat_id(chat_id=chat_id)
        if (result):
            return {
                "Status": "Success",
                "Message": [parse_reservation_into_format(reservation) for reservation in result]
            }
        else:
            return {
                "Status": "Failed",
                "Message": f"There are no reservations available for the client with chat_id {chat_id}"
            }
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR,
            message=f"An error occurred in /reservation/get_all_by_chat_id/: {e}",
            module_name="API"
        )

@router.get("/reservation/get_by_id/{reservation_id}", tags=["Reservation"])
async def get_by_id(reservation_id: int):
    try:
        result = await ReservationMiddleware.get_by_id(reservation_id=reservation_id)
        if (result):
            return {
                "Status": "Success",
                "Message": parse_reservation_into_format(result)
            }
        else:
            return {
                "Status": "Failed",
                "Message": f"There is not a reservation with reservation_id {reservation_id}"
            }
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR,
            message=f"An error occurred in /reservation/get_by_id/: {e}",
            module_name="API"
        )

@router.get("/reservation/get_by_reserve_id/{reserve_id}", tags=["Reservation"])
async def get_by_reserve_id(reserve_id: str):
    try:
        result = await ReservationMiddleware.get_by_reserve_id(reserve_id=reserve_id)
        if (result):
            return {
                "Status": "Success",
                "Message": parse_reservation_into_format(result)
            }
        else:
            return {
                "Status": "Failed",
                "Message": f"There is not a reservation with reserve_id {reserve_id}"
            }
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR,
            message=f"An error occurred in /reservation/get_by_reserved_id/: {e}",
            module_name="API"
        )

@router.get("/reservation/get_by_order_uuid/{order_uuid}", tags=["Reservation"])
async def get_by_order_uuid(order_uuid: str):
    try:
        reservations = await ReservationMiddleware.get_by_order_uuid(order_uuid=order_uuid)
        if (reservations):
            return {
                "Status": "Success",
                "Message": [parse_reservation_into_format(reservation) for reservation in reservations]
            }
        else:
            return {
                "Status": "Failed",
                "Message": f"There are not any reservations with order_uuid {order_uuid}"
            }
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR,
            message=f"An error occurred in /reservation/get_by_order_uuid/: {e}",
            module_name="API"
        )

@router.get("/reservation/get_reservation_and_table_by_order_uuid/{order_uuid}", tags=["Reservation"])
async def get_reservation_and_table_by_order_uuid(order_uuid: str):
    try:
        reservations = await ReservationMiddleware.get_by_order_uuid(order_uuid=order_uuid)
        if (reservations):
            result = []
            for reservation in reservations:
                table = await TableMiddleware.get_by_uuid(table_uuid=reservation.table_uuid)
                result.append(
                    parse_reservation_and_table_into_format(
                        reservation=reservation,
                        table=table
                    )
                )
            return {
                "Status": "Success",
                "Message": result
            }
        else:
            return {
                "Status": "Failed",
                "Message": f"There are not any reservations with order_uuid {order_uuid}"
            }
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR,
            message=f"An error occurred in /reservation/get_by_order_uuid/: {e}",
            module_name="API"
        )

@router.post("/reservation/get_all_reserved_statuses_by_chat_id/", tags=["Reservation"])
async def get_all_reserved_statuses_by_chat_id(request: GetClientReservationsRequest):
    try:
        reservations = await ReservationMiddleware.get_all_reserved_statuses_by_chat_id(**request.model_dump())
        if (reservations):
            return {
                "Status": "Success",
                "Message": [parse_reservation_into_format(reservation) for reservation in reservations]
            }
        else:
            return {
                "Status": "Failed",
                "Message": f"There are not any reservations for the client with chat_id {request.chat_id}"
            }
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR,
            message=f"An error occurred in /reservation/get_all_reserved_statuses_by_chat_id/: {e}",
            module_name="API"
        )

@router.post("/reservation/get_expired_and_cancelled_by_chat_id/", tags=["Reservation"])
async def get_all_expired_and_cancelled_by_chat_id(request: GetClientReservationsRequest):
    try:
        reservations = await ReservationMiddleware.get_all_expired_and_cancelled_by_chat_id(**request.model_dump())
        if (reservations):
            return {
                "Status": "Success",
                "Message": [parse_reservation_into_format(reservation) for reservation in reservations]
            }
        else:
            return {
                "Status": "Failed",
                "Message": f"There are not any reservations for the client with chat_id {request.chat_id} with cancelled or expired statuses"
            }
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR,
            message=f"An error occurred in /reservation/get_expired_and_cancelled_by_chat_id/: {e}",
            module_name="API"
        )

@router.post("/reservation/check_change_ability/", tags=["Reservation"])
async def check_change_ability(reserve_id: str):
    try:
        reservation = await ReservationMiddleware.get_by_reserve_id(reserve_id=reserve_id)
        if (reservation):
            now = datetime.now() + timedelta(hours=3)
            verge = reservation.reservation_start - timedelta(hours=2)
            change_ability = True if now < verge else False
            return {
                "Status": "Success",
                "Message": change_ability
            }
        else:
            return {
                "Status": "Failed",
                "Message": f"There is not a reservation with reserve_id {reserve_id}"
            }
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR,
            message=f"An error occurred in /reservation/check_change_ability/: {e}",
            module_name="API"
        )
