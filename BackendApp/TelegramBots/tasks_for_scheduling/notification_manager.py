from BackendApp.TelegramBots.HeadBot.Config import bot

from BackendApp.Database.session import DBTransactionStatus
from BackendApp.Database.Models.event_model import Event
from BackendApp.Database.Models.promocode_model import Promocode
from BackendApp.Database.Models.ticket_model import Ticket
from BackendApp.Database.Models.reservation_model import Reservation

from BackendApp.Middleware.client_middleware import ClientMiddleware
from BackendApp.Middleware.promocodes_middleware import PromocodesMiddleware
from BackendApp.Middleware.bar_middleware import BarMiddleware
from BackendApp.Middleware.event_middleware import EventMiddleware
from BackendApp.Middleware.ticket_middleware import TicketMiddleware
from BackendApp.Middleware.reservation_middleware import ReservationMiddleware
from BackendApp.scheduler.core import Scheduler 

from datetime import datetime, timedelta
from telebot import types
from dotenv import load_dotenv
import asyncio
import json
import os

load_dotenv()

ROVESNIK_NAME = os.getenv("ROVESNIK_BOT_NAME")
SKREPKA_NAME = os.getenv("SKREPKA_BOT_NAME")
DOROSHKA_NAME = os.getenv("DOROSHKA_BOT_NAME")
CONTEXT_MANAGER = os.getcwd() + "/BackendApp/API/client/context_manager.json"

