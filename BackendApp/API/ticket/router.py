import os
from BackendApp.API.client.schemas import ClientForReturn
from BackendApp.API.client.utils import parse_client_into_format
from BackendApp.Database.session import DBTransactionStatus
from BackendApp.Database.Models.client_model import Client
from BackendApp.Middleware.ticket_middleware import TicketMiddleware
from BackendApp.Middleware.event_middleware import EventMiddleware
from BackendApp.Middleware.client_middleware import ClientMiddleware
from BackendApp.IIKO.api import Client as ClientIIKO
from BackendApp.API.ticket.schemas import *
from BackendApp.API.ticket.utils import *
from BackendApp.TelegramBots.HeadBot.Config.bot import bot
from BackendApp.Logger import logger, LogLevel

from telebot import types
from datetime import datetime, timedelta
from typing import Union, List
from fastapi import APIRouter
from dotenv import load_dotenv
import ast

load_dotenv()

AFISHA_ROVESNIK = "https://rovesnik-bot.online/rovesnik/my/events/"
AFISHA_SKREPKA = "https://rovesnik-bot.online/skrepka/my/events/"
AFISHA_DOROSHKA = "https://rovesnik-bot.online/doroshka/my/events/"
API_LOGIN = os.getenv("API_LOGIN")

router = APIRouter()

@router.post("/ticket/purchase/", tags=["Tickets"])
async def purchase_ticket(payload: PurchaseTicketRequest) -> dict:
    try:
        status = await TicketMiddleware.purchase_ticket(**payload.model_dump())
        if (status):
            id = await TicketMiddleware.get_entity_id(**payload.model_dump())
            event = await EventMiddleware.get_event_by_id(event_id=payload.event_id)
            date = event.datetime.strftime("%Y-%m-%d")
            time = event.datetime.strftime("%H:%M")
            
            bar_id = event.bar_id

            if (bar_id == 1):
                url = f"{AFISHA_ROVESNIK}?barId={bar_id}"
            elif (bar_id == 2):
                url = f"{AFISHA_SKREPKA}?barId={bar_id}"
            elif (bar_id == 3):
                url = f"{AFISHA_DOROSHKA}?barId={bar_id}"

            await bot.send_message(
                chat_id=payload.client_chat_id,
                text=f"✅ Вам успешно был назначен билет на бесплатное мероприятие \"{event.short_name}\". Оно начнется в {time}, {date}.",
                reply_markup=types.InlineKeyboardMarkup(
                    row_width=1,
                    keyboard=[
                        [ 
                            types.InlineKeyboardButton(
                                text="Мероприятие в веб-апп",
                                web_app=types.WebAppInfo(url)
                            )
                        ]
                    ]
                )
            )
            return {
                "status": "Success",
                "message": f"Ticket with id {id} for chat_id {payload.client_chat_id} for event with id {payload.event_id} has been succesfully created."
            }
        else:
            return {
                "status": "Failed",
                "message": f"This ticket has already been puchased for the user with chat id {payload.client_chat_id}"
            }
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR,
            message=f"An error occurred in /ticket/purchase/: {e}",
            module_name="API"
        )

@router.post("/ticket/purchase_free/", tags=["Tickets"])
async def purchase_free_ticket(purchase_ticket_info: PurchaseFreeTicketRequest) -> dict:
    try:
        status = await TicketMiddleware.purchase_ticket(**purchase_ticket_info.model_dump())
        if (status):
            event = await EventMiddleware.get_event_by_id(event_id=purchase_ticket_info.event_id)
            date = event.datetime.strftime("%Y-%m-%d")
            time = event.datetime.strftime("%H:%M")

            bar_id = event.bar_id

            if (bar_id == 1):
                url = f"{AFISHA_ROVESNIK}?barId={bar_id}"
            elif (bar_id == 2):
                url = f"{AFISHA_SKREPKA}?barId={bar_id}"
            elif (bar_id == 3):
                url = f"{AFISHA_DOROSHKA}?barId={bar_id}"
            
            await bot.send_message(
                chat_id=purchase_ticket_info.client_chat_id,
                text=f"✅ Вам успешно был назначен билет на бесплатное мероприятие \"{event.short_name}\". Оно начнется в {time}, {date}.",
                reply_markup=types.InlineKeyboardMarkup(
                    row_width=1,
                    keyboard=[
                        [ 
                            types.InlineKeyboardButton(
                                text="Мероприятие в веб-апп",
                                web_app=types.WebAppInfo(url)
                            )
                        ]
                    ]
                )
            )
            dump = purchase_ticket_info.model_dump()
            friends = dump["friends"]
            if (friends):
                for friend in friends:
                    client = await ClientMiddleware.get_client_by_username(username=friend["username"])
                    if (isinstance(client, Client)):
                        await bot.send_message(
                            chat_id=client.chat_id,
                            text=f"✅ Вам успешно был назначен билет на бесплатное мероприятие \"{event.short_name}\". Оно начнется в {time}, {date}.",
                            reply_markup=types.InlineKeyboardMarkup(
                                row_width=1,
                                keyboard=[
                                    [ 
                                        types.InlineKeyboardButton(
                                            text="Мероприятие в веб-апп",
                                            web_app=types.WebAppInfo(url)
                                        )
                                    ]
                                ]
                            )
                        )
                        await TicketMiddleware.purchase_ticket(
                            event_id=purchase_ticket_info.event_id,
                            client_chat_id=client.chat_id
                        )
                    
            return get_ticket_purchasing_info(status)
        else:
            return get_ticket_purchasing_info(status)
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR,
            message=f"An error occurred in /ticket/purchase_free/: {e}",
            module_name="API"
        )

