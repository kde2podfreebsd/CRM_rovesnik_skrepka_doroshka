from BackendApp.scheduler.core import Scheduler 

from BackendApp.TelegramBots.tasks_for_scheduling.balance_checker import BalanceChecker
from BackendApp.TelegramBots.tasks_for_scheduling.reservation_checker import ReservationChecker
from BackendApp.TelegramBots.tasks_for_scheduling.notification_manager import NotificationManager
from BackendApp.TelegramBots.tasks_for_scheduling.table_manager import TableManager
from BackendApp.TelegramBots.tasks_for_scheduling.context_cleaner import ContextCleaner

from datetime import datetime, timedelta
import asyncio

class ShedulerCore:
    
    def __init__(
            self, 
            checking_delay: int, 
            scheduler: Scheduler
        ):
        self.checking_delay = checking_delay
        self.scheduler = scheduler
    
async def main_scheduler_thread():
    main_scheduler = ShedulerCore(
        checking_delay=1,
        scheduler=Scheduler(5)
    )
    # ----reservation_checker----
    main_scheduler.scheduler.create_job(
        ReservationChecker.send_notification,
        "every",
        "minutes",
        delay=1 
    )
    main_scheduler.scheduler.create_job(
        ReservationChecker.change_status,
        "every",
        "minutes",
        delay=1 
    )
    main_scheduler.scheduler.create_job(
        ReservationChecker.change_client_reservation_status,
        "at",
        None,
        time_str="21:00" # GMT +0 
    )
    main_scheduler.scheduler.create_job(
        ReservationChecker.change_client_reserve_table,
        "at",
        None,
        time_str="21:00" # GMT +0 
    )
    # --------------------------
    # ---notification_manager---
    main_scheduler.scheduler.create_job(
        NotificationManager.manage_tickets,
        "at",
        None,
        time_str="09:00" # GMT +0 
    )
    main_scheduler.scheduler.create_job(
        NotificationManager.manage_reservations,
        "at",
        None,
        time_str="09:00" # GMT +0
    )
    main_scheduler.scheduler.create_job(
        NotificationManager.manage_events,
        "every",
        "minutes",
        delay=1
    )
    main_scheduler.scheduler.create_job(
        NotificationManager.manage_shipping_query,
        "every",
        "minutes",
        delay=1
    )
    # --------------------------
    # ------balance_manager-----
    main_scheduler.scheduler.create_job(
        BalanceChecker.envoke,
        "at",
        None,
        time_str="21:00" # GMT +0
    )
    # --------------------------
    # -------table_manager------
    main_scheduler.scheduler.create_job(
        TableManager.manage_tables,
        "every",
        "minutes",
        delay=1
    )
    # --------------------------
    # ------context_cleaner-----
    main_scheduler.scheduler.create_job(
        ContextCleaner.clear,
        "every",
        "minutes",
        delay=1
    )
    # --------------------------
    print(f"Delay is {main_scheduler.checking_delay} minutes")
    while True:
        now = datetime.now() + timedelta(hours=3)
        timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
        print(f"{timestamp} - Main Scheduler has been envoked") 
        await main_scheduler.scheduler.pending()

if __name__ == "__main__":
    asyncio.run(main_scheduler_thread())
