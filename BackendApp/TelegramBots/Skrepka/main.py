import asyncio
import os

from telebot.asyncio_filters import (
    ForwardFilter,
    IsDigitFilter,
    IsReplyFilter,
    StateFilter,
)

from BackendApp.Logger import logger
from BackendApp.scheduler.core import Scheduler
from BackendApp.TelegramBots.Skrepka.Config.bot import MyStates, bot
from BackendApp.TelegramBots.Skrepka.Handlers.inline_handler import (
    HandlerInlineMiddleware,
)
from BackendApp.TelegramBots.Skrepka.Handlers.start_handler import start_handler, home_handler
from BackendApp.TelegramBots.Skrepka.Middlewares.flooding_middleware import (
    FloodingMiddleware,
)
from BackendApp.TelegramBots.Skrepka.Middlewares.scheduler_middleware import (
    ScheduledTasks,
)
from BackendApp.TelegramBots.Skrepka.Handlers.support_handler import *

from BackendApp.TelegramBots.Skrepka.Filters.forward_filter import forward_filter
from BackendApp.TelegramBots.Skrepka.Filters.reply_filter import reply_filter

class Bot:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self) -> None:
        bot.add_custom_filter(IsReplyFilter())
        bot.add_custom_filter(ForwardFilter())
        bot.add_custom_filter(StateFilter(bot))
        bot.add_custom_filter(IsDigitFilter())

        bot.setup_middleware(FloodingMiddleware(1))

        self.provider_token: str = os.getenv("SKREPKA_PAYMENT_TOKEN")
        self.scheduler: Scheduler = Scheduler(pending_delay=1)
        self.scheduled_tasks: ScheduledTasks = ScheduledTasks(self.scheduler)

    @staticmethod
    async def polling():
        task1 = asyncio.create_task(bot.infinity_polling())
        await task1


b = Bot()


asyncio.run(b.polling())
