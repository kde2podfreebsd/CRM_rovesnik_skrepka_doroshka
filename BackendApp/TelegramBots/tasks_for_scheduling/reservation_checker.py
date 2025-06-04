from BackendApp.TelegramBots.HeadBot.Config.bot import bot

from BackendApp.Database.Models.reservation_status import ReservationStatus
from BackendApp.Database.Models.reservation_model import Reservation

from BackendApp.Middleware.bar_middleware import BarMiddleware
from BackendApp.Middleware.table_middleware import TableMiddleware
from BackendApp.Middleware.reservation_middleware import ReservationMiddleware
from BackendApp.Middleware.client_middleware import ClientMiddleware
from BackendApp.scheduler.core import Scheduler 

from datetime import datetime, timedelta
from telebot import types
import asyncio

ROVESNIK_MY_RESERVATIONS = "https://rovesnik-bot.online/rovesnik/my/reservations/"
SKREPKA_MY_RESERVATIONS = "https://rovesnik-bot.online/skrepka/my/reservations/"
DOROSHKA_MY_RESERVATIONS = "https://rovesnik-bot.online/doroshka/my/reservations/"

class ReservationChecker:
    
    def __init__(
            self, 
            checking_delay: int, 
            scheduler: Scheduler
        ):
        self.checking_delay = checking_delay
        self.scheduler = scheduler

    @staticmethod
    async def send_notification():
        reservations = await ReservationMiddleware.get_by_reserved_status()
        for reservation in reservations:
            now = datetime.now() + timedelta(hours=3)
            if (
                (reservation.reservation_start > now) and
                (reservation.reservation_start - now < timedelta(minutes=30))
            ):
                await ReservationMiddleware.update_entity(
                    reservation_id=reservation.id,
                    status=ReservationStatus.RESERVED_AND_NOTIFIED
                )
                table_entity = await TableMiddleware.get_by_uuid(table_uuid=reservation.table_uuid)
                bar_entity = await BarMiddleware.get_by_id(bar_id=table_entity.bar_id)

                bar_name = bar_entity.bar_name
                bar_id = bar_entity.bar_id

                if (bar_id == 1):
                    url = f"{ROVESNIK_MY_RESERVATIONS}?barId={bar_id}"
                elif (bar_id == 2):
                    url = f"{SKREPKA_MY_RESERVATIONS}?barId={bar_id}"
                elif (bar_id == 3):
                    url = f"{DOROSHKA_MY_RESERVATIONS}?barId={bar_id}"

                await bot.send_message(
                    chat_id=reservation.client_chat_id,
                    text=f"Ваша бронь в баре {bar_name} на столик {table_entity.table_id} уже начнется менее чем через 30 минут",
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
    
    @staticmethod
    async def change_status():
        reservations = await ReservationMiddleware.get_all_reserved_statuses()
        for reservation in reservations:
            now = datetime.now() + timedelta(hours=3)
            if ((reservation.reservation_start + timedelta(hours=2)) < now):
                await TableMiddleware.update(
                    table_uuid=reservation.table_uuid,
                    reserved=False
                )
                await ReservationMiddleware.update_entity(
                    reservation_id=reservation.id,
                    status=ReservationStatus.EXPIRED
                )
    
    @staticmethod
    async def change_client_reservation_status():
        clients = await ClientMiddleware.get_all_clients()
        for client in clients:
            if (not client.change_reservation):
                await ClientMiddleware.update_change_reservation(
                    chat_id=client.chat_id
                )
    
    @staticmethod
    async def change_client_reserve_table():
        clients = await ClientMiddleware.get_all_clients()
        for client in clients:
            if (not client.reserve_table):
                await ClientMiddleware.update_reserve_table(
                    chat_id=client.chat_id
                )
            

async def reservation_checking_thread():
    reservation_checker = ReservationChecker(
        checking_delay=1,
        scheduler=Scheduler(5)
    )

    reservation_checker.scheduler.create_job(
        ReservationChecker.send_notification,
        "every",
        "minutes",
        delay=1 
    )
    reservation_checker.scheduler.create_job(
        ReservationChecker.change_status,
        "every",
        "minutes",
        delay=1 
    )
    reservation_checker.scheduler.create_job(
        ReservationChecker.change_client_reservation_status,
        "at",
        None,
        time_str="21:00" # GMT +0 
    )
    reservation_checker.scheduler.create_job(
        ReservationChecker.change_client_reserve_table,
        "at",
        None,
        time_str="21:00" # GMT +0 
    )

    print(f"Delay is {reservation_checker.checking_delay} minutes")
    while True:
        now = datetime.now()
        timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
        print(f"{timestamp} - ReservationChecker envoked") 
        await reservation_checker.scheduler.pending()

if __name__ == "__main__":
    asyncio.run(reservation_checking_thread())