class NotificationManager:
    
    def __init__(
            self, 
            checking_delay: int, 
            scheduler: Scheduler
        ):
        self.checking_delay = checking_delay
        self.scheduler = scheduler
    
    @staticmethod
    async def send_review_promocodes(promocode: Promocode):
        await bot.send_message(
            chat_id=promocode.client_chat_id,
            text="🤠 Ты вчера использовал промокод в одном из наших баров. Оставь отзыв о нём, нам очень ценно твое мнение!",
            reply_markup=types.InlineKeyboardMarkup(
                row_width=1,
                keyboard=[
                    [
                        types.InlineKeyboardButton(
                            text="👉 Перейди по этой кнопке, чтобы оставить отзыв о баре",
                            callback_data="leave_feedback"
                        )
                    ]
                ]
            )
        )

    @staticmethod
    async def manage_promocodes():
        clients = await ClientMiddleware.get_all_clients()
        if (clients != DBTransactionStatus.NOT_EXIST):
            for client in clients:
                promocodes = await PromocodesMiddleware.get_user_promocodes(client_chat_id=client.chat_id)
                for promocode in promocodes:
                    now = datetime.now() + timedelta(hours=3)
                    if (now - promocode.activation_time > timedelta(days=1) and 
                        now - promocode.activation_time < timedelta(days=2)):
                        await NotificationManager.send_review_promocodes(promocode=promocode)
                        break # one notification if a client used a promocode a day ago will be enough

    @staticmethod
    async def send_review_ticket(ticket: Ticket):
        event = await EventMiddleware.get_event_by_id(event_id=ticket.event_id)

        if (event.bar_id == 1):
            url = f"http://t.me/{ROVESNIK_NAME}"
        elif (event.bar_id == 2):
            url = f"http://t.me/{SKREPKA_NAME}"
        else:
            url = f"http://t.me/{DOROSHKA_NAME}"

        await bot.send_message(
            chat_id=ticket.client_chat_id,
            text=f"🥳 Ты вчера был в одном из наших баров и посетил мероприятие \"{event.short_name}\". Оставь отзыв о нем, нам очень ценно твое мнение!",
            reply_markup=types.InlineKeyboardMarkup(
                row_width=1,
                keyboard=[
                    [
                        types.InlineKeyboardButton(
                            text="👉 Перейди по этой кнопке в бота, где было мероприятие, чтобы оставить отзыв",
                            url=url
                        )
                    ]
                ]
            )
        )

    @staticmethod
    async def manage_tickets():
        clients = await ClientMiddleware.get_all_clients()
        if (clients != DBTransactionStatus.NOT_EXIST):
            for client in clients:
                tickets = await TicketMiddleware.get_by_chat_id(chat_id=client.chat_id)
                for ticket in tickets:
                    now = datetime.now() + timedelta(hours=3)
                    if (ticket.activation_status):
                        if (now - ticket.activation_time > timedelta(days=1) and 
                            now - ticket.activation_time < timedelta(days=2)):
                            await NotificationManager.send_review_ticket(ticket=ticket)
                            break # one notification if a client bought a ticket a day ago will be enough

    @staticmethod
    async def send_review_reservation(reservation: Reservation):
        await bot.send_message(
            chat_id=reservation.client_chat_id,
            text="🤠 Ты вчера бронировал столик в одном из наших баров. Оставь отзыв о нём, нам очень ценно твое мнение!",
            reply_markup=types.InlineKeyboardMarkup(
                row_width=1,
                keyboard=[
                    [
                        types.InlineKeyboardButton(
                            text="👉 Перейди по этой кнопке, чтобы оставить отзыв о баре",
                            callback_data="leave_feedback"
                        )
                    ]
                ]
            )
        )

    @staticmethod
    async def manage_reservations():
        clients = await ClientMiddleware.get_all_clients()
        if (clients != DBTransactionStatus.NOT_EXIST):
            for client in clients:
                reservations = await ReservationMiddleware.get_all_by_chat_id(chat_id=client.chat_id)
                for reservation in reservations:
                    now = datetime.now() + timedelta(hours=3) - timedelta(hours=2) 
                    if (now - reservation.reservation_start > timedelta(days=1) and 
                        now - reservation.reservation_start < timedelta(days=2)):
                        await NotificationManager.send_review_reservation(reservation=reservation)
                        break # one notification if a client made a reservation a day ago will be enough
    
    @staticmethod
    async def send_event_reminder(chat_id: int, event: Event):
        bar_entity = await BarMiddleware.get_by_id(bar_id=event.bar_id)
        await bot.send_message(
            chat_id=chat_id,
            text=f"☝️ Ты был зарегистрирован на мероприятие \"{event.short_name}\". Мероприятие пройдет в баре {bar_entity.bar_name}, {event.datetime}. {event.motto}"
        )
    
    @staticmethod
    async def manage_events():
        clients = await ClientMiddleware.get_all_clients()
        if (clients != DBTransactionStatus.NOT_EXIST):
            for client in clients:
                tickets = await TicketMiddleware.get_by_chat_id(chat_id=client.chat_id)
                for ticket in tickets:
                    if (not ticket.activation_status): 
                        now = datetime.now() + timedelta(hours=3)
                        event = await EventMiddleware.get_event_by_id(event_id=ticket.event_id)
                        for notification_time in event.notification_time:
                            if (
                                (now - event.datetime > timedelta(minutes=int(notification_time))) and 
                                (now - event.datetime < timedelta(minutes=int(notification_time)) + timedelta(minutes=1)) and
                                (now < event.datetime)
                            ):
                                await NotificationManager.send_event_reminder(
                                    chat_id=client.chat_id,
                                    event=event
                                )
    @staticmethod
    async def manage_shipping_query():
        try:
            with open(CONTEXT_MANAGER, "r", encoding="utf-8") as infile:
                data = json.load(infile)
        except json.JSONDecodeError:
            data = []
            
        for chunk in data:
            date_time = chunk['datetime']
            date_time = datetime.strptime(date_time, "%Y-%m-%d %H:%M:%S")
            now = datetime.now() + timedelta(hours=3)
            if (now - date_time > timedelta(hours=12)):
                del data[data.index(chunk)]
                await bot.delete_message(chunk['chat_id'], chunk['msg_id'])

        with open(CONTEXT_MANAGER, "w", encoding="utf-8") as outfile:
            json.dump(data, outfile, indent=4, ensure_ascii=False)

async def notification_manager_thread():
    notification_manager = NotificationManager(
        checking_delay=1,
        scheduler=Scheduler(5)
    )

   # notification_manager.scheduler.create_job(
   #     NotificationManager.manage_promocodes,
   #     "at",
   #     None,
   #     time_str="09:00" # GMT +0
   # )
    notification_manager.scheduler.create_job(
        NotificationManager.manage_tickets,
        "at",
        None,
        time_str="09:00" # GMT +0 
    )
    notification_manager.scheduler.create_job(
        NotificationManager.manage_reservations,
        "at",
        None,
        time_str="09:00" # GMT +0
    )
    notification_manager.scheduler.create_job(
        NotificationManager.manage_events,
        "every",
        "minutes",
        delay=1
    )
    notification_manager.scheduler.create_job(
        NotificationManager.manage_shipping_query,
        "every",
        "minutes",
        delay=1
    )
    print(f"Delay - every day at 12:00 GMT +3")
    while True:
        now = datetime.now()
        timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
        print(f"{timestamp} - NotificationManager envoked") 
        await notification_manager.scheduler.pending()

if __name__ == "__main__":
    asyncio.run(notification_manager_thread())