@router.post("/ticket/purchase_by_bonus_points", tags=["Tickets"])
async def purchase_by_bonus_points(info: PurchaseTicketByBonusPoints) -> dict:
    try:
        status = await ClientMiddleware.purchase_by_bonus_points(
            chat_id=info.client_chat_id,
            bar_id=info.bar_id,
            amount=info.amount,
            event_id=info.event_id
        )
        if (status != "Билет не куплен, произошла ошибка"):
            event = await EventMiddleware.get_event_by_id(event_id=info.event_id)
            date = event.datetime.strftime("%Y-%m-%d")
            time = event.datetime.strftime("%H:%M")

            bar_id = event.bar_id

            if (bar_id == 1):
                url = f"{AFISHA_ROVESNIK}?barId={bar_id}"
            elif (bar_id == 2):
                url = f"{AFISHA_SKREPKA}?barId={bar_id}"
            elif (bar_id == 3):
                url = f"{AFISHA_DOROSHKA}?barId={bar_id}"

            await bot.send_message(
                chat_id=info.client_chat_id,
                text=f"✅ Вы успешно приобрели билет на мероприятие \"{event.short_name}\". Оно начнется в {time}, {date}.",
                reply_markup=types.InlineKeyboardMarkup(
                    row_width=1,
                    keyboard=[
                        [ 
                            types.InlineKeyboardButton(
                                text="Мероприятие в веб-апп",
                                web_app=types.WebAppInfo(url)
                            )
                        ]
                    ]
                )
            )
            return {
                "status": "Success",
                "message": status
            }
        return {
            "status": "Failed",
            "message": status
        }
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR,
            message=f"An error occurred in /ticket/purchase_by_bonus_points/: {e}",
            module_name="API"
        )


@router.get("/tickets/{client_chat_id}/", tags=["Tickets"])
async def get_all_tickets(client_chat_id: int) -> List[TicketInfo]:
    try:
        user_tickets = await TicketMiddleware.get_all_tickets(client_chat_id)
        return parse_tickets_into_format(user_tickets)
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR,
            message=f"An error occurred in /tickets/: {e}",
            module_name="API"
        )

@router.get("/ticket/{ticket_id}/", tags=["Tickets"])
async def get_ticket_by_id(ticket_id: int) -> Union[TicketInfo, dict]:
    try:
        ticket = await TicketMiddleware.get_ticket_by_id(ticket_id)
        if ticket:
            return {
                "status": "Success",
                "message": parse_ticket_into_format(ticket)
            }
        else:
            return {
                "status": "Failed",
                "message" : f"Ticket with ticket_id {ticket_id} has not been found"
            }
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR,
            message=f"An error occurred in /ticket/: {e}",
            module_name="API"
        )

@router.get("/ticket/hash/{hashcode}/", tags=["Tickets"])
async def get_ticket_by_hashcode(hashcode: str) -> Union[TicketInfo, dict]:
    try:
        ticket = await TicketMiddleware.get_ticket_by_hashcode(hashcode)
        if ticket:
            return {
                "status": "Success",
                "message": parse_ticket_into_format(ticket)
            }
        else:
            return {
                "status": "Failed",
                "message" : f"Ticket with hashcode {hashcode} has not been found"
            }
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR,
            message=f"An error occurred in /ticket/hash/: {e}",
            module_name="API"
        )

