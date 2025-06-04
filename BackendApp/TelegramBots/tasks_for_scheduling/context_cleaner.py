from BackendApp.TelegramBots.HeadBot.Middlewares.message_context_middleware import message_context_manager as hmcm
from BackendApp.TelegramBots.Rovesnik.Middlewares.message_context_middleware import message_context_manager as rmcm
from BackendApp.TelegramBots.Skrepka.Middlewares.message_context_middleware import message_context_manager as smcm
from BackendApp.TelegramBots.Doroshka.Middlewares.message_context_middleware import message_context_manager as dmcm

from BackendApp.TelegramBots.HeadBot.Config.bot import bot as head_bot
from BackendApp.TelegramBots.Rovesnik.Config.bot import bot as rovesnik_bot
from BackendApp.TelegramBots.Skrepka.Config.bot import bot as skrepka_bot
from BackendApp.TelegramBots.Doroshka.Config.bot import bot as doroshka_bot

from BackendApp.scheduler.core import Scheduler 

from datetime import datetime, timedelta
import asyncio

ALLOWED_TIME = timedelta(days=1, hours=23, minutes=55)
TIME_INDEX = 1

class ContextCleaner:
    
    def __init__(
            self, 
            checking_delay: int, 
            scheduler: Scheduler
        ):
        self.checking_delay = checking_delay
        self.scheduler = scheduler
    
    @staticmethod
    async def clear():
        for chat_id in hmcm.help_menu_msgId_to_delete.keys():
            for msg_to_del in hmcm.help_menu_msgId_to_delete[chat_id]:
                now = datetime.now() + timedelta(hours=3)
                if (
                    now - msg_to_del[TIME_INDEX] > ALLOWED_TIME and
                    now > msg_to_del[TIME_INDEX]
                ):
                    await head_bot.delete_message(chat_id, msg_to_del[0])
                    index = hmcm.help_menu_msgId_to_delete[chat_id].index(msg_to_del)
                    del hmcm.help_menu_msgId_to_delete[chat_id][index]
        
        for chat_id in rmcm.help_menu_msgId_to_delete.keys():
            for msg_to_del in rmcm.help_menu_msgId_to_delete[chat_id]:
                now = datetime.now() + timedelta(hours=3)
                if (
                    now - msg_to_del[TIME_INDEX] > ALLOWED_TIME and
                    now > msg_to_del[TIME_INDEX]
                ):
                    await rovesnik_bot.delete_message(chat_id, msg_to_del[0])
                    index = rmcm.help_menu_msgId_to_delete[chat_id].index(msg_to_del)
                    del rmcm.help_menu_msgId_to_delete[chat_id][index]
        
        for chat_id in smcm.help_menu_msgId_to_delete.keys():
            for msg_to_del in smcm.help_menu_msgId_to_delete[chat_id]:
                now = datetime.now() + timedelta(hours=3)
                if (
                    now - msg_to_del[TIME_INDEX] > ALLOWED_TIME and
                    now > msg_to_del[TIME_INDEX]
                ):
                    await skrepka_bot.delete_message(chat_id, msg_to_del[0])
                    index = smcm.help_menu_msgId_to_delete[chat_id].index(msg_to_del)
                    del smcm.help_menu_msgId_to_delete[chat_id][index]
        
        for chat_id in dmcm.help_menu_msgId_to_delete.keys():
            for msg_to_del in dmcm.help_menu_msgId_to_delete[chat_id]:
                now = datetime.now() + timedelta(hours=3)
                if (
                    now - msg_to_del[TIME_INDEX] > ALLOWED_TIME and
                    now > msg_to_del[TIME_INDEX]
                ):
                    await doroshka_bot.delete_message(chat_id, msg_to_del[0])
                    index = dmcm.help_menu_msgId_to_delete[chat_id].index(msg_to_del)
                    del dmcm.help_menu_msgId_to_delete[chat_id][index]
            
async def context_cleaner_thread():
    context_cleaner = ContextCleaner(
        checking_delay=1,
        scheduler=Scheduler(5)
    )

    context_cleaner.scheduler.create_job(
        ContextCleaner.clear,
        "every",
        "minutes",
        delay=1 
    )
   
    print(f"Delay is {context_cleaner.checking_delay} minutes")
    while True:
        now = datetime.now()
        timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
        print(f"{timestamp} - ContextCleaner envoked") 
        await context_cleaner.scheduler.pending()

if __name__ == "__main__":
    asyncio.run(context_cleaner_thread())