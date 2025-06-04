from BackendApp.TelegramBots.Rovesnik.Config import bot

from BackendApp.Database.Models.client_model import Client
from BackendApp.Database.Models.event_model import Event

from BackendApp.Middleware.client_middleware import ClientMiddleware
from BackendApp.Middleware.event_middleware import EventMiddleware
from BackendApp.Middleware.ticket_middleware import TicketMiddleware
from BackendApp.scheduler.core import Scheduler 

from BackendApp.IIKO.api.customer import Customer

from typing import List
from datetime import datetime
from dotenv import load_dotenv
import asyncio
import os 

load_dotenv()

API_LOGIN = os.getenv("API_LOGIN")

class BalanceChecker:
    
    def __init__(
            self, 
            checking_delay: int, 
            scheduler: Scheduler
        ):
        self.checking_delay = checking_delay
        self.scheduler = scheduler

    @staticmethod
    def check(balance):
        if (balance >= 10000):
            return True
        return False
    
    @staticmethod
    async def register_client_to_events(events: List[Event], client: Client):
        for event in events:
            await TicketMiddleware.purchase_ticket(
                event_id=event.id,
                client_chat_id=client.chat_id,
                friends=None
            )

    @staticmethod
    async def envoke():
        clients = await ClientMiddleware.get_all_clients()
        events = await EventMiddleware.get_upcoming_deposit_and_free_events_from_all_bars()
        client_iiko = await Customer.create(API_LOGIN, "Rovesnik")
        for client in clients:
            iiko_user = await client_iiko.get_customer_info(id=client.iiko_id)
            balance = iiko_user.walletBalances[0]["balance"]
            if (BalanceChecker.check(balance)):
                await BalanceChecker.register_client_to_events(
                    events=events, client=client
                )

        

async def balance_checking_thread():
    balance_checker = BalanceChecker(
        checking_delay=1,
        scheduler=Scheduler(5)
    )

    balance_checker.scheduler.create_job(
        BalanceChecker.envoke,
        "at",
        None,
        time_str="21:00" # GMT +0
    )
    while True:
        now = datetime.now()
        timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
        print(f"{timestamp} - BalanceChecker.envoke; delay is {balance_checker.checking_delay} minutes")
        await balance_checker.scheduler.pending()

if __name__ == "__main__":
    asyncio.run(balance_checking_thread())