@router.patch("/ticket/activate/", tags=["Tickets"], description=get_activate_ticket_description())
async def activate_ticket_by_hashcode(hashcode: str) -> dict:
    try:
        activation_status = await TicketMiddleware.validate_ticket(hashcode)
        if activation_status:

            ticket = await TicketMiddleware.get_ticket_by_hashcode(hashcode=hashcode)
            event = await EventMiddleware.get_event_by_id(event_id=ticket.event_id)
            
            await TicketMiddleware.update_ticket(
                ticket_id=ticket.id,
                activation_time=(datetime.now() + timedelta(hours=3))
            )
            await bot.send_message(
                chat_id=ticket.client_chat_id,
                text=f"✅ Ваш билет на мероприятие \"{event.short_name}\" был успешно активирован"
            )

            return {
                "Status": "Success",
                "message": "Ticket activated successfully"
            }
        else:
            return {
                "Status": "Failed",
                "message": "Ticket actiavtion failed"
            }
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR,
            message=f"An error occurred in /ticket/activate/: {e}",
            module_name="API"
        )
    
@router.delete("/ticket/delete/{ticket_id}/", tags=["Tickets"])
async def delete_ticket(ticket_id: int) -> dict:
    try:
        ticket = await TicketMiddleware.get_ticket_by_id(ticket_id=ticket_id)
        if (ticket):
            event = await EventMiddleware.get_event_by_id(event_id=ticket.event_id)
            msg_text = f"✅ Ваш тикет был успешно удален на мероприятие \"{event.short_name}\"."
            friends = ticket.friends
            if (friends is not None):
                friends = ast.literal_eval(friends)
                for friend in friends:
                    client = await ClientMiddleware.get_client_by_username(username=friend["username"])
                    friend_ticket = await TicketMiddleware.get_by_chat_id_and_event_id(
                        chat_id=client.chat_id,
                        event_id=event.id
                    )
                    if (friend_ticket != DBTransactionStatus.NOT_EXIST):
                        status = await TicketMiddleware.delete_ticket(friend_ticket.id)
                        if (status):
                            if (isinstance(client, Client)):
                                await bot.send_message(
                                    chat_id=client.chat_id,
                                    text=msg_text
                                )

            if (event.event_type == "free"):
                free_event_tickets = await TicketMiddleware.get_by_event_id(event_id=event.id)
                ticket_owner = await ClientMiddleware.get_client(
                    chat_id=ticket.client_chat_id
                )
                owner_username = ticket_owner.username

                for free_ticket in free_event_tickets:
                    free_ticket_friends = free_ticket.friends
                    if (free_ticket_friends is not None):
                        free_ticket_friends = ast.literal_eval(free_ticket_friends)
                        for friend in free_ticket_friends:
                            if (friend["username"] == owner_username):
                                free_ticket_friends.remove(friend)
                        
                        await TicketMiddleware.update_ticket(
                            ticket_id=free_ticket.id,
                            friends=free_ticket_friends
                        )

            delete_status = await TicketMiddleware.delete_ticket(ticket_id)
            await bot.send_message(
                chat_id=ticket.client_chat_id,
                text=msg_text
            )
            return {
                "status" : "Success"
            } 
        else:
            return {
                "status" : "Something went wrong"
            }
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR,
            message=f"An error occurred in /ticket/delete/: {e}",
            module_name="API"
        )

