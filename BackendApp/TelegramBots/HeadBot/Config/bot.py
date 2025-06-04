import os

from dotenv import load_dotenv
from telebot.async_telebot import AsyncTeleBot
from telebot.asyncio_storage import StateMemoryStorage

from BackendApp.TelegramBots.HeadBot.Middlewares.exception_middleware import (
    ExceptionHandler,
)

load_dotenv()


bot = AsyncTeleBot(
    str(os.getenv("HEAD_TELEGRAM_BOT_TOKEN")),
    # exception_handler=ExceptionHandler(),
    state_storage=StateMemoryStorage(),
)

provider_token = os.getenv("HEAD_BOT_PAYMENT_TOKEN")