@router.patch("/ticket/update", tags=["Tickets"])
async def update_ticket(ticket: TicketUpdateRequest) -> dict:
    try:
        old_ticket = await TicketMiddleware.get_ticket_by_id(ticket_id=ticket.id)
        old_friends = old_ticket.friends

        status = await TicketMiddleware.update_ticket(
            ticket_id=ticket.id,
            qr_path=ticket.qr_path,
            activation_status=ticket.activation_status,
            event_id=ticket.event_id,
            client_chat_id=ticket.client_chat_id,
            hashcode=ticket.hashcode,
            friends=[friend.model_dump() for friend in ticket.friends] if ticket.friends else None,
            activation_time=ticket.activation_time
        )

        if (status == DBTransactionStatus.SUCCESS):
            client_ticket = await TicketMiddleware.get_ticket_by_id(ticket_id=ticket.id)
            event = await EventMiddleware.get_event_by_id(event_id=client_ticket.event_id)

            bar_id = event.bar_id

            if (bar_id == 1):
                url = f"{AFISHA_ROVESNIK}?barId={bar_id}"
            elif (bar_id == 2):
                url = f"{AFISHA_SKREPKA}?barId={bar_id}"
            elif (bar_id == 3):
                url = f"{AFISHA_DOROSHKA}?barId={bar_id}"

            await bot.send_message(
                chat_id=client_ticket.client_chat_id,
                text=f"✅ Ваш билет на мероприятие \"{event.short_name}\" был обновлен.",
                reply_markup=types.InlineKeyboardMarkup(
                    row_width=1,
                    keyboard=[
                        [ 
                            types.InlineKeyboardButton(
                                text="Мероприятие в веб-апп",
                                web_app=types.WebAppInfo(url)
                            )
                        ]
                    ]
                )
            )

            dump = ticket.model_dump()
            friends = dump["friends"]

            if (friends):
                for friend in friends:
                    client = await ClientMiddleware.get_client_by_username(username=friend["username"])
                    if (isinstance(client, Client)):
                        await bot.send_message(
                            chat_id=client.chat_id,
                            text=f"✅ Ваш билет на мероприятие \"{event.short_name}\" был обновлен.",
                            reply_markup=types.InlineKeyboardMarkup(
                                row_width=1,
                                keyboard=[
                                    [ 
                                        types.InlineKeyboardButton(
                                            text="Мероприятие в веб-апп",
                                            web_app=types.WebAppInfo(url)
                                        )
                                    ]
                                ]
                            )
                        )
                        await TicketMiddleware.purchase_ticket(
                            event_id=ticket.event_id,
                            client_chat_id=client.chat_id
                        )
            if (old_friends is not None):
                old_friends = ast.literal_eval(old_friends)
                for old_friend in old_friends:
                    if (old_friend not in friends):
                        old_friend_entity = await ClientMiddleware.get_client_by_username(
                            username=old_friend["username"]
                        )
                        old_friend_ticket = await TicketMiddleware.get_by_chat_id_and_event_id(
                            chat_id=old_friend_entity.chat_id,
                            event_id=ticket.event_id
                        )
                        if (old_friend_ticket != DBTransactionStatus.NOT_EXIST):
                            status = await TicketMiddleware.delete_ticket(old_friend_ticket.id)
                            if (status):
                                if (isinstance(old_friend_entity, Client)):
                                    msg_text = f"✅ Ваш тикет был успешно удален на мероприятие \"{event.short_name}\"."
                                    await bot.send_message(
                                        chat_id=client.chat_id,
                                        text=msg_text
                                    )



            return {"status" : "Success"}
        else:
            return {"status" : "Something went wrong"}
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR,
            message=f"An error occurred in /ticket/update/: {e}",
            module_name="API"
        )
    
@router.get("/ticket/get_clients_with_ticket_for_event/{event_id}/", tags=["Tickets"])
async def get_clients_with_ticket_for_event(
    event_id: int
    ) -> Union[List[ClientForReturn], dict]:
    try:
        parsed_clients = []
        clients = await TicketMiddleware.get_registered_clients_for_event(event_id)
        if clients == DBTransactionStatus.NOT_EXIST:
            return {"status ": "Failed", "message": "There are no clients with tickets for this event"}
        if clients == DBTransactionStatus.ROLLBACK:
            return {"status ": "Failed", "message": "Something went wrong"}
        for client in clients:
            client_iiko = await ClientIIKO.create(API_LOGIN, "Rovesnik")
            iiko_user = await client_iiko.get_customer_info(id=client.iiko_id)
            balance = iiko_user.walletBalances[0]["balance"]
            loyalty_info = await client_iiko.get_customer_loyalty_info(client.iiko_id)
            parsed_clients.append(parse_client_into_format(client, balance, loyalty_info))
        return {"status ": "Success", "message": parsed_clients}
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR,
            message=f"An error occurred in /ticket/get_clients_with_ticket_for_event/: {e}",
            module_name="API"
        )

@router.get(path="/ticket/get_by_event_id/{event_id}", tags=["Tickets"])
async def get_by_event_id(event_id: int):
    try:
        tickets = await TicketMiddleware.get_by_event_id(event_id=event_id)
        if (tickets):
            return {
                "status": "Success",
                "message": parse_tickets_into_format(tickets=tickets)
            }
        else:
            return {
                "status": "Failed",
                "message": f"There are no tickets for the event with event_id {event_id}"
            }
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR,
            message=f"An error occurred in /ticket/get_by_event_id/: {e}",
            module_name="API"
        )